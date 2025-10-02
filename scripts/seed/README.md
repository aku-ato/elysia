# Elysia Cross-Collection Correlation Seed Scripts

Scripts per popolare Elysia con collection di esempio multilingua per testare le capacità di correlazione cross-collection.

## 📦 Contenuto

```
/Users/paolo/Projects/elysia/scripts/seed/
├── Makefile                              # Comandi orchestrazione
├── requirements.txt                      # Dipendenze Python
├── .env.example                          # Template configurazione
├── .env                                  # Configurazione locale (git-ignored)
├── seed_correlation_collections.py      # Script popolazione dati
├── cleanup_collections.py                # Script rimozione collection
├── CORRELATION_QUERIES.md                # Esempi query correlazione
└── README.md                             # Questa documentazione
```

## 🚀 Quick Start

### 1. Setup Iniziale

```bash
cd /Users/paolo/Projects/elysia/scripts/seed

# Crea virtualenv e installa dipendenze
make setup

# Copia e configura .env
cp .env.example .env
nano .env  # Configura BACKEND_URL se necessario
```

### 2. Popola le Collection

```bash
# Testa connessione backend
make test-connection

# Popola collection di esempio
make seed
```

### 3. Usa le Collection

- Apri frontend Elysia: http://localhost:3000
- Analizza le collection create
- Testa query cross-collection (vedi [CORRELATION_QUERIES.md](CORRELATION_QUERIES.md))

### 4. Cleanup (Opzionale)

```bash
# Rimuovi collection di test
make cleanup

# Rimuovi virtualenv
make clean
```

## 📊 Collection Create

### SocialMediaPosts

**Descrizione**: Tweet multilingua da conferenza tech

**Campi**:
- `post_id` (text) - ID univoco post
- `content` (text) - Contenuto tweet
- `language` (text) - Lingua (ar/en/it)
- `timestamp` (date) - Data/ora pubblicazione
- `author_id` (text) - ID autore
- `topic` (text) - Argomento
- `sentiment` (text) - Sentimento (positive/neutral/negative)
- `hashtags` (text[]) - Array hashtag
- `event_id` (text) - ID evento (chiave correlazione)
- `location` (text) - Località

**Record**: 13 post (4 arabi, 4 inglesi, 5 italiani)

### AudioTranscriptions

**Descrizione**: Trascrizioni audio multilingua da sessioni conferenza

**Campi**:
- `transcription_id` (text) - ID univoco trascrizione
- `transcript` (text) - Testo trascritto
- `language` (text) - Lingua (ar/en/it)
- `duration_seconds` (int) - Durata audio
- `timestamp` (date) - Data/ora registrazione
- `speaker_id` (text) - ID speaker (correlato ad author_id)
- `topic` (text) - Tema discusso
- `audio_quality` (text) - Qualità audio
- `keywords` (text[]) - Parole chiave
- `event_id` (text) - ID evento (chiave correlazione)
- `session_type` (text) - Tipo sessione (keynote/panel/workshop)

**Record**: 10 trascrizioni (3 arabe, 4 inglesi, 3 italiane)

## 🔗 Chiavi di Correlazione

Le collection sono correlabili tramite:

1. **event_id** - Stesso evento (`tech_conf_2025`)
2. **author_id / speaker_id** - Stessa persona
3. **topic** - Argomenti correlati
4. **timestamp** - Analisi temporale
5. **language** - Analisi multilingua

## 🔍 Esempi di Query

Vedi [CORRELATION_QUERIES.md](CORRELATION_QUERIES.md) per esempi dettagliati:

- Query cross-collection per evento
- Tracciamento persona su piattaforme
- Analisi sentiment multilingua
- Correlazione temporale eventi-reazioni social
- Pattern di partecipazione

## 🛠️ Comandi Makefile

```bash
make help              # Mostra aiuto
make setup             # Setup virtualenv
make test-connection   # Testa backend API
make seed              # Popola collection
make cleanup           # Rimuovi collection
make clean             # Rimuovi virtualenv
```

## 📝 Configurazione

### Variabili .env

```bash
BACKEND_URL=http://localhost:8000   # URL backend Elysia
USER_ID=default                      # User ID per API calls
```

### Requisiti

- Python 3.8+
- Backend Elysia running su `http://localhost:8000`
- OpenAI API key configurata nel backend (per vectorizzazione)

## ✅ Test Workflow Completo

1. **Setup**: `make setup` ✓
2. **Test connessione**: `make test-connection` ✓
3. **Seed**: `make seed` ✓
   - Collection create: 2/2 ✓
   - Record inseriti: 23/23 ✓
4. **Query**: Vedi frontend Elysia
5. **Cleanup**: `make cleanup` (quando finito)

## 🎯 Obiettivi di Test

Con queste collection puoi testare:

- ✅ Query su collection multiple simultanee
- ✅ Correlazione via campi comuni
- ✅ Ricerca semantica multilingua
- ✅ Aggregazioni cross-collection
- ✅ Filtri temporali complessi
- ✅ Tracciamento entità (persone, topic)

## 📚 Risorse

- Documentazione Elysia: https://docs.elysia.ai
- API Backend: http://localhost:8000/docs
- Frontend: http://localhost:3000

## 🐛 Troubleshooting

**Errore: Backend non raggiungibile**
```bash
# Verifica che il backend sia running
docker-compose ps

# Verifica URL in .env
cat .env | grep BACKEND_URL
```

**Errore: Collection già esistono**
```bash
# Rimuovi collection esistenti
make cleanup
```

**Errore: Dipendenze Python**
```bash
# Reinstalla virtualenv
make clean
make setup
```

---

**Creato per**: Test correlazione cross-collection Elysia
**Lingue supportate**: Arabo (ar), Inglese (en), Italiano (it)
**Evento**: Tech Conference 2025
