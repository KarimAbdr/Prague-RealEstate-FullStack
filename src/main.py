from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.requests import Request
from src.api.endpoints.analytics import router as analytics_router
from src.api.endpoints.marketplace import router as marketplace_router
from src.api.endpoints.predictor import router as predictor_router
app = FastAPI()
app.include_router(analytics_router)
app.include_router(marketplace_router)
app.include_router(predictor_router)

templates = Jinja2Templates(directory="src/templates")

@app.get("/analytics-page", response_class=HTMLResponse)
async def analytics_page(request: Request):
    return templates.TemplateResponse("analytics.html", {"request": request})

@app.get("/marketplace-page", response_class=HTMLResponse)
async def marketplace_page(request: Request):
    return templates.TemplateResponse("marketplace.html", {"request": request})

@app.get("/predictor-page", response_class=HTMLResponse)
async def predictor_page(request: Request):
    return templates.TemplateResponse("predicting.html", {"request": request})