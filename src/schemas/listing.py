from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer

class BaseListing(BaseModel):
    id: Mapped[int] = mapped_column(Integer , primary_key=True)
    external_id: str
    source: str
    price: int
    price_per_m2: float | None = None
    disposition: str | None = None
    surface: int | None = None
    district: str | None = None

    furnishing: str | None = None
    garage: bool = False
    balcony: bool = False
    loggia: bool = False
    mhd: bool = False

    latitude: float | None = None
    longitude: float | None = None
    distance_to_center: float | None = None
    distance_to_metro_km: float | None = None
    nearest_metro: str | None = None

    main_image: str | None = None
    all_images: str | None = None

    class Config:
        from_attributes = True  

    

class RentListing(BaseListing):
    __tablename__ = "rent_listings"

class SellListingRead(BaseListing):
    __tablename__ = "sell_listings"
    predicted_rent_price: float | None = None