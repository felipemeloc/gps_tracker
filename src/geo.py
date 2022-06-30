from geopy.distance import geodesic
from geopy.geocoders import Nominatim

def get_distance(coor1:tuple, coor2:tuple)->float:
    distance = geodesic(coor1, coor2).miles
    return distance

def get_coordinates(post_code:str)->tuple:
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.geocode(post_code)
    if location:
        return location.latitude, location.longitude
    else:
        return None