import math
from sqlalchemy import func
from src.db import get_session, RentListing, SellListing
from collections import defaultdict
from sqlalchemy import func

class DBSearch:  
    #docs.sqlalchemy.org → ORM → Querying Guide    
    #filter=WHERE in sql
    #ilike case sensitive 
    def search_rent(self, district=None, max_price=None,
                    disposition=None, limit=5) -> list[dict]:
        session = get_session()
        try:
            q = session.query(RentListing)
            if district:
                q = q.filter(RentListing.district.ilike(f"%{district}%"))
            if disposition:
                q = q.filter(RentListing.disposition.ilike(f"%{disposition}%"))
            if max_price:
                q = q.filter(RentListing.price <= max_price)

            grouped_result = defaultdict(list)
            results = q.order_by(RentListing.price.asc()).limit(limit).all() #wont let kill server 
            for item in results:
                data = self._r(item)
                key = item.disposition 
                grouped_result[key].append(data)

            return dict(grouped_result)
        finally:
            session.close()


    def search_sell(self, district=None, max_price=None, min_price=500000,
                    disposition=None, limit=5) -> list[dict]:
        session = get_session()
        try:
                q = session.query(SellListing)
                if district:
                    q=q.filter(SellListing.district.ilike(f"%{district}%"))
                if max_price:
                    q=q.filter(SellListing.price <= max_price)
                    q=q.filter( SellListing.price >= min_price)
                if disposition:  
                    q=q.filter(SellListing.disposition.ilike(f"%{disposition}%"))

                grouped_result = defaultdict(list)  
                result = q.order_by(SellListing.price.asc()).limit(limit).all()
                
                for item in result:
                    data =self._s(item)
                    key = item.disposition
                    grouped_result[key].append(data)
                
                return dict(grouped_result) 
        finally:
                session.close()  

    def _r(self, l:RentListing) -> dict:
        return{
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
    def _s(self , l:SellListing) -> dict:
        payback_years=None
        if l.price and l.predicted_rent_price:
            payback_years = round(l.price/(l.predicted_rent_price*12),1)

        return{
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
            "payback_yers": payback_years
        }      
       


    def get_investment_districts(self) -> dict:
        session = get_session()
        try:
            result = session.query(SellListing.disposition, 
            SellListing.district, 
            func.avg(SellListing.price).label('avg_price'),
            func.count(SellListing.id).label('total_count')).group_by(
            SellListing.disposition, SellListing.district).all()

            stats = defaultdict(dict)
            for item in result:
                stats[item.district][item.disposition] = {
                    "avg_price": round(item.avg_price, 2),
                    "sample_size": item.total_count
            }
            return dict(stats)
        finally:
            session.close()


    def get_market_stats(self) -> dict:
        session = get_session()
        try:
            r = session.query(
                func.avg(RentListing.price).label("avg_rent_price"),
                func.min(RentListing.price).label("min_rent"),
                func.max(RentListing.price).label("max_rent"),
                func.count(RentListing.price).label("count_rent")
            ).first()
            s = session.query(
                func.avg(SellListing.price).label("avg_sell_price"),
                func.min(SellListing.price).label("min_sell"),
                func.max(SellListing.price).label("max_sell"),
                func.count(SellListing.price).label("count_sell")
            ).filter(SellListing.price >= 500_000).first()
            return {
                "rent": {"avg": int(r.avg_rent_price or 0), 
                         "min": int(r.min_rent or 0),
                         "max": int(r.max_rent or 0),
                         "count": r.count_rent},
                "sell": {"avg": int(s.avg_sell_price or 0), 
                         "min": int(s.min_sell or 0),
                         "max": int(s.max_sell or 0),
                         "count": s.count_sell}
            }
        finally:
            session.close()