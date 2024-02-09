import requests
import pandas as pd

def get_elevation_by_point(latitude, longitude):
    '''
    :param latitude: latitude in degrees (from -90 to 90)
    :param longitude: longitude in degrees (from -180 to 180)
    :return: elevation (meters)
    '''
    query = ('https://api.open-elevation.com/api/v1/lookup'
             f'?locations={latitude},{longitude}')
    r = requests.get(query).json()  # json object, various ways you can extract value
    # one approach is to use pandas json functionality:
    elevation = pd.json_normalize(r, 'results')['elevation'].values[0]
    return elevation