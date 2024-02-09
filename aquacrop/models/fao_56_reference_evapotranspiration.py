import os
import json
import math
import numpy as np
import pandas as pd

from AgroMetEquations.evapotranspiration_equations import fao56_penman_monteith
from AgroMetEquations.auxiliary import (get_solar_declination,
                                        get_sunset_hour_angle,
                                        get_daylight_hours,
                                        get_inverse_relative_distance_earth_sun,
                                        get_daily_extraterrestrial_radiation,
                                        get_clear_sky_radiation,
                                        get_svp_from_temp,
                                        get_svp,
                                        get_avp_from_rhmean,
                                        get_net_out_lw_rad,
                                        celsius2kelvin,
                                        get_net_in_sol_rad,
                                        get_net_rad,
                                        get_latent_heat,
                                        get_delta_svp,
                                        get_psy_const)


def eto_calculation(latitude,
                    altitude,
                    meteo_raw_file_path,
                    meteo_calc_file_folder,
                    project_name,
                    albedo=0.23,
                    time_period='daily',
                    temperature_avg_name='T2M',
                    temperature_min_name='T2M_MIN',
                    temperature_max_name='T2M_MAX',
                    wind_speed_name='WS2M',
                    atmospheric_pressure_name='PS',
                    relative_humidity_name='RH2M',
                    global_radiation_name='ALLSKY_SFC_SW_DWN',
                    precipitation_name='PRECTOTCORR'):
    '''
    Function for calculation FAO-56 Reference Evapotranspiration
    based on modified Penman-Monteith equation in Allen et al (1998).
    :param latitude: latitude in degrees
    :param altitude: height above mean sea level
    :param meteofile_path: input nasapower meteo file path (tools.meteo_downloader.get_nasa_power_meteo_data)
    :param output_path: output path for meteorological csv file
    :param albedo: reference surface albedo (=0.23 in Allen et al (1998))
    :param time_period: usually daily
    :param temperature_avg_name: average air temperature nasapower variable name
    :param temperature_min_name: minimum air temperature nasapower variable name
    :param temperature_max_name: maximum air temperature nasapower variable name
    :param wind_speed_name: wind speed nasapower variable name
    :param atmospheric_pressure_name: atmospheric pressure nasapower variable name
    :param relative_humidity_name: relative humidity nasapower variable name
    :param global_radiation_name: global radiation nasapower variable name
    :param precipitation_name: precipitation nasapower variable name
    :return: filename for meteorological csvfile
    '''

    # Convert latitude from degrees to radians
    latitude = math.radians(latitude)
    # Open meteo .json file
    data = json.load(open(meteo_raw_file_path))
    # Transform .json file to Pandas DataFrame
    df = pd.DataFrame(data['properties']['parameter'])
    # -999 is missing values, replace to NaN
    df.replace(-999.00, np.nan)
    # Set datetime column from DataFrame index
    df['datetime'] = df.index
    # Str format to datetime format
    df['datetime'] = pd.to_datetime(df.index)
    # Get day of the year (doy) from datetime
    df['doy'] = df['datetime'].apply(lambda x: int(x.strftime('%j')))
    # Calculate solar declination
    df['solar_dec'] = df['doy'].apply(get_solar_declination)
    # Calculate sunset hour angle
    df['sunset_hour_angle'] = df.apply(lambda x: get_sunset_hour_angle(latitude, x.solar_dec), axis=1)
    # Calculate daylight hours
    df['daylight_hours'] = df['sunset_hour_angle'].apply(get_daylight_hours)
    # Calculate relative distance between Earth and Sun
    df['inv_rel_dist_earth_sun'] = df['doy'].apply(get_inverse_relative_distance_earth_sun)
    # Calculate extraterrestrial radiation [MJ m-2 day-1]
    df['ext_rad'] = df.apply(lambda x: get_daily_extraterrestrial_radiation(latitude, x.solar_dec, x.sunset_hour_angle,
                                                                            x.inv_rel_dist_earth_sun), axis=1)
    # Calculate clear sky radiation [MJ m-2 day-1]
    df['cs_rad'] = df.apply(lambda x: get_clear_sky_radiation(altitude, x.ext_rad), axis=1)
    # Calculate saturated vapour pressure with minimum temperature [kPa]
    df['svp_min'] = df[temperature_min_name].apply(get_svp_from_temp)
    # Calculate saturated vapour pressure with maximum temperature [kPa]
    df['svp_max'] = df[temperature_max_name].apply(get_svp_from_temp)
    # Calculate saturated vapour pressure [kPa]
    df['svp'] = df.apply(lambda x: get_svp(x.svp_min, x.svp_max), axis=1)
    # Calculate actual vapour pressure [kPa]
    df['avp'] = df.apply(lambda x: get_avp_from_rhmean(x.svp_min, x.svp_max, x[relative_humidity_name]), axis=1)
    # Convert minimum temperature from Celcius to Kelvin scale
    df['temperature_kelvin_min'] = df[temperature_min_name].apply(celsius2kelvin)
    # Convert maximum temperature from Celcius to Kelvin scale
    df['temperature_kelvin_max'] = df[temperature_max_name].apply(celsius2kelvin)
    # Calculate longwave radiation balance [MJ m-2 day-1]
    df['net_out_lw_rad'] = df.apply(lambda x: get_net_out_lw_rad(x.temperature_kelvin_min, x.temperature_kelvin_max,
                                                                 x[global_radiation_name], x.cs_rad, x.avp,
                                                                 time_period=time_period), axis=1)
    # Calculate shortwave radiation balance [MJ m-2 day-1]
    df['net_in_sol_rad'] = df.apply(lambda x: get_net_in_sol_rad(x[global_radiation_name], albedo), axis=1)
    # Calculate net radiation [MJ m-2 day-1]
    df['daily_net_radiation'] = df.apply(lambda x: get_net_rad(x.net_in_sol_rad, x.net_out_lw_rad), axis=1)
    # Soil heat flux (daily = 0)
    soil_heat_flux = 0
    # Calculate latent heat
    df['latent_heat'] = df[temperature_avg_name].apply(get_latent_heat)
    # Calculate the slope of the saturation vapour pressure curve at a given temperature
    df['delta_svp'] = df[temperature_avg_name].apply(get_delta_svp)
    # Calculate the psychrometric constant
    df['gamma'] = df.apply(lambda x: get_psy_const(x[atmospheric_pressure_name], x.latent_heat), axis=1)
    # Calculate reference evapotranspiration (ET0)
    df['ET0'] = df.apply(lambda x: fao56_penman_monteith(x.daily_net_radiation, x[temperature_avg_name],
                                                         x[wind_speed_name], x.latent_heat, x.svp,
                                                         x.avp, x.delta_svp, x.gamma, x[global_radiation_name],
                                                         soil_heat_flux, time_period=time_period), axis=1)
    df['ET0'] = df['ET0'].where(df['ET0']>0, 0)
    #Create minumum temperature column with name Tn
    df['Tn'] = df[temperature_min_name]
    #Create maximum temperature column with name Tx
    df['Tx'] = df[temperature_max_name]
    # Create precipitation column with name Pr
    df['Pr'] = df[precipitation_name]
    df['Pr'] = np.where(df['Pr'] < 1, 0, df['Pr'])
    meteo_params = ['Tx', 'Tn', 'Pr', 'ET0']
    #Write csv file with meteo parameters for AquaCrop
    meteo_calc_file = f'Meteo_calc_data_{project_name}.csv'
    meteo_calc_file_path = os.path.join(meteo_calc_file_folder, meteo_calc_file)
    df[meteo_params].to_csv(meteo_calc_file_path)

    return meteo_calc_file





