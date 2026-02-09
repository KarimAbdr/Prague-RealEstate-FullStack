from fastapi import APIRouter
from src.schemas.listing import RentPredictionRequest
from src.services.predictor import Predictor
from pydantic import BaseModel

predictor = Predictor()
router = APIRouter(prefix="/api/predictor", tags=["Predictor"])

class RentPredictionResponse(BaseModel):
    predicted_rent_price: float

@router.post("/predict", response_model=RentPredictionResponse)
def predict_rent_price(request: RentPredictionRequest):
    data = request.model_dump()
    result = predictor.predict(data)
    return {"predicted_rent_price": result}