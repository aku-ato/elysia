# Piano Dettagliato: Mapping Semantico Cross-Collection

## 📐 Architettura della Soluzione

### Fase 1: Estensione dello Schema Metadata
Aggiungere un nuovo campo `semantic_aliases` al metadata di ogni campo per indicare equivalenze semantiche tra collection.

**Schema Proposto**:
```python
field_metadata = {
    "name": "speaker_id",
    "type": "text",
    "description": "...",
    "groups": [...],
    "semantic_aliases": [
        {
            "collection": "SocialMediaPosts",
            "field": "author_id",
            "relationship": "equivalent"  # o "similar", "related"
        }
    ]
}
```

### Fase 2: Generazione Automatica degli Alias
Durante il preprocessing, usare un LLM per identificare campi semanticamente equivalenti tra collection.

**File**: `/Users/paolo/Projects/elysia/elysia/preprocessing/collection.py`

**Nuovo Componente**: `_identify_semantic_aliases()`
- Input: Tutte le collection analizzate + i loro field metadata
- Output: Mapping di equivalenze semantiche
- Logica: 
  - Confronta descriptions dei campi
  - Confronta nomi dei campi (fuzzy matching)
  - Chiede al LLM: "speaker_id in AudioTranscriptions è equivalente a author_id in SocialMediaPosts?"

### Fase 3: Enrichment dei Prompt LLM
Modificare i prompt delle query per includere informazioni sugli alias.

**File**: `/Users/paolo/Projects/elysia/elysia/tools/retrieval/prompt_templates.py`

**Modifica a `AggregationPrompt` e `QueryCreatorPrompt`**:
```python
# Aggiungere nuovo campo di input
semantic_mappings: dict = dspy.InputField(
    description="""
    Cross-collection field mappings showing semantically equivalent fields:
    {
        "AudioTranscriptions.speaker_id": ["SocialMediaPosts.author_id"],
        "SocialMediaPosts.author_id": ["AudioTranscriptions.speaker_id"]
    }
    When aggregating or querying across collections, use these mappings 
    to translate field names appropriately.
    """
)
```

**Aggiornamento docstring**:
```
When working with multiple collections, check the semantic_mappings field 
to understand which fields are equivalent across collections. 
For example, if asked to aggregate by "author" across AudioTranscriptions 
and SocialMediaPosts, use speaker_id for the first and author_id for the second.
```

### Fase 4: Runtime Translation
Implementare logica per tradurre i field names quando l'LLM genera query cross-collection.

**File**: `/Users/paolo/Projects/elysia/elysia/tools/retrieval/aggregate.py`

**Nuovo Metodo**: `_translate_field_names()`
```python
def _translate_field_names(
    self, 
    aggregation_outputs: list[AggregationOutput],
    semantic_mappings: dict
) -> list[AggregationOutput]:
    """
    Se l'LLM usa un field name errato per una collection,
    traduce automaticamente usando semantic_mappings.
    
    Esempio:
    - Query usa "author_id" su AudioTranscriptions
    - Mapping dice: AudioTranscriptions.author_id → AudioTranscriptions.speaker_id
    - Sostituisce automaticamente
    """
```

### Fase 5: Error Recovery con Feedback
Se una query fallisce per "field not found", usa il semantic mapping per retry automatico.

**File**: `/Users/paolo/Projects/elysia/elysia/tools/retrieval/util.py`

**Logica**:
```python
try:
    result = await execute_weaviate_aggregation(...)
except PropertyNotFoundError as e:
    # Estrai collection e field dall'errore
    # Cerca in semantic_mappings
    # Retry con field corretto
    if corrected_field := semantic_mappings.get(f"{collection}.{wrong_field}"):
        result = await execute_weaviate_aggregation(..., field=corrected_field)
```

---

## 🔧 Implementazione Passo-Passo

### Step 1: Schema Extension (1-2 ore)

**File da modificare**:
1. `/Users/paolo/Projects/elysia/elysia/preprocessing/collection.py`
   - Linea ~104-155: Aggiungere `out["semantic_aliases"] = []`
   - Estendere schema Weaviate per ELYSIA_METADATA__ se necessario

**Codice**:
```python
# In _evaluate_field_statistics()
out["semantic_aliases"] = []  # Inizialmente vuoto
```

