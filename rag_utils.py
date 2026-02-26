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
            # Create a rich document string for embedding
            doc_text = f"Material: {row['Material']}. Project: {row['Project Idea']}. Difficulty: {row['Difficulty']}. Time: {row['Time to Complete']}.\nInstructions:\n{row['Instructions']}"
            
            documents.append(doc_text)
            embeddings.append(self._get_embedding(doc_text))
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
        
        return f"Successfully ingested {len(documents)} projects from CSV."

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
            
        # Return simply the list of document contents match
        return results['documents'][0]

# Singleton instance for the app to use
_rag_instance = None

def get_rag_manager():
    global _rag_instance
    if _rag_instance is None:
         _rag_instance = RAGManager()
    return _rag_instance
