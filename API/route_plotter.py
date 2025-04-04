# Import the needed Liabraries
import os
import numpy as np
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import pip._vendor.requests as requests
import xml.etree.ElementTree as ET
from tqdm import tqdm
from django.http import JsonResponse
from multiprocessing import Process

import plotly.express as px
import logging
from functools import lru_cache

# Path declaration for reading csv file
FILE = os.path.abspath(__file__)
BASE_DIR = os.path.dirname(FILE)

# keep track of execution events where necessary
logger = logging.getLogger(__name__)
DEBUG = True

# Get the corresponding latitude and longitude of the specified location
@lru_cache(maxsize=None)
def geocode(location):
    return _geocode(location)

def _geocode(location):
    loc = Nominatim(user_agent="Geopy Library")
    getLoc = loc.geocode(location)
    loc = (getLoc.longitude, getLoc.latitude) 
    return loc

# Comput the distance traveled using the geopy library
@lru_cache(maxsize=None)
def distance(origin, dest):
    response = _distance(origin, dest)
    return response

def _distance(origin, dest):
    distance_ = geodesic((geocode(origin)[1], geocode(origin)[0]), (geocode(dest)[1], geocode(dest)[0])).miles
    return distance_

@lru_cache(maxsize=None)
# Response_Type can either be a Json object or a dictionary 
def get_route(origin, destination, response_type):

# format the origin name into its corresponding lat-lon and destination name into its corresponding lat-lon  
    start = "{},{}".format(geocode(origin)[0], geocode(origin)[1])
    end = "{},{}".format(geocode(destination)[0], geocode(destination)[1])
    # Service - 'route', mode of transportation - 'driving', without alternatives
    url = 'http://router.project-osrm.org/route/v1/driving/{};{}?alternatives=false&annotations=nodes'.format(start, end)


    headers = { 'Content-type': 'application/json'}
    r = requests.get(url, headers = headers)
    # print("Calling API ...:", r.status_code) # Status Code 200 is success


    routejson = r.json()
    # print(routejson)
    route_nodes = routejson['routes'][0]['legs'][0]['annotation']['nodes']

    # Get the distance travelled from origin to destination
    distance_traveled =  distance(origin, destination)

    ### keeping every three hundredth element in the node list to optimise time
    # Note: the distance between each node on the rout is 100 metres apart
    route_list = []
    for i in range(0, len(route_nodes)):
        if i % 300 == 1:
            route_list.append(route_nodes[i])

    coordinates = []

    for node in tqdm(route_list):
        try:
            url = 'https://api.openstreetmap.org/api/0.6/node/' + str(node)
            r = requests.get(url, headers = headers)
            myroot = ET.fromstring(r.text)
            for child in myroot:
                lat, long = child.attrib['lat'], child.attrib['lon']
            coordinates.append((lat, long))
        except:
            continue

    df_out = pd.DataFrame({'Node': np.arange(len(coordinates))})
    # df_out['nodes'] = final_nodes
    df_out['coordinates'] = coordinates
    df_out[['lat', 'long']] = pd.DataFrame(df_out['coordinates'].tolist())

    # Converting Latitude and Longitude into float
    df_out['lat'] = df_out['lat'].astype(float)
    df_out['long'] = df_out['long'].astype(float)

    df_lat = df_out['lat'].to_list()
    df_long = df_out['long'].to_list()
    lon_lat = zip(df_long, df_lat)


    # Get the average price data from the csv file to calculate the money spent on gas per distance 
    # price_data = pd.read_csv('C:/Users/ISAAC/Desktop/ASSIGNMENT/Django Developer/Route/fuel-prices-for-be-assessment.csv')
    price_data = pd.read_csv(BASE_DIR + "/fuel-prices-for-be-assessment.csv")

    average_price = price_data['Retail Price'].mean() 
    # Assuming a gallon of gas can cover up to 10 miles (divide the distance traveled by 10 to get the total number of gallons used)
    gallons = distance_traveled / 10
    # Total cost of fuel will now be the total cost of gas multiplied by the average price gotten from the price data file
    total_fuel_cost = gallons * average_price
     # Data to be returned as a Python dictionary
    DictData = {
        "data": df_out, 
        "lon_lat": lon_lat,
        "lat": df_lat,
        "lon": df_long,
        "distance": f"{distance_traveled} Miles", 
        "gallons": gallons, 
        "average_price": f"${average_price}", 
        "total_cost": f"${total_fuel_cost}", 
        # "nodes": final_nodes, 
        "length": len(route_list)
        }
    # Data to be returned in Json format
    JsonData = {
        "data": df_out.to_dict(),
        "distance": f"{distance_traveled} Miles", 
        "gallons": gallons, 
        "average_price": average_price, 
        "total_cost": total_fuel_cost, 
        }
    if response_type == "Json":
        return JsonResponse(JsonData)
  
    else:
        return DictData


if __name__ == '__main__':
    p = Process(target=get_route, args=('bob',))
    p.start()
    p.join()


