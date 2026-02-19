import os
import json
import re
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

from src.ai.db_search import DBSearch
from src.ai.knowledge_base import KnowledgeBase


class RealEstateChatbot:
    SYSTEM = """You are a Prague real estate expert assistant."""

    INTENT_PROMPT = """Classify this real estate query. Return ONLY valid JSON."""



    def __init__(self):
        self.db = DBSearch()
        self.kb = KnowledgeBase()
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY") ) 
        self.history = []
    
    def _get_intent(self, message: str) -> dict:
       try:
           response = self.client.models.generate_content(
               model="gemini-2.5-flash",
               contents=self.INTENT_PROMPT.format(query=message)
           )
           text = re.sub(r"```(?:json)?", "", response.text).strip()
           return json.loads(text)
       except Exception as e:
           print(f"Intent error:{e}")
   
    def _fmt_rent(self, listings: list) -> str:
        if not listings:
            return "No listings found"
        
        # Step 3 — build lines
        lines = ["RENT LISTINGS:"]
        for l in listings:
            line = f"• {l['disposition']}, {l['district']}, {l['surface']}m², {l['price']:,} CZK"
            lines.append(line)
        return "\n".join(lines)
    def _fmt_sell(self, listings: list) -> str:
        if not listings:
            return "No listings found"
        lines = ["SALE LISTINGS:"]
        for l in listings:
            line = f"• {l['disposition']}, {l['district']}, {l['surface']}m², {l['price']:,} CZK"
            if l.get('payback_years'):
                line += f", payback {l['payback_years']} yrs"
            lines.append(line)
        return "\n".join(lines)
    
    def _fmt_semantic(self, results: list) -> str:
            return "LISTINGS:\n" + "\n".join(f"• {r['text']}" for r in results)
      
    def _retrieve(self, intent: dict, query: str) -> str:
        t = intent.get("type", "general")

        if t == "rent":
            semantic = self.kb.search(query, n=5)
            max_price = intent.get("max_price")
            if max_price and semantic:
                semantic = [r for r in semantic if r["meta"].get("price", 0) <= max_price]
            if not semantic:
                listings = self.db.search_rent(
                    district=intent.get("district"),
                    max_price=intent.get("max_price"),
                    disposition=intent.get("disposition")
                )
                return self._fmt_rent(listings)
            return self._fmt_semantic(semantic)

        elif t == "sell":
            result = self.db.search_sell(
                district=intent.get("district"),
                max_price=intent.get("max_price"),
                disposition=intent.get("disposition")
            )
            listings = []
            for group in result.values():
                listings.extend(group)
                
            return self._fmt_sell(listings)

        elif t == "student":
            sql = self.db.get_student_districts()
            semantic = self.kb.search("cheap student apartment near metro", n=4)
            return self._merge(str(sql), semantic)

        elif t == "investment":
            sql = self.db.get_investment_districts()
            return str(sql)

        elif t == "family":
            sql = self.db.get_family_districts()
            semantic = self.kb.search("family apartment quiet area balcony", n=4)
            return self._merge(str(sql), semantic)

        elif t == "stats":
            return str(self.db.get_market_stats())

        elif t == "districts":
            return str(self.db.get_districts_stats())

        elif t == "compare":
            d1 = intent.get("district", "")
            d2 = intent.get("district2", "")
            return str(self.db.compare_districts(d1, d2))

        elif t == "geo":
            lat = intent.get("lat")
            lon = intent.get("lon")
            if lat and lon:
                return str(self.db.geo_analysis(lat, lon))
            return "Please provide location coordinates."

        else:  
            semantic = self.kb.search(query, n=5)
            return self._fmt_semantic(semantic)

    
    def _merge(self, sql_data: str, semantic: list) -> str:
        parts = [sql_data]
        if semantic:
            parts.append("\nEXAMPLE LISTINGS:")
            for r in semantic[:4]:
                parts.append(f"• {r['text']}") 
        return "\n".join(parts)

    def ask(self, user_message: str) -> str:
        intent = self._get_intent(user_message)

        data = self._retrieve(intent, user_message)

        if data:
            prompt = f"{user_message}\n\n---\n{data}\n---"
        else:
            prompt = user_message

        self.history.append(
            types.Content(role="user", parts=[types.Part(text=prompt)])
        )

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=self.history,
            config=types.GenerateContentConfig(
                system_instruction=self.SYSTEM
            )
        )
        answer = response.text

        self.history.append(
            types.Content(role="model", parts=[types.Part(text=answer)])
        )

        if len(self.history) > 20:
            self.history = self.history[-20:]

        return answer

    def reset(self):
       self.history = []
    

    
