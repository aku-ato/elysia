# Dockerfile per Elysia Backend
FROM python:3.12-slim

# Imposta la directory di lavoro
WORKDIR /app

# Installa dipendenze di sistema necessarie per spaCy, tiktoken e altre librerie
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia i file di configurazione per le dipendenze
COPY pyproject.toml MANIFEST.in README.md ./

# Copia il codice sorgente (necessario per pip install -e .)
COPY elysia/ ./elysia/

# Installa le dipendenze Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e . && \
    pip install --no-cache-dir debugpy

# Scarica il modello spaCy (necessario per l'elaborazione del testo)
RUN python -m spacy download en_core_web_sm

# Copia lo script di avvio per il debug
COPY start_debug.sh /app/start_debug.sh
RUN chmod +x /app/start_debug.sh

# Esponi le porte dell'applicazione
EXPOSE 8000
# Porta per il debugger (debugpy)
EXPOSE 5678

# Comando per avviare l'applicazione
# Usa lo script di debug che supporta sia modalità normale che debug
CMD ["/app/start_debug.sh"]
