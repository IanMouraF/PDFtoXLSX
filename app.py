from flask import Flask, render_template, request, send_file
import os
import fitz  # PyMuPDF
import pandas as pd

app = Flask(__name__)

def extract_table_data_from_text_v2(pdf_text):
    lines = pdf_text.split('\n')
    data = []
    current_product_code = None
    current_product_description = None
    for line in lines:
        if 'Produto:' in line:
            # Extract product code and description
            parts = line.split('Descrição:')
            current_product_code = parts[0].split('Produto: ')[1].strip()
            description_with_unit = parts[1].strip()
            # Remove unwanted text from description
            if 'Unidade:' in description_with_unit:
                current_product_description = description_with_unit.split('Unidade:')[0].strip()
            else:
                current_product_description = description_with_unit.split('Valores Expressos em R$(REAL)')[0].strip()
        elif '|' in line and len(line.split('|')) == 11:
            # Extract table row by splitting with '|'
            row = [item.strip() for item in line.split('|')]
            # Remove the trailing text from description
            if 'UN Valores Expressos em R$(REAL)' in row[2]:
                row[2] = row[2].replace('UN Valores Expressos em R$(REAL)', '')
            # Add product code and description to the row
            data.append([current_product_code, current_product_description] + row)
    return data




def pdf_to_excel_v2(pdf_path, output_excel_path):
    # Open the PDF and extract text
    pdf_document = fitz.open(pdf_path)
    pdf_text = ''
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        pdf_text += page.get_text()
    pdf_document.close()

    # Extract table data
    table_data = extract_table_data_from_text_v2(pdf_text)

    # Define the columns
    columns = ["Código do Produto", "Descrição do Produto", "Data", "Nota Fiscal", "CFOP", "Quantidade", "Preço Unitário", "Valor", "% LBC", "Quantidade em Estoque", "Preço Médio", "Valor em Estoque", "OBS"]
    df = pd.DataFrame(table_data, columns=columns)

    # Save the DataFrame to Excel
    df.to_excel(output_excel_path, index=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if request.method == 'POST':
        # Receber o arquivo PDF do formulário
        pdf_file = request.files['pdf_file']

        # Verificar se foi enviado um arquivo
        if pdf_file.filename == '':
            return render_template('index.html', message='Nenhum arquivo selecionado.')

        # Caminho para salvar o arquivo Excel de saída
        output_excel_filename = f'{os.path.splitext(pdf_file.filename)[0]}_converted.xlsx'
        output_excel_path = os.path.join(app.config['UPLOAD_FOLDER'], output_excel_filename)

        # Salvar o arquivo PDF temporariamente
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_file.filename)
        pdf_file.save(pdf_path)

        # Converter PDF para Excel
        try:
            pdf_to_excel_v2(pdf_path, output_excel_path)
        finally:
            # Remover o arquivo PDF temporário (após garantir que esteja fechado)
            if os.path.exists(pdf_path):
                os.remove(pdf_path)

        # Retornar o caminho do arquivo Excel para download
        return send_file(output_excel_path, as_attachment=True, download_name=output_excel_filename)


if __name__ == '__main__':
    app.config['UPLOAD_FOLDER'] = 'uploads'
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
