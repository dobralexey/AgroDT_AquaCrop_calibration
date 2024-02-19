import os
import pandas as pd
import numpy as np
import subprocess
from SALib.sample import sobol
from aquacrop.tools.meteo_downloader import get_nasa_power_meteo_data
from aquacrop.tools.elevation_downloader import get_elevation_by_point
from aquacrop.tools.crop_functions import get_crop_parameters_dict
from aquacrop.tools.format_aquacrop import (create_aquacrop_meteo_files,
                                            create_aquacrop_calendar_file,
                                            modify_aquacrop_crop_file,
                                            modify_aquacrop_fertility_management_file,
                                            create_aquacrop_soil_file,
                                            create_aquacrop_swo_file,
                                            create_aquacrop_gwt_file,
                                            create_aquacrop_project_file,
                                            create_aquacrop_parameters_file,
                                            create_aquacrop_project_list,
                                            aquacrop_daily_out_to_csv_df)

from aquacrop.models.fao_56_reference_evapotranspiration import eto_calculation

def aquacrop_run_variety_calibration(project_name_base,
                                   aquacrop_project_folder,
                                   latitude,
                                   longitude,
                                   yield_measured,
                                   simulation_starts,
                                   simulation_ends,
                                   growing_season_starts,
                                   growing_season_ends,
                                   crop_ref,
                                   crop_parameters_dict_new,
                                   fertility_stress_range,
                                   parameters_for_calibration,
                                   crop_parameters_rounds,
                                   range_percent,
                                   soil_df,
                                   swo_dfs,
                                   gwt_depth,
                                   gwt_ec,
                                   N=8):

    '''
    :param project_name_base: Base project name for calibration
    :param aquacrop_project_folder:  Path to project folder with aquacrop executable
    :param latitude: Latitude in degrees (from -90 to 90)
    :param longitude: Longitude in degrees (from -180 to 180)
    :param yield_measured: Measured crop yield (t/ha)
    :param simulation_starts: List of simulation starts [yyyymmdd, yyyymmdd .... ]
    :param simulation_ends: List of simulation ends [yyyymmdd, yyyymmdd .... ]
    :param growing_season_starts: List of growing season starts [yyyymmdd, yyyymmdd .... ]
    :param growing_season_ends: List of growing season ends [yyyymmdd, yyyymmdd .... ]
    :param crop_ref: Reference crop
    :param crop_parameters_dict_new: New crop parameters dict {'parameter': 'value'}
    :param fertility_stress_range: range of fertility stress for calibration
    :param parameters_for_calibration: List of crop parameters for calibration
    :param crop_parameters_rounds: decimal signs for parameters
    :param range_percent: percent to range crop parameters (parameters_for_calibration)
    :param soil_df: Soil properties DataFrame (up to 5)
        pd.DataFrame(
            {'horizon_number': [],
             'thickness': [],
             'sat': [],
             'fc': [],
             'wp': [],
             'ksat': [],
             'penetrability': [],
             'gravel': []})
    :param swo_dfs: List of DataFrames with initial soil water content for each year
        [pd.DataFrame({'horizon_number': [], 'thickness': [], 'wc': [], 'ec': []}),
         pd.DataFrame({'horizon_number': [], 'thickness': [], 'wc': [], 'ec': []}) ....]
    :param gwt_depth: Groundwater depth (m)
    :param gwt_ec: Groundwater electric conductivity (dS/m)
    :param N: amount of parameters combination
    :return: crop_parameters_result, best_error
    '''

    aquacrop_data_folder = os.path.join(aquacrop_project_folder, 'DATA/')
    aquacrop_simul_folder = os.path.join(aquacrop_project_folder, 'SIMUL/')
    aquacrop_crops_folder = os.path.join(aquacrop_project_folder, 'CROPS/')
    aquacrop_project_file_folder = os.path.join(aquacrop_project_folder, 'LIST/')
    aquacrop_parameters_folder = os.path.join(aquacrop_project_folder, 'PARAM/')
    aquacrop_project_out_file_folder = os.path.join(aquacrop_project_folder, 'OUTP/')
    aquacrop_project_results_folder = os.path.join(aquacrop_project_folder, 'RESULTS/')


    crop_default_parameters = pd.to_numeric(get_crop_parameters_dict(os.path.join(aquacrop_crops_folder, crop_ref)))
    crop_default_parameters_filter = crop_default_parameters.loc[parameters_for_calibration]
    crop_default_parameters_filter_limits = crop_default_parameters_filter.apply(lambda x: [x - (x * range_percent/100), x + (x * range_percent/100)])
    crop_default_parameters_filter_limits.to_dict()
    crop_parameters_range = list(crop_default_parameters_filter_limits.items())

    #SIMULATION PARAMETERS
    calibration_period_start = simulation_starts[0]
    calibration_period_end = simulation_ends[-1]
    years = [int(str(i)[:4]) for i in growing_season_starts]


    #CREATE PARAMETERS COMBINATION
    num_vars = len(crop_parameters_range) + 1
    names = [i[0] for i in crop_parameters_range]
    names.append('fertility_stress')
    bounds = [i[1] for i in crop_parameters_range]
    bounds.append(fertility_stress_range)

    problem = {
        'num_vars': num_vars,
        'names': names,
        'bounds': bounds
    }

    param_values = sobol.sample(problem, N)          #parameters_matrix


    #=======================METEOROLOGICAL DATA=============================
    # GET ELEVATION (ALTITUDE)
    altitude = get_elevation_by_point(latitude=latitude,
                                      longitude=longitude)

    # DOWNLOAD METEODATA FROM NASAPOWER AND WRITE TO JSON RETURN METEOFILENAME
    meteo_raw_file = 'nasa_power_{date_start}_{date_end}_{latitude}_{longitude}.json'.format(longitude=longitude,
                                                                                             latitude=latitude,
                                                                                             date_start=calibration_period_start,
                                                                                          date_end=calibration_period_end)
    get_nasa_power_meteo_data(latitude=latitude,
                              longitude=longitude,
                              date_start=calibration_period_start,
                              date_end=calibration_period_end,
                              output_path=aquacrop_project_results_folder,
                              filename=meteo_raw_file)

    # CALCULATE ET0 (REFERENCE EVAPOTRANSPIRATION) AND WRITE TO CSV
    meteo_raw_file_path = os.path.join(aquacrop_project_results_folder, meteo_raw_file)
    meteo_calc_file = eto_calculation(latitude=latitude,
                                      altitude=altitude,
                                      meteo_raw_file_path=meteo_raw_file_path,
                                      meteo_calc_file_folder=aquacrop_project_results_folder,
                                      project_name=project_name_base)
    meteo_calc_file_folder = os.path.join(aquacrop_project_results_folder, meteo_calc_file)

    # TRANSFORM METEO CSV FILE TO AQUACROP CLIMATE FILES (.CLI)
    climate_file, temperature_file, rain_file, eto_file = create_aquacrop_meteo_files(project_name=project_name_base,
                                                                                      meteo_csvfile_path=meteo_calc_file_folder,
                                                                                      meteo_files_folder=aquacrop_data_folder)

    #====================SOIL===================
    #Soil parameters static

    # CREATE SOIL (.SOL) FILE
    soil_file = create_aquacrop_soil_file(project_name=project_name_base,
                                          soil_file_folder=aquacrop_data_folder,
                                          soil_df=soil_df)

    # CREATE GROUNDWATER TABLE (.GWT) FILE
    gwt_file = create_aquacrop_gwt_file(project_name=project_name_base,
                                        gwt_file_folder=aquacrop_data_folder,
                                        depth=gwt_depth,
                                        ec=gwt_ec)

    #===============INPUT PARAMETERS=====================================

    # CREATE LIST FOR ERRORS
    errors = []

    for i, year in enumerate(years):

        project_name = f'{project_name_base}_{year}'
        simulation_start = simulation_starts[i]
        simulation_end = simulation_ends[i]
        growing_season_start = growing_season_starts[i]
        growing_season_end = growing_season_ends[i]

    # CREATE CALENDAR FILE (.CAL)
        calendar_file = create_aquacrop_calendar_file(project_name=project_name,
                                                      growing_season_start=growing_season_start,
                                                      calendar_file_folder=aquacrop_data_folder)

        swo_df = swo_dfs[i]

        # CREATE INITIAL CONDITION (.SW0) FILE
        swo_file = create_aquacrop_swo_file(project_name=project_name,
                                            swo_file_folder=aquacrop_data_folder,
                                            swo_df=swo_df)

        for num, value in enumerate(param_values):

            project_list = []


            project_name_num = f'{project_name_base}_{year}_{num}'

            for ii in range(len(names)-1):
                crop_parameters_dict_new[names[ii]] = str(round(value[ii], crop_parameters_rounds[ii]))

            # MODIFY CROP PARAMETERS
            crop_file = modify_aquacrop_crop_file(project_name=project_name_num,
                                                  crop_parameters_dict_new=crop_parameters_dict_new,
                                                  crop_file_folder=aquacrop_data_folder,
                                                  crop_ref_folder=aquacrop_crops_folder,
                                                  crop_ref=crop_ref)
            fertility_stress = round(value[-1])

            # MODIFY FERTILITY STRESS % IN MANAGEMENT (.MAN) FILE
            management_file = modify_aquacrop_fertility_management_file(project_name=project_name_num,
                                                                        management_file_folder=aquacrop_data_folder,
                                                                        fertility_stress=fertility_stress)


            # CREATE PARAMETERS FILE
            parameters_file = create_aquacrop_parameters_file(aquacrop_parameters_file_folder=aquacrop_parameters_folder,
                                            project_name=project_name_num)
            # CREATE PROJECT FILE
            project_file = create_aquacrop_project_file(simulation_start=simulation_start,
                                                        simulation_end=simulation_end,
                                                        growing_season_start=growing_season_start,
                                                        growing_season_end=growing_season_end,
                                                        project_name=project_name_num,
                                                        climate_file=climate_file,
                                                        temperature_file=temperature_file,
                                                        eto_file=eto_file,
                                                        rain_file=rain_file,
                                                        calendar_file=calendar_file,
                                                        crop_file=crop_file,
                                                        management_file=management_file,
                                                        soil_file=soil_file,
                                                        gwt_file=gwt_file,
                                                        swo_file=swo_file,
                                                        project_file_folder=aquacrop_project_file_folder,
                                                        aquacrop_data_path_folder=aquacrop_data_folder,
                                                        aquacrop_simul_path_folder=aquacrop_simul_folder)
            project_list.append(project_file)

            create_aquacrop_project_list(aquacrop_project_file_folder=aquacrop_project_file_folder,
                                         project_list=project_list)

            aquacrop_exe_path = os.path.join(aquacrop_project_folder, 'aquacrop.exe')

            subprocess.call(aquacrop_exe_path)

            daily_out_file, season_out_file, df = aquacrop_daily_out_to_csv_df(aquacrop_project_out_file_folder=aquacrop_project_out_file_folder,
                                         aquacrop_project_out_csvfile_folder=aquacrop_project_results_folder,
                                         project_name=project_name_num,
                                         csv_write=False)

            yield_simulated = df['Y(dry)'].iloc[-1]

            error = np.sqrt((yield_measured[i] - yield_simulated)**2)                   #RMSE

            errors.append((year, num, error))

            #REMOVE TEMPORAL FILES

            os.remove(os.path.join(aquacrop_data_folder, crop_file))
            os.remove(os.path.join(aquacrop_data_folder, management_file))
            os.remove(os.path.join(aquacrop_parameters_folder, parameters_file))
            os.remove(os.path.join(aquacrop_project_file_folder, project_file))
            os.remove(os.path.join(aquacrop_project_out_file_folder, daily_out_file))
            os.remove(os.path.join(aquacrop_project_out_file_folder, season_out_file))

        os.remove(os.path.join(aquacrop_data_folder, swo_file))
        os.remove(os.path.join(aquacrop_data_folder, calendar_file))

    os.remove(os.path.join(aquacrop_data_folder, climate_file))
    os.remove(os.path.join(aquacrop_data_folder, temperature_file))
    os.remove(os.path.join(aquacrop_data_folder, rain_file))
    os.remove(os.path.join(aquacrop_data_folder, eto_file))
    os.remove(os.path.join(aquacrop_data_folder, soil_file))
    os.remove(os.path.join(aquacrop_data_folder, gwt_file))

    df_errors = pd.DataFrame(errors, columns=['year', 'num_iteration', 'error'])
    df_errors_gr = df_errors.groupby(by='num_iteration').mean()
    best_num_iteration = df_errors_gr['error'].idxmin()

    best_param_values_round = []
    for i in range(len(param_values[best_num_iteration])-1):
        best_param_values_round.append(round(param_values[best_num_iteration][i], crop_parameters_rounds[i]))
    best_param_values_round.append(round(param_values[best_num_iteration][-1], crop_parameters_rounds[-1]))

    best_error = str(df_errors_gr['error'].min())

    crop_parameters_result = dict(zip(names, best_param_values_round))

    return crop_parameters_result, best_error

