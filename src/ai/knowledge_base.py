import os
import chromadb
from google import genai
from src.db import get_session, RentListing
from sentence_transformers import SentenceTransformer

class KnowledgeBase:
    def __init__(self):
        self.chroma_client = chromadb.HttpClient(host="localhost", port=8001)
        self.colection = self.chroma_client.get_or_create_collection(name="prague_listings", metadata={"hnsw:space": "cosine"})
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
   
    #this method will encode only text IN OUR DB objects, it will be nedeed in build() 
    def _embed_batch(self, texts: list[str]) -> list[list[float]]:
        result = self.encoder.encode(texts) 
        return result.tolist()

    #this one will encode users input, it will convers users input in one vector and it will be compared with all our objects from db
    def _embed_query(self, text: str) -> list[float]:
       result = self.encoder.encode([text])
       return result[0].tolist()
    
    def _to_text(self, l: RentListing) -> str:
        parts = []

        parts.append(f"{l.disposition or 'apartment'} in {l.district or 'Prague'}")
        parts.append(f"{l.price:,} CZK per month")
        parts.append(f"{l.surface}m²")

        if l.distance_to_metro_km:
            km = l.distance_to_metro_km
            if km < 0.3:
                parts.append(f"steps from {l.nearest_metro} metro")
            elif km < 0.7:
                parts.append(f"walking distance to {l.nearest_metro} metro")
            else:
                parts.append(f"{km}km to {l.nearest_metro} metro")

        if l.distance_to_center:
            d = l.distance_to_center
            if d < 2:
                parts.append("city center location")
            elif d < 5:
                parts.append("close to city center")
            else:
                parts.append("suburban quiet area")

        if l.furnishing == "furnished":
            parts.append("fully furnished move-in ready")
        elif l.furnishing == "partly_furnished":
            parts.append("partially furnished")
        elif l.furnishing == "not_furnished":
            parts.append("unfurnished empty")

        if l.balcony:
            parts.append("has balcony")
        if l.garage:
            parts.append("has parking garage")

        if l.price:
            if l.price < 13000:
                parts.append("budget affordable student")
            elif l.price > 35000:
                parts.append("luxury premium")

        return ", ".join(parts) + "."

    def _meta(self, l: RentListing) -> dict:
        return {
            "price": l.price or 0,
            "district": l.district or "Prague",
            "disposition": l.disposition or "Apartment",
            "surface": l.surface or 0, 
            "distance_to_metro_km": l.distance_to_metro_km or 0 
        }

    def build(self):
        session = get_session()
        try:
            listings=session.query(RentListing).all()

            existing=set(self.colection.get()["ids"])

            new = [l for l in listings if f"r_{l.id}" not in existing]
            
            if not new:
                print("Smth wrong, I got empty list")
            else:
               bathc_size=32
               for i in range(0, len(new), bathc_size):
                   batch=new[i:i+bathc_size]

                   text = [self._to_text(b) for b in batch]

                   embeddings = self._embed_batch(text)

                   self.colection.add(
                       documents=text,
                       embeddings=embeddings, 
                       metadatas=[self._meta(l) for l in batch],
                       ids=[f"r_{l.id}" for l in batch]
                   )
                   done = min(i + bathc_size, len(new))
                   print(f"{done}/{len(new)}")
        finally:
            session.close()

    def search(self, query: str, n: int = 5) -> list[dict]:
        vec = self._embed_query(query)
        result = self.colection.query(
            query_embeddings=[vec] ,
            n_results=n)
        return[
            {"text": doc, "meta": meta , "distance":dist }
            for doc , meta, dist in zip(
                result["documents"][0],
                result["metadatas"][0],
                result["distances"][0]
            )
        ]
