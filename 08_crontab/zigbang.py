import pymongo
import requests
import geohash2
import time
import pandas as pd

def get_items(addr, ip):
    url = "https://apis.zigbang.com/search?q={}".format(addr)
    response = requests.get(url)
    data = response.json()["items"][0]
    lat, lng = data["lat"], data["lng"]
    geohash = geohash2.encode(lat, lng, precision=5)

    url = "https://apis.zigbang.com/v2/items?deposit_gteq=0&domain=zigbang&geohash={}&rent_gteq=0&sales_type_in=전세|월세&service_type_eq=원룸".format(geohash)
    response = requests.get(url)
    item_ids = [data["item_id"] for data in response.json()["items"]]
    time.sleep(5)
    
    url = "https://apis.zigbang.com/v2/items/list"
    params = {
        "domain": "zigbang",
        "item_ids": item_ids,
        "withCoalition": "true",
    }
    response = requests.post(url, data=params)
    datas = response.json()["items"]

    columns = ["item_id", "address1", "address2", "building_floor", "floor",
               "deposit", "rent", "sales_type", "size_m2", "random_location"]
    result_df = pd.DataFrame(datas)[columns]
    result_df["lat"] = result_df["random_location"].apply(lambda data: data["lat"])
    result_df["lng"] = result_df["random_location"].apply(lambda data: data["lng"])
    result_df.drop(columns="random_location", inplace=True)
    items_df = result_df[result_df["address1"].str.contains(addr)].reset_index(drop=True)
    items_dict = items_df.to_dict("records")
    
    client = pymongo.MongoClient('mongodb://{}:27017/'.format(ip))
    db = client.zigbang
    collection = db.oneroom
    
    collection.insert(items_dict)