### Step 2: Alias Generation Logic (3-4 ore)

**Nuovo File**: `/Users/paolo/Projects/elysia/elysia/preprocessing/semantic_mapping.py`

```python
class SemanticMappingPrompt(dspy.Signature):
    """
    Identify if two fields from different collections are semantically equivalent.
    """
    field1_name: str = dspy.InputField()
    field1_collection: str = dspy.InputField()
    field1_description: str = dspy.InputField()
    field1_sample_values: list[str] = dspy.InputField()
    
    field2_name: str = dspy.InputField()
    field2_collection: str = dspy.InputField()
    field2_description: str = dspy.InputField()
    field2_sample_values: list[str] = dspy.InputField()
    
    are_equivalent: bool = dspy.OutputField(
        desc="True if these fields represent the same semantic concept"
    )
    confidence: float = dspy.OutputField(
        desc="Confidence score 0.0-1.0"
    )
    reasoning: str = dspy.OutputField()

async def generate_semantic_mappings(
    collections_metadata: dict[str, dict],
    lm: dspy.LM
) -> dict[str, list[str]]:
    """
    Per ogni coppia di collection, confronta tutti i campi
    e identifica equivalenze semantiche.
    """
    mappings = {}
    
    for coll1_name, coll1_meta in collections_metadata.items():
        for field1 in coll1_meta["fields"]:
            key = f"{coll1_name}.{field1['name']}"
            mappings[key] = []
            
            for coll2_name, coll2_meta in collections_metadata.items():
                if coll1_name == coll2_name:
                    continue
                    
                for field2 in coll2_meta["fields"]:
                    # Quick filters
                    if field1["type"] != field2["type"]:
                        continue
                        
                    # LLM check
                    result = await check_semantic_equivalence(
                        field1, coll1_name,
                        field2, coll2_name,
                        lm
                    )
                    
                    if result.are_equivalent and result.confidence > 0.8:
                        mappings[key].append(f"{coll2_name}.{field2['name']}")
    
    return mappings
```

**Integrazione in preprocessing** (linea ~640-660):
```python
# Dopo aver processato tutte le collection
if len(processed_collections) > 1:
    semantic_mappings = await generate_semantic_mappings(
        processed_collections,
        lm
    )
    
    # Aggiorna i metadata di ogni collection
    for collection_name, mappings in semantic_mappings.items():
        coll, field = collection_name.split(".")
        # Update metadata con aliases
```

### Step 3: Prompt Enhancement (1 ora)

**File**: `/Users/paolo/Projects/elysia/elysia/tools/retrieval/prompt_templates.py`

**Linea ~114 (AggregationPrompt)**:
```python
semantic_field_mappings: dict = dspy.InputField(
    description="""
    Cross-collection semantic field equivalences. Format:
    {"Collection1.field_a": ["Collection2.field_b", "Collection3.field_c"]}
    
    IMPORTANT: When aggregating on a field that exists in one collection 
    but you need it from another, use the mapped equivalent field name.
    
    Example: If aggregating by "author" across collections and you see:
    {"AudioTranscriptions.speaker_id": ["SocialMediaPosts.author_id"]}
    Then use speaker_id for AudioTranscriptions, author_id for SocialMediaPosts.
    """,
    format=dict[str, list[str]]
)
```

**Linea ~97 (docstring update)**:
```python
The schema is provided in the `collection_schemas` field.
The semantic_field_mappings field shows equivalent fields across collections.
ALWAYS check semantic mappings when working with multiple collections to use 
the correct field name for each collection.
```

### Step 4: Query Generation Enhancement (2 ore)

**File**: `/Users/paolo/Projects/elysia/elysia/tools/retrieval/aggregate.py`

**Linea ~200+ (in __call__ method)**:
```python
# Get semantic mappings
semantic_mappings = tree_data.collection_data.get_semantic_mappings(
    collection_names
)

# Pass to LLM
aggregation_generator = ElysiaChainOfThought(
    aggregation_prompt,
    tree_data=tree_data,
    # ... other args ...
    semantic_field_mappings=semantic_mappings  # NUOVO
)
```

### Step 5: Error Recovery (2 ore)

**File**: `/Users/paolo/Projects/elysia/elysia/tools/retrieval/util.py`

