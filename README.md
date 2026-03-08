Prague Real Estate Analytics Platform
A full-stack web application that helps analyze the Prague rental market and evaluate apartments as investment opportunities.
What it does
You give it an apartment — it tells you how much rent it could realistically generate, and how many years it would take to pay for itself.
The platform has four main sections:

Marketplace — browse Prague apartments for sale with predicted rent and ROI (payback period) already calculated for each listing
Price Predictor — enter any apartment's details and get an instant rental price estimate from the ML model
Analytics — charts showing price distributions, average rent by layout, listing counts by district, and more
AI Chatbot — ask natural language questions like "cheap apartments near metro in Žižkov" or "best districts for families"

How it works under the hood
Data collection — four custom scrapers pull real listings from Bezrealitky (GraphQL API) and Sreality (REST API), for both rent and sale. A cron job runs monthly to keep the data fresh.
ML model — a Random Forest Regressor trained on rental listings predicts rent prices. Features include surface area, distance to city centre, distance to metro, district, layout, and furnishing. Achieves R² = 0.85 and ~11% average prediction error on real data.
RAG chatbot — rental listings are embedded with sentence-transformers and stored in ChromaDB. When you ask a question, Gemini classifies your intent, the app retrieves relevant listings via semantic search or SQL, and Gemini generates the final answer.
Payback calculation — for every sale listing, the model predicts what rent it could earn, then computes sale_price / (predicted_rent × 12) to get the years-to-payback figure shown in the marketplace.
Tech stack
FastAPI · SQLite + SQLAlchemy · scikit-learn · ChromaDB · Gemini API · sentence-transformers · Docker · Pandas · Pydantic · Jinja2
