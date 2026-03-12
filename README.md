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
🏠 Marketplace Overview
This page displays apartments currently available for sale, integrated with an AI-driven financial analysis tool. For each listing, the platform provides:
-Estimated Rent: Predicted monthly rental income based on market data.
-ROI (Return on Investment): A calculated payback period showing how many years it will take for the property to pay for itself through rental yields.

<img width="1461" height="838" alt="Screenshot 2026-03-12 at 20 48 07" src="https://github.com/user-attachments/assets/69232bda-3cbb-4e36-94b6-c7c772b46b99" />

---
🎯 Rental Price Predictor
This interactive tool allows users to estimate the rental value of any apartment by inputting specific parameters such as surface area, layout, and location.
-Custom Inputs: Users can toggle features like garage, balcony, or proximity to transit to see how they impact market value.
-High Accuracy: The underlying Machine Learning model is trained on real-market data, achieving an R2 score of 0.85, ensuring reliable and data-driven estimates.

<img width="1466" height="843" alt="Screenshot 2026-03-12 at 20 46 16" src="https://github.com/user-attachments/assets/68182b1c-2a2a-47ea-bb05-1cfdd0fd4c4d" />

---

📊 Market Analytics Dashboard
The dashboard provides a high-level overview of the Prague real estate market through interactive data visualizations. It helps users identify trends and make informed investment decisions.
-Market Trends: Visualize rent and sale price distributions across different districts.
-Inventory Analysis: Track the volume of listings by disposition (e.g., 1+kk, 3+1) and geographic location.
Comparative Stats: Compare average rental yields and prices to identify undervalued areas or high-demand layouts.

<img width="1469" height="837" alt="Screenshot 2026-03-12 at 20 45 33" src="https://github.com/user-attachments/assets/409274b5-dea2-43f6-9b95-33e029ccb8a2" />

---
💬 Prague Real Estate AI Assistant
The platform features an intelligent chatbot that acts as a personal real estate consultant. Unlike a simple search bar, it understands context and provides data-backed advice.
-Natural Language Queries: Ask complex questions 
-RAG-Powered Accuracy: The bot uses Retrieval-Augmented Generation to query the live database of listings and market statistics before generating an answer, ensuring it doesn't "hallucinate" prices.
-Smart Recommendations: It can compare different districts (e.g., Žižkov vs. Holešovice) and suggest which areas currently offer the best investment potential based on the latest scraped data.

<img width="1459" height="843" alt="Screenshot 2026-03-12 at 20 45 14" src="https://github.com/user-attachments/assets/352a9677-3898-40bf-9bef-888330dbd449" />
