from dotenv import load_dotenv
load_dotenv()

from src.ai.knowledge_base import KnowledgeBase

if __name__ == "__main__":
    print("🔨 Building ChromaDB...")
    kb = KnowledgeBase()
    kb.build()
    print("✅ Done!")