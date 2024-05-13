# Use a imagem base do Ubuntu 24.04
FROM ubuntu:24.04

# Atualize o gerenciador de pacotes e instale o Python 3 e o pip
RUN apt-get update && apt-get install -y && apt-get upgrade -y && apt dist-upgrade -y python3 python3-venv python3-pip

# Crie e defina o diretório de trabalho
WORKDIR /app

# Copie o arquivo requirements.txt para o contêiner
COPY requirements.txt .

# Crie um ambiente virtual Python
RUN python3 -m venv xml

# Ative o ambiente virtual e instale as dependências usando pip
RUN /bin/bash -c "source xml/bin/activate && pip install --no-cache-dir -r requirements.txt"

# Comando padrão para ser executado quando o contêiner for iniciado
CMD [ "python3", "app.py" ]
