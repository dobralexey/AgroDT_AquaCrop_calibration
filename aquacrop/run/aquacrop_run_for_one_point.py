import os
import subprocess
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


def aquacrop_run_for_one_point(project_name,
                               aquacrop_project_folder,
                               latitude,
                               longitude,
                               simulation_start,
                               simulation_end,
                               growing_season_start,
                               growing_season_end,
                               crop_ref,
                               crop_parameters_dict_new,
                               fertility_stress,
                               soil_df,
                               swo_df,
                               gwt_depth,
                               gwt_ec):
    '''
    Run AquaCrop for one point with parameters
    :param project_name: Project name
    :param latitude: Latitude in degrees (from -90 to 90)
    :param longitude: Longitude in degrees (from -180 to 180)
    :param simulation_start: Simulation start date (yyyymmdd)
    :param simulation_end: Simulation end date (yyyymmdd)
    :param growing_season_start: Onset of the growing period (yyyymmdd)
    :param growing_season_end: End of the growing period (yyyymmdd)
    :param output_path: Folder for outputs results and calculations
    :param aquacrop_project_folder: #Project folder
    :param crop_ref: Reference crop
    :param crop_parameters_dict_new: New crop parameters dict {'parameter': 'value'}
           Show current: crop_parameters = get_crop_parameters_dict(cropfile_path=os.path.join(aquacrop_project_folder, 'CROPS', crop_ref))
    :param fertility_stress: Fertility stress %
    :param soil_df: Soil properties DataFrame
        pd.DataFrame(
            {'horizon_number': [],
             'thickness': [],
             'sat': [],
             'fc': [],
             'wp': [],
             'ksat': [],
             'penetrability': [],
             'gravel': []})
    :param swo_df: Initial soil water content DataFrame
        pd.DataFrame({'horizon_number': [], 'thickness': [], 'wc': [], 'ec': []})
    :param gwt_depth: Groundwater depth (m)
    :param gwt_ec: Groundwater electric conductivity (dS/m)
    :return: None
    '''

    #DEFINE FOLDERS IN PROJECT
    aquacrop_data_folder = os.path.join(aquacrop_project_folder, 'DATA/')
    aquacrop_simul_folder = os.path.join(aquacrop_project_folder, 'SIMUL/')
    aquacrop_crops_folder = os.path.join(aquacrop_project_folder, 'CROPS/')
    aquacrop_project_file_folder = os.path.join(aquacrop_project_folder, 'LIST/')
    aquacrop_parameters_folder = os.path.join(aquacrop_project_folder, 'PARAM/')
    aquacrop_project_out_file_folder = os.path.join(aquacrop_project_folder, 'OUTP/')
    aquacrop_project_results_folder = os.path.join(aquacrop_project_folder, 'RESULTS/')


    #GET ELEVATION (ALTITUDE)
    altitude = get_elevation_by_point(latitude=latitude,
                                      longitude=longitude)

    #DOWNLOAD METEODATA FROM NASAPOWER AND WRITE TO JSON RETURN METEOFILENAME
    meteo_raw_file = 'nasa_power_{date_start}_{date_end}_{latitude}_{longitude}.json'.format(longitude=longitude,
                                                                                             latitude=latitude,
                                                                                             date_start=simulation_start,
                                                                                             date_end=simulation_end)
    get_nasa_power_meteo_data(latitude=latitude,
                              longitude=longitude,
                              date_start=simulation_start,
                              date_end=simulation_end,
                              output_path=aquacrop_project_results_folder,
                              filename=meteo_raw_file)


    #CALCULATE ET0 (REFERENCE EVAPOTRANSPIRATION) AND WRITE TO CSV
    meteo_raw_file_path = os.path.join(aquacrop_project_results_folder, meteo_raw_file)
    meteo_calc_file = eto_calculation(latitude=latitude,
                                      altitude=altitude,
                                      meteo_raw_file_path=meteo_raw_file_path,
                                      meteo_calc_file_folder=aquacrop_project_results_folder,
                                      project_name=project_name)
    meteo_calc_file_folder = os.path.join(aquacrop_project_results_folder, meteo_calc_file)

    #TRANSFORM METEO CSV FILE TO AQUACROP CLIMATE FILES (.CLI)
    climate_file, temperature_file, rain_file, eto_file = create_aquacrop_meteo_files(project_name=project_name,
                                                                                      meteo_csvfile_path=meteo_calc_file_folder,
                                                                                      meteo_files_folder=aquacrop_data_folder)

    #CREATE CALENDAR FILE (.CAL)
    calendar_file = create_aquacrop_calendar_file(project_name=project_name,
                                                  growing_season_start=growing_season_start,
                                                  calendar_file_folder=aquacrop_data_folder)

    #MODIFY CROP PARAMETERS
    crop_file = modify_aquacrop_crop_file(project_name=project_name,
                                          crop_parameters_dict_new=crop_parameters_dict_new,
                                          crop_file_folder=aquacrop_data_folder,
                                          crop_ref_folder=aquacrop_crops_folder,
                                          crop_ref=crop_ref)

    #MODIFY FERTILITY STRESS % IN MANAGEMENT (.MAN) FILE
    management_file = modify_aquacrop_fertility_management_file(project_name=project_name,
                                                                management_file_folder=aquacrop_data_folder,
                                                                fertility_stress=fertility_stress)

    #CREATE SOIL (.SOL) FILE
    soil_file = create_aquacrop_soil_file(project_name=project_name,
                                          soil_file_folder=aquacrop_data_folder,
                                          soil_df=soil_df)

    #CREATE GROUNDWATER TABLE (.GWT) FILE
    gwt_file = create_aquacrop_gwt_file(project_name=project_name,
                                        gwt_file_folder=aquacrop_data_folder,
                                        depth=gwt_depth,
                                        ec=gwt_ec)

    #CREATE INITIAL CONDITION (.SW0) FILE
    swo_file = create_aquacrop_swo_file(project_name=project_name,
                                        swo_file_folder=aquacrop_data_folder,
                                        swo_df=swo_df)

    #CREATE PARAMETERS FILE
    create_aquacrop_parameters_file(aquacrop_parameters_file_folder=aquacrop_parameters_folder,
                                    project_name=project_name)
    #CREATE PROJECT FILE
    project_file = create_aquacrop_project_file(simulation_start=simulation_start,
                                                simulation_end=simulation_end,
                                                growing_season_start=growing_season_start,
                                                growing_season_end=growing_season_end,
                                                project_name=project_name,
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

    #CREATE PROJECTS TXT LIST FOR RUN AQUACROP
    project_list = [project_file]
    create_aquacrop_project_list(aquacrop_project_file_folder=aquacrop_project_file_folder,
                                 project_list=project_list)
    #RUN AQUACROP

    aquacrop_exe_path = os.path.join(aquacrop_project_folder, 'aquacrop')

    subprocess.call(aquacrop_exe_path)

    #CREATE CSV OUT FILE AND DARAFRAME
    aquacrop_daily_out_to_csv_df(aquacrop_project_out_file_folder=aquacrop_project_out_file_folder,
                                 aquacrop_project_out_csvfile_folder=aquacrop_project_results_folder,
                                 project_name=project_name,
                                 csv_write=True)