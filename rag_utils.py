import os
import chromadb
from sentence_transformers import SentenceTransformer
import pandas as pd
import PyPDF2

# Use a local directory for the database
DB_PATH = "./chroma_db"
COLLECTION_NAME = "upcycle_knowledge"

class RAGManager:
    def __init__(self):
        # Initialize ChromaDB client pointing to local storage
        self.chroma_client = chromadb.PersistentClient(path=DB_PATH)
        
        # Load the local embedding model (runs completely offline/locally)
        # all-MiniLM-L6-v2 is fast and good for general text
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Get or create the collection
        self.collection = self.chroma_client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"} # Use cosine similarity
        )
        
    def _get_embedding(self, text):
        # Generate embedding vector for the text
        return self.encoder.encode(text).tolist()

    def ingest_csv(self, csv_path):
        """Ingests the synthetic dataset we generated."""
        df = pd.read_csv(csv_path)
        
        # Check if already ingested to avoid duplicates. 
        # A simple check: if collection count >= row count, assume it's loaded.
        if self.collection.count() >= len(df):
            return f"Database already contains {self.collection.count()} items. Skipping CSV ingestion."

        documents = []
        embeddings = []
        metadatas = []
        ids = []

        for index, row in df.iterrows():
            # Create the rich document string we actually want to RETURN
            doc_text = f"Material: {row['Material']}. Project: {row['Project Idea']}. Difficulty: {row['Difficulty']}. Time: {row['Time to Complete']}.\nInstructions:\n{row['Instructions']}"
            documents.append(doc_text)
            
            # **CRITICAL OPTIMIZATION**: Instead of embedding the full instructional text,
            # we embed the specific visual descriptors the vision model will likely output.
            # This ensures a much tighter mathematical match during RAG query search.
            vision_target = row.get('Vision Description Target', row['Material'])
            embeddings.append(self._get_embedding(str(vision_target)))
            
            metadatas.append({
                "source": "csv_seed",
                "material": row['Material'],
                "difficulty": row['Difficulty']
            })
            ids.append(f"csv_{row['ID']}")

        # Add to Chroma
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        return f"Successfully ingested {len(documents)} optimized projects from CSV."

    def extract_text_from_pdf(self, pdf_file):
        """Extracts text from a PyPDF2 supported file object."""
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text

    def ingest_document(self, file_name, file_bytes, is_pdf=False):
        """Ingests a single text or PDF file, chunking it into smaller pieces."""
        import io
        
        if is_pdf:
            pdf_file = io.BytesIO(file_bytes)
            text = self.extract_text_from_pdf(pdf_file)
        else:
            text = file_bytes.decode('utf-8')

        # Simple chunking (e.g., split by paragraphs or fixed length)
        # Here we do a basic fixed-length chunking with overlap
        chunk_size = 500
        overlap = 50
        chunks = []
        
        for i in range(0, len(text), chunk_size - overlap):
            chunk = text[i:i + chunk_size]
            if len(chunk.strip()) > 10: # Ignore tiny empty chunks
                chunks.append(chunk)

        if not chunks:
            return "No text could be extracted."

        documents = []
        embeddings = []
        metadatas = []
        ids = []

        # Use a timestamp-based ID prefix for uniqueness
        import time
        prefix = int(time.time())

        for idx, chunk in enumerate(chunks):
            documents.append(chunk)
            embeddings.append(self._get_embedding(chunk))
            metadatas.append({"source": file_name})
            ids.append(f"doc_{prefix}_{idx}")

        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        return f"Successfully ingested document '{file_name}' into {len(chunks)} chunks."

    def query(self, query_text, n_results=3):
        """Searches the vector DB for the most relevant context."""
        query_embedding = self._get_embedding(query_text)
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        # Results is a dictionary containing ids, distances, metadatas, documents
        if not results['documents'] or not results['documents'][0]:
            return []
            
        filtered_docs = []
        for i, doc in enumerate(results['documents'][0]):
            distance = results['distances'][0][i]
            # Only include snippets that are reasonably relevant (distance < 0.6)
            if distance <= 0.6:
                filtered_docs.append(doc)
                
        return filtered_docs

    def find_exact_match(self, vision_description, threshold=0.15):
        """Searches for a visually identical previous scan."""
        query_embedding = self._get_embedding(vision_description)
        
        # We query for 1 result
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=1,
            # We filter specifically for generated feedback to avoid returning raw instructional CSV rows as a full cache hit
            where={"source": "llm_generated"}
        )
        
        if not results['documents'] or not results['documents'][0]:
            return None
            
        distance = results['distances'][0][0]
        print(f"DEBUG: Cache Hit Check - Best Match Distance: {distance:.4f} (Threshold: {threshold})")
        
        # In Chroma with cosine similarity, lower distance means higher similarity.
        # A distance of 0.0 is a perfect match.
        if distance <= threshold:
            print(f"DEBUG: Cache hit successful! Distance {distance:.4f} is <= {threshold}")
            return results['documents'][0][0] # Return the cached text
            
        print("DEBUG: Cache hit failed. Distance too high.")
        return None

    def add_generated_idea(self, vision_description, generated_text):
        """Saves a good generated idea back into the database."""
        # We embed the *vision description* so we can easily find it later based on similar images
        embedding = self._get_embedding(vision_description)
        
        import time
        prefix = int(time.time())
        doc_id = f"gen_{prefix}"
        
        self.collection.add(
            documents=[generated_text], # The text we RETURN is the generated instructions
            embeddings=[embedding],     # But the EMBEDDING is based on the description
            metadatas=[{"source": "llm_generated", "description": vision_description}],
            ids=[doc_id]
        )
        
        return doc_id

    def ingest_sqlite_history(self, db_path="upcycle.db"):
        """Reads past scans from upcycle.db and indexes them into ChromaDB."""
        import sqlite3
        if not os.path.exists(db_path):
            return "SQLite DB not found."
            
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        try:
            # Table schema from database.py: id, image_path, item_name, api_response, timestamp
            c.execute('SELECT id, item_name, api_response FROM recipes')
            rows = c.fetchall()
        except sqlite3.OperationalError:
            conn.close()
            return "Invalid DB schema or table not found."
            
        conn.close()
        
        if not rows:
            return "No history found in the database to sync."
            
        documents = []
        embeddings = []
        metadatas = []
        ids = []
        
        count = 0
        for row in rows:
            row_id, item_name, api_response = row
            doc_id = f"sqlite_{row_id}"
            
            # Check if this ID is already synced
            existing = self.collection.get(ids=[doc_id])
            if existing and existing['ids']:
                continue # Skip already synced items
                
            # If the item_name isn't great, at least we have the response text
            description = item_name if item_name and item_name != "Scanned Item" else "Historical Scan"
            
            # Embed the description / summary of what it is
            embedding = self._get_embedding(description)
            
            documents.append(api_response)
            embeddings.append(embedding)
            metadatas.append({"source": "sqlite_sync", "description": description})
            ids.append(doc_id)
            count += 1
            
        if count == 0:
            return "All history items have already been synced."
            
        # Batch insert
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        return f"Successfully synced {count} past scans from history."

# Singleton instance for the app to use
_rag_instance = None

def get_rag_manager():
    global _rag_instance
    if _rag_instance is None:
         _rag_instance = RAGManager()
    return _rag_instance
