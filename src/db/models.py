from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class RentListing(Base):
    __tablename__ = "rent_listings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    external_id: Mapped[str] = mapped_column(String(100), unique=True)
    
    source: Mapped[str] = mapped_column(String(50))
    
    price: Mapped[int] = mapped_column(Integer)
    price_per_m2: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    disposition: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    surface: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    district: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    furnishing: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    garage: Mapped[bool] = mapped_column(Boolean, default=False)
    balcony: Mapped[bool] = mapped_column(Boolean, default=False)
    loggia: Mapped[bool] = mapped_column(Boolean, default=False)
    mhd: Mapped[bool] = mapped_column(Boolean, default=False)
    
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    distance_to_center: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    distance_to_metro_km: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    nearest_metro: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    main_image: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    all_images: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

class SellListing(Base):
    __tablename__ = "sell_listings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    external_id: Mapped[str] = mapped_column(String(100), unique=True)
    
    source: Mapped[str] = mapped_column(String(50))
    
    price: Mapped[int] = mapped_column(Integer)
    price_per_m2: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    disposition: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    surface: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    district: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    furnishing: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    garage: Mapped[bool] = mapped_column(Boolean, default=False)
    balcony: Mapped[bool] = mapped_column(Boolean, default=False)
    loggia: Mapped[bool] = mapped_column(Boolean, default=False)
    mhd: Mapped[bool] = mapped_column(Boolean, default=False)
    
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    distance_to_center: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    distance_to_metro_km: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    nearest_metro: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    main_image: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    all_images: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    predicted_rent_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

