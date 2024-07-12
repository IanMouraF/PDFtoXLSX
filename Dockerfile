# Use uma imagem base com suporte ao Python
FROM python:3.11-slim

# Instale dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Crie um ambiente virtual
RUN python -m venv --copies /opt/venv

# Ative o ambiente virtual
ENV PATH="/opt/venv/bin:$PATH"

# Copie os arquivos da aplicação
COPY . /app

# Defina o diretório de trabalho
WORKDIR /app

# Instale as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Comando para rodar a aplicação
CMD ["flask", "run", "--host=0.0.0.0"]
