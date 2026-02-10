from pydantic import BaseModel, ConfigDict
from typing import Optional


class RentListingRead(BaseModel):
    id: int
    external_id: str
    source: str
    
    price: int
    price_per_m2: Optional[float] = None
    
    disposition: Optional[str] = None
    surface: Optional[int] = None
    district: Optional[str] = None
    
    furnishing: Optional[str] = None
    garage: bool = False
    balcony: bool = False
    loggia: bool = False
    mhd: bool = False
    
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    distance_to_center: Optional[float] = None
    distance_to_metro_km: Optional[float] = None
    nearest_metro: Optional[str] = None
    
    main_image: Optional[str] = None
    all_images: Optional[list] = None  
    
    model_config = ConfigDict(from_attributes=True)


class SellListingRead(BaseModel):
    id: int
    price: int
    
    disposition: Optional[str] = None
    surface: Optional[int] = None
    district: Optional[str] = None
    furnishing: Optional[str] = None
    
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    distance_to_center: Optional[float] = None
    distance_to_metro_km: Optional[float] = None
    nearest_metro: Optional[str] = None
    
    main_image: Optional[str] = None
    all_images: Optional[list] = None
    
    predicted_rent_price: Optional[float] = None
    
    years_to_payback: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True)

class RentPredictionRequest(BaseModel):
    surface: int
    distance_to_center: float
    distance_to_metro_km: float
    garage: bool = False
    mhd: bool = False
    balcony: bool = False
    loggia: bool = False
    disposition: Optional[str] = None
    furnishing: Optional[str] = None
    district: Optional[str] = None