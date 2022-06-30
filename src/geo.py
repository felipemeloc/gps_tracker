"""geo.py

Contains the following function:
* get_distance: Return a float regarding the distance between two coordinates. use:
    import geo
    geo.get_distance(coor1 = (LATITUDE, LONGITUDE), coor2 = (LATITUDE, LONGITUDE))

* get_coordinates: Return a tuple with the coordinates of the input postcode. use:
    import geo
    geo.get_coordinates(post_code = 'YOUR POSTCODE)

"""


from geopy.distance import geodesic
from geopy.geocoders import Nominatim

def get_distance(coor1:tuple[float, float], coor2:tuple[float, float])->float:
    """Function to calculate the distance between two coordinates

    Args:
        coor1 (tuple[float, float]): coordinate #1 (latitude, longitude)
        coor2 (tuple[float, float]): coordinate #2 (latitude, longitude)

    Returns:
        float: distance between the two coordinates. Number.
    """    
    distance = geodesic(coor1, coor2).miles
    return distance

def get_coordinates(post_code:str)->tuple[float, float]:
    """Function to get the coordinates (latitude and longitude) from a postcode

    Args:
        post_code (str): postcode to be transform to coordinate

    Returns:
        tuple[float, float]: coordinate (latitude, longitude)
    """    
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.geocode(post_code)
    if location:
        return location.latitude, location.longitude
    else:
        return None