**Nuovo wrapper attorno a execute_weaviate_aggregation**:
```python
async def execute_with_field_recovery(
    aggregation_output: AggregationOutput,
    collection: CollectionAsync,
    semantic_mappings: dict,
    logger: Logger
) -> dict:
    """
    Esegue aggregation con automatic field name recovery.
    """
    try:
        return await execute_weaviate_aggregation(
            aggregation_output,
            collection,
            logger
        )
    except Exception as e:
        if "Property" in str(e) and "not found" in str(e):
            # Parse error to get collection and field
            match = re.search(
                r"Property '(\w+)' not found in.*'(\w+)'",
                str(e)
            )
            if match:
                wrong_field, coll_name = match.groups()
                key = f"{coll_name}.{wrong_field}"
                
                # Check semantic mappings
                if key in semantic_mappings:
                    # Find the correct field for this collection
                    for mapping in semantic_mappings[key]:
                        if mapping.startswith(f"{coll_name}."):
                            correct_field = mapping.split(".")[1]
                            logger.warning(
                                f"Auto-correcting field {wrong_field} → "
                                f"{correct_field} for {coll_name}"
                            )
                            
                            # Modify aggregation_output
                            aggregation_output = replace_field_name(
                                aggregation_output,
                                wrong_field,
                                correct_field
                            )
                            
                            # Retry
                            return await execute_weaviate_aggregation(
                                aggregation_output,
                                collection,
                                logger
                            )
        
        # Re-raise if can't recover
        raise
```

---

## 🎯 Vantaggi della Soluzione

### Pro
1. ✅ **Automatico**: I mapping vengono identificati durante l'analisi
2. ✅ **Scalabile**: Funziona con N collection, non solo 2
3. ✅ **Intelligente**: Usa LLM per capire equivalenze semantiche
4. ✅ **Resiliente**: Error recovery automatico se LLM sbaglia
5. ✅ **Trasparente**: I nomi originali restano, nessun refactoring dati
6. ✅ **Estensibile**: Può supportare relazioni "similar" o "related", non solo "equivalent"

### Contro
1. ⚠️ **Complessità**: Richiede modifiche a 5+ file
2. ⚠️ **LLM Calls**: Aggiunge chiamate LLM durante preprocessing
3. ⚠️ **Latenza**: Ogni analisi diventa leggermente più lenta
4. ⚠️ **Maintenance**: Logica più complessa da debuggare

---

## 📊 Stima Effort

| Fase | Tempo | Complessità |
|------|-------|-------------|
| Schema Extension | 1-2h | Bassa |
| Alias Generation | 3-4h | Media |
| Prompt Enhancement | 1h | Bassa |
| Query Enhancement | 2h | Media |
| Error Recovery | 2h | Media-Alta |
| **Testing** | 3-4h | Alta |
| **Totale** | **12-15h** | **Media-Alta** |

---

## 🔄 Alternativa Ibrida (Raccomandazione)

### Approccio Pragmatico
**Breve termine** (5 min):
- Rinomina `speaker_id` → `author_id` nelle collection di test
- Testa correlazioni subito

**Lungo termine** (12-15h):
- Implementa semantic mapping per robustezza generale
- Beneficia sistema intero, non solo queste 2 collection
- Abilita casi d'uso futuri più complessi

### Quando Usare Semantic Mapping?
- ✅ Dataset reali con schemi inconsistenti
- ✅ Multiple source (API diverse, database legacy)
- ✅ Sistema production che riceve dati esterni
- ❌ Solo per test/demo con dati controllati

---

## 💡 Decisione Consigliata

Per il tuo caso specifico (test correlazione):
1. **Ora**: Rinomina campi (Soluzione 1) → 5 minuti
2. **Dopo validazione**: Se Elysia funziona bene, considera Semantic Mapping come feature generale

**Rationale**: Il semantic mapping è un'ottima feature per un sistema production, ma per testare le capacità di correlazione ora, il rename è più pratico.

---

Vuoi che proceda con:
- **A)** Implementazione completa Semantic Mapping (12-15h)
- **B)** Quick fix: rename speaker_id → author_id (5 min)
- **C)** Ibrido: rename ora + pianificare semantic mapping per dopo