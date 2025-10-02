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
    pip install --no-cache-dir -e .

# Scarica il modello spaCy (necessario per l'elaborazione del testo)
RUN python -m spacy download en_core_web_sm

# Esponi la porta dell'applicazione
EXPOSE 8000

# Comando per avviare l'applicazione
# Usa uvicorn direttamente per maggiore controllo
CMD ["uvicorn", "elysia.api.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
