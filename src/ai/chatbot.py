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
    """
    Главный класс — соединяет все части вместе.
    
    Поток запроса:
        ask(message)
            → _get_intent()     # Gemini классифицирует запрос
            → _retrieve()       # достаём данные из нужного источника
            → generate_content() # Gemini генерирует ответ с данными
    
    Связи:
        - DBSearch: точные агрегаты (avg, min, payback)
        - KnowledgeBase: семантический поиск
        - Google Gemini API: intent detection + генерация ответа
    
    Документация Gemini: ai.google.dev/gemini-api/docs/text-generation
    """

    SYSTEM = """You are a Prague real estate expert assistant.

RULES:
- Use ONLY data provided between --- markers. Never invent prices.
- Always cite specific numbers from the data.
- For "best districts": give top 3 with brief reasoning.
- For investment: always show payback period.
- Reply in the SAME language as the user.
- If no data: say you don't have this info.
- Max 200 words."""

    INTENT_PROMPT = """Classify this real estate query. Return ONLY valid JSON.

Query: "{query}"

{{
  "type": "<rent|sell|student|investment|family|compare|geo|stats|districts|general>",
  "district": "<Praha 8 or null>",
  "district2": "<Praha 1 or null>",
  "max_price": <20000 or null>,
  "disposition": "<2+kk or null>",
  "lat": <50.08 or null>,
  "lon": <14.43 or null>,
  "radius_km": <1.5 or null>
}}"""

    def __init__(self):
        # TODO: создай экземпляры DBSearch и KnowledgeBase
        self.db = ...
        self.kb = ...

        # TODO: создай Google Gemini клиент
        # Подсказка: genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.client = ...

        # История разговора — список типов Content
        # Зачем: Gemini не помнит предыдущие сообщения,
        # мы сами передаём всю историю каждый раз
        self.history = []

    def ask(self, user_message: str) -> str:
        """
        Главный метод — обрабатывает сообщение пользователя.
        
        Алгоритм RAG:
            1. _get_intent() → понять что хочет юзер
            2. _retrieve()   → достать нужные данные
            3. Собрать промпт: вопрос + данные
            4. generate_content() → получить ответ
            5. Сохранить в историю
            6. Вернуть ответ
        
        TODO: реализуй алгоритм
        
        Подсказка для сборки промпта:
            if data:
                prompt = f"{user_message}\\n\\n---\\n{data}\\n---"
            else:
                prompt = user_message
        
        Подсказка для добавления в историю:
            self.history.append(
                types.Content(
                    role="user",
                    parts=[types.Part(text=prompt)]
                )
            )
        
        Подсказка для вызова Gemini:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=self.history,
                config=types.GenerateContentConfig(
                    system_instruction=self.SYSTEM
                )
            )
            answer = response.text
        
        Подсказка для ограничения истории:
            if len(self.history) > 20:
                self.history = self.history[-20:]
            # Зачем: каждый токен стоит денег и замедляет ответ
        """
        ...

    def reset(self):
        """
        Очищает историю разговора.
        
        TODO: одна строка
        """
        ...

    def _get_intent(self, message: str) -> dict:
        """
        Использует Gemini чтобы классифицировать запрос.
        
        Возвращает словарь с типом и параметрами:
            {"type": "student", "district": null, "max_price": null}
        
        Почему отдельный вызов к Gemini, а не if/else?
        LLM лучше понимает естественный язык чем regex.
        "Kde koupit byt v Praze?" → type: "sell", понял чешский!
        
        TODO: реализуй метод
        
        Подсказка — вызов:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=self.INTENT_PROMPT.format(query=message)
            )
        
        Подсказка — парсинг JSON:
            text = re.sub(r"```(?:json)?", "", response.text).strip()
            return json.loads(text)
            # re.sub убирает markdown ```json ... ``` если Gemini добавил
        
        Подсказка — обработка ошибок:
            try:
                ...
            except Exception as e:
                print(f"Intent error: {e}")
                return {"type": "general"}  # fallback
        """
        ...

    def _retrieve(self, intent: dict, query: str) -> str:
        """
        Маршрутизатор данных — решает какой источник использовать.
        
        Это СЕРДЦЕ RAG системы.
        
        Маппинг типов на источники:
            "stats"      → db.get_market_stats()
            "districts"  → db.get_districts_stats()
            "student"    → db.get_student_districts() + kb.search()
            "investment" → db.get_investment_districts()
            "family"     → db.get_family_districts() + kb.search()
            "compare"    → db.compare_districts(d1, d2)
            "geo"        → db.geo_analysis(lat, lon)
            "rent"       → kb.search() с fallback на db.search_rent()
            "sell"       → db.search_sell()
            "general"    → kb.search()
        
        TODO: реализуй через if/elif цепочку
        
        Подсказка для rent — сначала ChromaDB, потом SQL fallback:
            semantic = self.kb.search(query, n=6)
            max_price = intent.get("max_price")
            if max_price and semantic:
                semantic = [r for r in semantic
                            if r["meta"].get("price", 0) <= max_price]
            if not semantic:
                # ChromaDB ничего не нашла → SQL
                listings = self.db.search_rent(...)
                return self._fmt_rent(listings)
            return self._fmt_semantic(semantic)
        
        Подсказка для student (комбинирование):
            sql = self.db.get_student_districts()
            semantic = self.kb.search("cheap student near metro", n=4)
            return self._merge(sql, semantic)
        """
        ...

    def _merge(self, sql_data: str, semantic: list) -> str:
        """
        Объединяет SQL данные и семантические результаты.
        
        SQL даёт агрегаты (топ районы).
        Semantic даёт конкретные примеры квартир.
        Вместе — полный контекст для LLM.
        
        TODO: реализуй
        
        Подсказка:
            parts = [sql_data]
            if semantic:
                parts.append("\\nEXAMPLE LISTINGS:")
                for r in semantic[:4]:
                    parts.append(f"• {r['text']}")
            return "\\n".join(parts)
        """
        ...

    def _fmt_rent(self, listings: list) -> str:
        """
        Форматирует список квартир из SQL в строку для промпта.
        
        TODO: реализуй форматирование
        
        Пример результата:
            "RENT LISTINGS:
             • 2+kk, Praha 8, 55m², 18,000 CZK, 0.4km to metro
             • 1+kk, Praha 9, 35m², 14,500 CZK, 0.2km to metro"
        """
        ...

    def _fmt_sell(self, listings: list) -> str:
        """
        Форматирует квартиры на продажу — добавляет payback period.
        
        TODO: реализуй по аналогии с _fmt_rent
        
        Пример: "• 2+kk, Praha 5, 60m², 4,500,000 CZK, payback 18.5 yrs"
        """
        ...

    def _fmt_semantic(self, results: list) -> str:
        """
        Форматирует результаты ChromaDB в строку.
        
        TODO: одна строка
        
        Подсказка:
            return "LISTINGS:\\n" + "\\n".join(f"• {r['text']}" for r in results)
        """
        ...