import os
import json
import requests

def get_nasa_power_meteo_data(latitude,
                              longitude,
                              date_start,
                              date_end,
                              filename,
                              output_path,
                              meteo_parameters='T2M,T2M_MAX,T2M_MIN,WS2M,PS,RH2M,PRECTOT,ALLSKY_SFC_SW_DWN'):
    '''
    Function gets meteorological data from nasapower reanalysis: https://power.larc.nasa.gov/#resources
    :param latitude: latitude in degrees (from -90 to 90)
    :param longitude: longitude in degrees (from -180 to 180)
    :param date_start: meteo time series start date (yyyymmdd)
    :param date_end: meteo time series end date (yyyymmdd)
    :param output_path: path to save meteo time series .json file
    :param filename: meteo time series json file name
    :param meteo_parameters: meteorological parameters variables names to download (designation for AG community)
    :return: filename
    '''
    base_url = r"https://power.larc.nasa.gov/api/temporal/daily/point?parameters={meteo_parameters}&community=AG&longitude={longitude}&latitude={latitude}&start={date_start}&end={date_end}&format=JSON"

    api_request_url = base_url.format(meteo_parameters=meteo_parameters,
                                      longitude=longitude,
                                      latitude=latitude,
                                      date_start=date_start,
                                      date_end=date_end)

    response = requests.get(url=api_request_url, verify=True, timeout=30.00)

    content = json.loads(response.content.decode('utf-8'))

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    filepath = os.path.join(output_path, filename)

    with open(filepath, 'w') as file_object:
        json.dump(content, file_object)

    return filename
