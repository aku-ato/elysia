import weaviate

# Configura il client
client = weaviate.connect_to_local()

# Valore del conversation_id da cercare
conversation_id = "1a976440-82e5-4243-b4e5-60fe2a892c90"

# Step 1: Cerca l'oggetto con il conversation_id specificato
collection = client.collections.get("ELYSIA_TREES__")  # Sostituisci con il nome della tua classe

results = collection.query.fetch_objects(
    filters=weaviate.classes.query.Filter.by_property("conversation_id").equal(conversation_id),
    limit=1
)

# Step 2: Recupera l'ID dell'oggetto
if results.objects and len(results.objects) > 0:
    object_id = results.objects[0].uuid

    # Step 3: Elimina l'oggetto usando l'ID
    collection.data.delete_by_id(object_id)
    print(f"Oggetto con conversation_id {conversation_id} eliminato con successo.")
else:
    print(f"Nessun oggetto trovato con conversation_id {conversation_id}.")