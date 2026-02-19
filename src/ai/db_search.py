import math
from sqlalchemy import func
from src.db import get_session, RentListing, SellListing
from collections import defaultdict


class DBSearch:

    def search_rent(self, district=None, max_price=None,
                    disposition=None, limit=5) -> list[dict]:
        session = get_session()
        try:
            q = session.query(RentListing)
            q = q.filter(RentListing.price > 2000)        
            if district:
                q = q.filter(RentListing.district.ilike(f"%{district}%"))
            if disposition:
                q = q.filter(RentListing.disposition.ilike(f"%{disposition}%"))
            if max_price:
                q = q.filter(RentListing.price <= max_price)
            results = q.order_by(RentListing.price.asc()).limit(limit).all()
            return [self._r(item) for item in results]
        finally:
            session.close()

    def search_sell(self, district=None, max_price=None,
                    disposition=None, limit=5) -> list[dict]:
        session = get_session()
        try:
            q = session.query(SellListing)
            q = q.filter(SellListing.price > 50000)        
            if district:
                q = q.filter(SellListing.district.ilike(f"%{district}%"))
            if max_price:
                q = q.filter(SellListing.price <= max_price)
            if disposition:
                q = q.filter(SellListing.disposition.ilike(f"%{disposition}%"))
            result = q.order_by(SellListing.price.asc()).limit(limit).all()
            return [self._s(item) for item in result]       
        finally:
            session.close()

    def _r(self, l: RentListing) -> dict:
        return {
            "type": "rent",
            "disposition": l.disposition or "N/A",
            "district": l.district or "Prague",
            "price": l.price,
            "surface": l.surface,
            "metro": l.nearest_metro,
            "dist_metro": l.distance_to_metro_km,
            "dist_center": l.distance_to_center,
            "furnishing": l.furnishing,
            "balcony": l.balcony,
            "lat": l.latitude,
            "lon": l.longitude,
        }

    def _s(self, l: SellListing) -> dict:
        payback_years = None
        if l.price and l.predicted_rent_price:
            payback_years = round(l.price / (l.predicted_rent_price * 12), 1)
        return {
            "type": "sell",
            "disposition": l.disposition or "N/A",
            "district": l.district or "Prague",
            "price": l.price or 0,
            "surface": l.surface,
            "metro": l.nearest_metro,
            "dist_metro": l.distance_to_metro_km,
            "dist_center": l.distance_to_center,
            "furnishing": l.furnishing,
            "balcony": l.balcony,
            "lat": l.latitude,
            "lon": l.longitude,
            "payback_years": payback_years,
        }

    def get_market_stats(self) -> dict:
        session = get_session()
        try:
            r = session.query(
                func.avg(RentListing.price).label("avg_rent_price"),
                func.min(RentListing.price).label("min_rent"),
                func.max(RentListing.price).label("max_rent"),
                func.count(RentListing.price).label("count_rent")
            ).filter(RentListing.price > 2000).first()

            s = session.query(
                func.avg(SellListing.price).label("avg_sell_price"),
                func.min(SellListing.price).label("min_sell"),
                func.max(SellListing.price).label("max_sell"),
                func.count(SellListing.price).label("count_sell")
            ).filter(SellListing.price > 500000).first()

            return {
                "rent": {
                    "avg": int(r.avg_rent_price or 0),
                    "min": int(r.min_rent or 0),
                    "max": int(r.max_rent or 0),
                    "count": r.count_rent
                },
                "sell": {
                    "avg": int(s.avg_sell_price or 0),
                    "min": int(s.min_sell or 0),
                    "max": int(s.max_sell or 0),
                    "count": s.count_sell
                }
            }
        finally:
            session.close()

    def get_student_districts(self) -> str:
        session = get_session()
        try:
            result = session.query(
                RentListing.district,
                func.avg(RentListing.price).label("avg_price"),
                func.count(RentListing.id).label("count")
            ).filter(
                RentListing.price > 2000,
                RentListing.price < 15000          
            ).group_by(
                RentListing.district
            ).order_by(
                func.avg(RentListing.price).asc()
            ).limit(5).all()

            lines = ["TOP DISTRICTS FOR STUDENTS (cheapest avg rent):"]
            for i, r in enumerate(result, 1):
                lines.append(f"{i}. {r.district}: {int(r.avg_price):,} CZK avg (sample: {r.count})")
            return "\n".join(lines)
        finally:
            session.close()

    def get_family_districts(self) -> str:
        session = get_session()
        try:
            result = session.query(
                RentListing.district,
                func.avg(RentListing.price).label("avg_price"),
                func.count(RentListing.id).label("count")
            ).filter(
                RentListing.price > 2000,
                RentListing.disposition.in_(["3+kk", "3+1", "4+kk", "4+1"]),
                RentListing.balcony == True
            ).group_by(
                RentListing.district
            ).order_by(
                func.count(RentListing.id).desc()
            ).limit(5).all()

            lines = ["TOP DISTRICTS FOR FAMILIES (3+ rooms with balcony):"]
            for i, r in enumerate(result, 1):
                lines.append(f"{i}. {r.district}: {int(r.avg_price):,} CZK avg (sample: {r.count})")
            return "\n".join(lines)
        finally:
            session.close()

    def get_investment_districts(self) -> str:
        session = get_session()
        try:
            result = session.query(
                SellListing.district,
                func.avg(SellListing.price).label("avg_price"),        
                func.count(SellListing.id).label("count")
            ).filter(
                SellListing.price > 500000
            ).group_by(
                SellListing.district
            ).order_by(
                func.avg(SellListing.price).asc()
            ).limit(8).all()

            lines = ["TOP INVESTMENT DISTRICTS (lowest avg price):"]
            for i, r in enumerate(result, 1):
                lines.append(f"{i}. {r.district}: {int(r.avg_price):,} CZK avg (sample: {r.count})")
            return "\n".join(lines)
        finally:
            session.close()

    def get_districts_stats(self) -> str:
        session = get_session()
        try:
            result = session.query(
                RentListing.district,
                func.avg(RentListing.price).label("avg_price"),
                func.count(RentListing.id).label("count")
            ).filter(
                RentListing.price > 2000
            ).group_by(
                RentListing.district
            ).order_by(
                func.avg(RentListing.price).asc()
            ).limit(10).all()

            lines = ["DISTRICT OVERVIEW (avg rent):"]
            for r in result:
                lines.append(f"• {r.district}: {int(r.avg_price):,} CZK (sample: {r.count})")
            return "\n".join(lines)
        finally:
            session.close()

    def compare_districts(self, d1: str, d2: str) -> str:
        session = get_session()
        try:
            def get_stats(district):
                return session.query(
                    func.avg(RentListing.price).label("avg"),
                    func.min(RentListing.price).label("min"),
                    func.max(RentListing.price).label("max"),
                    func.count(RentListing.id).label("count")
                ).filter(
                    RentListing.price > 2000,
                    RentListing.district.ilike(f"%{district}%")
                ).first()

            r1 = get_stats(d1)
            r2 = get_stats(d2)

            return f"""DISTRICT COMPARISON:

{d1}:
  avg: {int(r1.avg or 0):,} CZK
  min: {int(r1.min or 0):,} CZK
  max: {int(r1.max or 0):,} CZK
  listings: {r1.count}

{d2}:
  avg: {int(r2.avg or 0):,} CZK
  min: {int(r2.min or 0):,} CZK
  max: {int(r2.max or 0):,} CZK
  listings: {r2.count}"""
        finally:
            session.close()

    def geo_analysis(self, lat: float, lon: float) -> str:
        return (
            f"Geo search near ({lat}, {lon}) is not implemented yet. "
            f"Try searching by district name instead."
        )