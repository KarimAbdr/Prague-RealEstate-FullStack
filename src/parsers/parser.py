import requests
import pandas as pd
from requests.exceptions import RequestException
def parsing_bezreality_rent_data():
    url = 'https://api.bezrealitky.cz/graphql/'

    headers = {
        "accept": "*/*",
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    all_data = []
    limit = 15
    offset = 0

    while True:
        data = {
    "query": """
    query AdvertList($locale: Locale!, $estateType: [EstateType], $offerType: [OfferType], $regionOsmIds: [ID], $limit: Int, $offset: Int, $order: ResultOrder , $disposition: [Disposition]) {
        listAdverts(
            locale: $locale,
            estateType: $estateType,
            offerType: $offerType,
            regionOsmIds: $regionOsmIds,
            limit: $limit,
            offset: $offset,
            order: $order, 
            disposition: $disposition,
           
            
        ) {
            list {
                id
                price
                currency
                estateType
                offerType
                address(locale: $locale)
                tags(locale: $locale)
                imageAltText(locale: $locale)
                dataJson
                surface
                garage
                disposition
                gps {
                    lat
                    lng
                }  
                mainImage {
                    url(filter: RECORD_THUMB)
                }
                publicImages(limit: 5) {
                    url(filter: RECORD_MAIN)
                    } 
           }    
            totalCount
        }
    }
    """,
    "variables": {
        "locale": "CS",
        "estateType": ["BYT"],
        "offerType": ["PRONAJEM"],
        "regionOsmIds": ["R435514"],
        "limit": limit,
        "offset": offset,
        "order": "TIMEORDER_DESC"
    }

        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            response_json = response.json()

            adverts = response_json['data']['listAdverts']['list']
            if not adverts:
                break

            for ad in adverts:
                tags = ad.get("tags", [])
                if 'Vybaveno' in tags: # Furnished
                    furnishing = 'furnished'
                elif 'Částečně vybaveno' in tags: # Partially furnished
                    furnishing = 'partially_furnished'
                elif 'Nevybaveno' in tags: # Unfurnished
                    furnishing = 'unfurnished'
                else:
                    furnishing = 'unknown'
                mhd = any('MHD' in tag for tag in tags)
                balcony=any('Balkón' in tag for tag in tags)
                loggia=any('Lodžie' in tag for tag in tags)
                gps = ad.get("gps", {})
                latitude = gps.get("lat")
                longitude = gps.get("lng")

                main_image_data = ad.get("mainImage")
                main_image_url = main_image_data.get("url") if main_image_data else None

                public_images_data = ad.get("publicImages", [])
                all_images_urls = [img.get("url") for img in public_images_data if img.get("url")]

                if not main_image_url and all_images_urls:
                 main_image_url = all_images_urls[0]

                all_data.append({
                    "id": ad.get("id"),
                    "price": ad.get("price"),
                    "address": ad.get("address"),
                    "offerType": ad.get("offerType"),
                    "disposition": ad.get("disposition"),
                    "surface": ad.get("surface"),
                    "garage": ad.get("garage"),
                    "tags": tags,
                    "furnishing": furnishing,
                    "mhd": mhd,
                    "balcony": balcony,
                    "loggia": loggia,   
                    "latitude": latitude,
                    "longitude": longitude,
                    "imageAltText": ad.get("imageAltText"),
                    "main_image": main_image_url,
                    "all_images": all_images_urls,
                })

            offset += limit

        except RequestException as e:
            print(f"Error: {e}")
            break

    df = pd.DataFrame(all_data)


    print("Total records received:", len(df))
    return df

def parse_sreality_rent_data(pages=5):
    url = "https://www.sreality.cz/api/cs/v2/estates"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    all_data = []
    per_page = 100  
    for page in range(pages):
        params = {
            "category_main_cb": 1,      
            "category_type_cb": 2,     
            "per_page": per_page,
            "locality_region_id": 10,
            "page": page
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  
            data = response.json()

            estates = data['_embedded']['estates']

            for estate in estates:
                labels_all = estate.get("labelsAll", [])
                tech_labels = labels_all[0] if len(labels_all) > 0 else []
                infra_labels = labels_all[1] if len(labels_all) > 1 else []
                images_links = estate.get("_links", {}).get("images", [])
                image_urls = [img.get("href") for img in images_links if img.get("href")]
                main_image = image_urls[0] if image_urls else "https://via.placeholder.com/400x300?text=No+Photo"

               
                if 'furnished' in tech_labels:
                    furnishing = 'furnished'
                elif 'partly_furnished' in tech_labels:
                    furnishing = 'partly_furnished'
                elif 'not_furnished' in tech_labels:
                    furnishing = 'not_furnished'
                else:
                    furnishing = None

                mhd_tag={'bus_public_transport', 'tram', 'metro' , 'train'}
                mhd=any(tag in infra_labels for tag in mhd_tag)
                garage=any('garage' in tech_labels for infa in tech_labels)
                loggia=any('loggia' in tech_labels for infa in tech_labels)
                balcony=any('balcony' in tech_labels for infa in tech_labels)
                gps=estate.get("gps" , {})
                latitude=gps.get("lat") 
                longitude= gps.get("lon") 
                all_data.append({
                    "id":estate.get("hash_id"),
                    "locality": estate.get("locality"),
                    "price": estate.get("price"),
                    "name": estate.get("name"),
                    "city_raw": estate.get("seo", {}).get("locality"),
                    "labels_all": labels_all,
                    "furnishing": furnishing,
                    "mhd": mhd,
                    "garage": garage,
                    "loggia": loggia,
                    "balcony": balcony,
                    "gps": gps,
                    "latitude": latitude,
                    "longitude": longitude,
                    "main_image": main_image,       # Ссылка на главное фото
                    "all_images": image_urls,
                })

        except requests.exceptions.RequestException as e:
            print(f"Error while fetching page {page + 1}: {e}")
            break

    df = pd.DataFrame(all_data)
    print("✅ Total listings fetched:", len(df))
    return df

def parsing_bezrealitky_sell_data():
    url = 'https://api.bezrealitky.cz/graphql/'

    headers = {
        "accept": "*/*",
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    all_data = []
    limit = 15
    offset = 0

    while True:
        data = {
    "query": """
    query AdvertList($locale: Locale!, $estateType: [EstateType], $offerType: [OfferType], $regionOsmIds: [ID], $limit: Int, $offset: Int, $order: ResultOrder , $disposition: [Disposition]) {
        listAdverts(
            locale: $locale,
            estateType: $estateType,
            offerType: $offerType,
            regionOsmIds: $regionOsmIds,
            limit: $limit,
            offset: $offset,
            order: $order, 
            disposition: $disposition,
           
            
        ) {
            list {
                id
                price
                currency
                estateType
                offerType
                address(locale: $locale)
                tags(locale: $locale)
                imageAltText(locale: $locale)
                dataJson
                surface
                garage
                disposition
                gps {
                    lat
                    lng
                }  
                mainImage {
                    url(filter: RECORD_THUMB)
                }
                publicImages(limit: 5) {
                    url(filter: RECORD_MAIN)
                    } 
           }    
            totalCount
        }
    }
    """,
    "variables": {
        "locale": "CS",
        "estateType": ["BYT"],
        "offerType": ["PRODEJ"],
        "regionOsmIds": ["R435514"],
        "limit": limit,
        "offset": offset,
        "order": "TIMEORDER_DESC"
    }

        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            response_json = response.json()

            adverts = response_json['data']['listAdverts']['list']
            if not adverts:
                break

            for ad in adverts:
                tags = ad.get("tags", [])
                if 'Vybaveno' in tags: # Furnished
                    furnishing = 'furnished'
                elif 'Částečně vybaveno' in tags: # Partially furnished
                    furnishing = 'partially_furnished'
                elif 'Nevybaveno' in tags: # Unfurnished
                    furnishing = 'unfurnished'
                else:
                    furnishing = 'unknown'
                mhd = any('MHD' in tag for tag in tags)
                balcony=any('Balkón' in tag for tag in tags)
                loggia=any('Lodžie' in tag for tag in tags)
                gps = ad.get("gps", {})
                latitude = gps.get("lat")
                longitude = gps.get("lng")

                main_image_data = ad.get("mainImage")
                main_image_url = main_image_data.get("url") if main_image_data else None

                public_images_data = ad.get("publicImages", [])
                all_images_urls = [img.get("url") for img in public_images_data if img.get("url")]

                if not main_image_url and all_images_urls:
                 main_image_url = all_images_urls[0]

                all_data.append({
                    "id": ad.get("id"),
                    "price": ad.get("price"),
                    "address": ad.get("address"),
                    "offerType": ad.get("offerType"),
                    "disposition": ad.get("disposition"),
                    "surface": ad.get("surface"),
                    "garage": ad.get("garage"),
                    "tags": tags,
                    "furnishing": furnishing,
                    "mhd": mhd,
                    "balcony": balcony,
                    "loggia": loggia,   
                    "latitude": latitude,
                    "longitude": longitude,
                    "imageAltText": ad.get("imageAltText"),
                    "main_image": main_image_url,
                    "all_images": all_images_urls,
                })

            offset += limit

        except RequestException as e:
            print(f"Error: {e}")
            break

    df = pd.DataFrame(all_data)


    print("Total records received:", len(df))
    return df

def parse_sreality_sell_data(pages=5):
    url = "https://www.sreality.cz/api/cs/v2/estates"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    all_data = []
    per_page = 100  
    for page in range(pages):
        params = {
            "category_main_cb": 1,      
            "category_type_cb": 1,     
            "per_page": per_page,
            "locality_region_id": 10,
            "page": page
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  
            data = response.json()

            estates = data['_embedded']['estates']

            for estate in estates:
                labels_all = estate.get("labelsAll", [])
                tech_labels = labels_all[0] if len(labels_all) > 0 else []
                infra_labels = labels_all[1] if len(labels_all) > 1 else []
                images_links = estate.get("_links", {}).get("images", [])
                image_urls = [img.get("href") for img in images_links if img.get("href")]
                main_image = image_urls[0] if image_urls else "https://via.placeholder.com/400x300?text=No+Photo"

               
                if 'furnished' in tech_labels:
                    furnishing = 'furnished'
                elif 'partly_furnished' in tech_labels:
                    furnishing = 'partly_furnished'
                elif 'not_furnished' in tech_labels:
                    furnishing = 'not_furnished'
                else:
                    furnishing = None

                mhd_tag={'bus_public_transport', 'tram', 'metro' , 'train'}
                mhd=any(tag in infra_labels for tag in mhd_tag)
                garage=any('garage' in tech_labels for infa in tech_labels)
                loggia=any('loggia' in tech_labels for infa in tech_labels)
                balcony=any('balcony' in tech_labels for infa in tech_labels)
                gps=estate.get("gps" , {})
                latitude=gps.get("lat") 
                longitude= gps.get("lon") 
                all_data.append({
                    "id":estate.get("hash_id"),
                    "locality": estate.get("locality"),
                    "price": estate.get("price"),
                    "name": estate.get("name"),
                    "city_raw": estate.get("seo", {}).get("locality"),
                    "labels_all": labels_all,
                    "furnishing": furnishing,
                    "mhd": mhd,
                    "garage": garage,
                    "loggia": loggia,
                    "balcony": balcony,
                    "gps": gps,
                    "latitude": latitude,
                    "longitude": longitude,
                    "main_image": main_image,       # Ссылка на главное фото
                    "all_images": image_urls,
                })

        except requests.exceptions.RequestException as e:
            print(f"Error while fetching page {page + 1}: {e}")
            break

    df = pd.DataFrame(all_data)
    print("✅ Total listings fetched:", len(df))
    return df
