from pydantic import BaseModel, ConfigDict
from typing import Optional


class RentListingRead(BaseModel):
    """
    Pydantic schema for API responses (NOT for database!)
    Uses simple Python types: int, str, float, bool
    """
    # Basic info
    id: int
    external_id: str
    source: str
    
    # Price
    price: int
    price_per_m2: Optional[float] = None
    
    # Apartment details
    disposition: Optional[str] = None
    surface: Optional[int] = None
    district: Optional[str] = None
    
    # Features
    furnishing: Optional[str] = None
    garage: bool = False
    balcony: bool = False
    loggia: bool = False
    mhd: bool = False
    
    # Location
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    distance_to_center: Optional[float] = None
    distance_to_metro_km: Optional[float] = None
    nearest_metro: Optional[str] = None
    
    # Images (will be populated by endpoint)
    main_image: Optional[str] = None
    all_images: Optional[list] = None  # List of URLs (parsed from JSON string)
    
    # Config to work with SQLAlchemy objects
    model_config = ConfigDict(from_attributes=True)


class SellListingRead(BaseModel):
    """
    Pydantic schema for API responses
    Only includes fields that are actually returned by the endpoint
    """
    # Basic info
    id: int
    price: int
    
    # Apartment details
    disposition: Optional[str] = None
    surface: Optional[int] = None
    district: Optional[str] = None
    furnishing: Optional[str] = None
    
    # Location
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    distance_to_center: Optional[float] = None
    distance_to_metro_km: Optional[float] = None
    nearest_metro: Optional[str] = None
    
    # Images
    main_image: Optional[str] = None
    all_images: Optional[list] = None
    
    # ML prediction
    predicted_rent_price: Optional[float] = None
    
    # ROI (calculated)
    years_to_payback: Optional[float] = None
    
    # Config
    model_config = ConfigDict(from_attributes=True)