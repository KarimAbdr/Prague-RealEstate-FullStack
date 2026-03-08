# Prague Real Estate Analytics Platform

A full-stack web application that helps analyze the Prague rental market and evaluate apartments as investment opportunities.

---

## What it does

> You give it an apartment — it tells you how much rent it could realistically generate, and how many years it would take to pay for itself.

| Section | Description |
|---|---|
| 🏢 Marketplace | Browse Prague apartments for sale with predicted rent and ROI already calculated |
| 🎯 Price Predictor | Enter any apartment's details and get an instant rental price estimate |
| 📊 Analytics | Charts showing price distributions, average rent by layout, listings by district |
| 🤖 AI Chatbot | Ask natural language questions like "cheap apartments near metro in Žižkov" |

---

## How it works

**Data collection**
Four custom scrapers pull real listings from Bezrealitky (GraphQL) and Sreality (REST API), for both rent and sale. A cron job refreshes the data monthly.

**ML model**
A Random Forest Regressor trained on rental listings predicts rent prices.
Features: surface area, distance to city centre, distance to metro, district, layout, furnishing.
- R² = **0.85**
- Average prediction error: **~11%**

**RAG chatbot**
Listings are embedded with `sentence-transformers` and stored in ChromaDB. Gemini classifies your intent → the app retrieves listings via semantic search or SQL → Gemini generates the answer.

**Payback calculation**
`sale_price / (predicted_rent × 12)` — computed automatically for every sale listing in the marketplace.

---

## Tech stack

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)
![Python](https://img.shields.io/badge/Python_3.12-3776AB?style=flat&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat&logo=scikit-learn&logoColor=white)

`FastAPI` `SQLite + SQLAlchemy` `scikit-learn` `ChromaDB` `Gemini API` `sentence-transformers` `Docker` `Pandas` `Pydantic` `Jinja2`

---

## Running locally
```bash
docker compose up --build
# → http://localhost:8000
```

First-time setup (inside the container):
```bash
python -m src.parsers.data_cleaning   # scrape & save listings
python -m src.services.predicting     # predict rent for sale listings
python -m src.ai.build_kb             # build ChromaDB knowledge base
```

---

## Project context

Built as a portfolio project during Informatics studies at Czech University of Life Sciences (CULS), Prague. The ML pipeline originated in a bachelor thesis on Prague rental price prediction.
