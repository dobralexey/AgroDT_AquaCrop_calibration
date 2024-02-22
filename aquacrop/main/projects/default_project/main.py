import os
import pandas as pd
from aquacrop.run.aquacrop_run_variety_calibration import aquacrop_run_variety_calibration
from aquacrop.run.aquacrop_run_for_one_point import aquacrop_run_for_one_point

#ШАГ 1 - КАЛИБРОВКА СОРТА ПРИ ОТСУТСВИИ СТРЕССА МИНЕРАЛЬНОГО ПИТАНИЯ
#ШАГ 2 - КАЛИБРОВКА СОРТА ПОД ОПРЕДЕЛЕННЫЙ УРОВЕНЬ ТЕХНОЛОГИИ И СТРЕСС МИНЕРАЛЬНОГО ПИТАНИЯ
#ШАГ 3 - МОДЕЛИРОВАНИЕ РАЗЛИЧНЫХ СЦЕНАРИЕВ ПОЧВЕННЫХ + МЕТЕОРОЛОГИЧЕСКИХ

#----ВХОДНЫЕ ПАРАМЕТРЫ ОБЩИЕ ДЛЯ ШАГОВ 1, 2, 3----
aquacrop_all_projects_folder = 'C:/Users/Aleksei/PycharmProjects/AgroDT_AquaCrop_calibration/aquacrop/main/projects/'
project_name_base = 'default_project'

latitude = 55.547980                                                                #Latitude in degrees (from -90 to 90)
longitude = 37.234828                                                               #Longitude in degrees (from -180 to 180)
# crop_list = os.listdir('./CROPS')
crop_ref = 'Wheat.CRO'                                                              #Reference crop

crop_parameters_dict_new = {'Number of plants per hectare': 4500000,
                            'Calendar Days: from sowing to emergence': 12,
                            'Calendar Days: from sowing to maximum rooting depth': 80,
                            'Calendar Days: from sowing to start senescence': 100,
                            'Calendar Days: from sowing to maturity (length of crop cycle)': 112,
                            'Calendar Days: from sowing to flowering': 80,
                            'Length of the flowering stage (days)': 13,
                            'Building up of Harvest Index starting at flowering (days)': 30,
                            'Minimum effective rooting depth (m)': 0.3,
                            'Maximum effective rooting depth (m)': 1.5
                            }

#Soil constants (up to 5 layers!)
soil_df = pd.DataFrame({'horizon_number': [1, 2, 3, 4, 5],
                        'thickness': [0.23, 0.10, 0.11, 0.39, 0.97],
                        'sat': [48.0, 46.0, 45.0, 41.0, 39.0],
                        'fc': [45.0, 43.0, 42.0, 34.0, 23.0],
                        'wp': [14.0, 15.0, 16.0, 12.0, 7.0],
                        'ksat': [602.0, 312.0, 167.0, 282.0, 1186.0],
                        'penetrability': [100, 100, 100, 100, 100],
                        'gravel': [0, 0, 0, 0, 0]})
#Ground water table (meters)
gwt_depth = 10
#Groundwater electrical conductivity
gwt_ec = 0

# ШАГ 1. ВХОДНЫЕ ДАННЫЕ ДЛЯ КАЛИБРОВКИ СОРТА БЕЗ СТРЕССА МИНЕРАЛЬНОГО ПИТАНИЯ
yield_measured_no_stress = [3.9, 7.0, 10.05, 10.25, 10.12, 10.18, 10.36, 7.77, 7.85, 10.53]                                          #Yield measured for calibration_no_stress
simulation_starts_no_stress = [20110401, 20120401, 20130401, 20140401, 20150401, 20160401, 20170401, 20180401, 20190401, 20200401]             #Simulation start dates list (yyyymmdd)
simulation_ends_no_stress = [20110915, 20120915, 20130915, 20140915, 20150915, 20160915, 20170915, 20180915, 20190915, 20200915]               #Simulation end dates list (yyyymmdd)
growing_season_starts_no_stress = [20110428, 20120426, 20130505, 20140419, 20150506, 20160427, 20170430, 20180509, 20190505, 20200428]         #Onset of the growing period (yyyymmdd)
growing_season_ends_no_stress = [20110915, 20120915, 20130915, 20140915, 20150915, 20160915, 20170915, 20180915, 20190915, 20200915]           #End of the growing period (yyyymmdd)

#Set Initial soil water content for each year (simulation start dates)
swo_dfs_no_stress = [pd.DataFrame({'horizon_number': [1, 2, 3, 4, 5], 'thickness': [0.23, 0.10, 0.11, 0.39, 0.97], 'wc': [45.00, 43.00, 42.00, 34.00, 23.00], 'ec': [0.00, 0.00, 0.00, 0.00, 0.00]}),
                   pd.DataFrame({'horizon_number': [1, 2, 3, 4, 5], 'thickness': [0.23, 0.10, 0.11, 0.39, 0.97], 'wc': [45.00, 43.00, 42.00, 34.00, 23.00], 'ec': [0.00, 0.00, 0.00, 0.00, 0.00]}),
                   pd.DataFrame({'horizon_number': [1, 2, 3, 4, 5], 'thickness': [0.23, 0.10, 0.11, 0.39, 0.97], 'wc': [45.00, 43.00, 42.00, 34.00, 23.00], 'ec': [0.00, 0.00, 0.00, 0.00, 0.00]}),
                   pd.DataFrame({'horizon_number': [1, 2, 3, 4, 5], 'thickness': [0.23, 0.10, 0.11, 0.39, 0.97], 'wc': [45.00, 43.00, 42.00, 34.00, 23.00], 'ec': [0.00, 0.00, 0.00, 0.00, 0.00]}),
                   pd.DataFrame({'horizon_number': [1, 2, 3, 4, 5], 'thickness': [0.23, 0.10, 0.11, 0.39, 0.97], 'wc': [45.00, 43.00, 42.00, 34.00, 23.00], 'ec': [0.00, 0.00, 0.00, 0.00, 0.00]}),
                   pd.DataFrame({'horizon_number': [1, 2, 3, 4, 5], 'thickness': [0.23, 0.10, 0.11, 0.39, 0.97], 'wc': [45.00, 43.00, 42.00, 34.00, 23.00], 'ec': [0.00, 0.00, 0.00, 0.00, 0.00]}),
                   pd.DataFrame({'horizon_number': [1, 2, 3, 4, 5], 'thickness': [0.23, 0.10, 0.11, 0.39, 0.97], 'wc': [45.00, 43.00, 42.00, 34.00, 23.00], 'ec': [0.00, 0.00, 0.00, 0.00, 0.00]}),
                   pd.DataFrame({'horizon_number': [1, 2, 3, 4, 5], 'thickness': [0.23, 0.10, 0.11, 0.39, 0.97], 'wc': [45.00, 43.00, 42.00, 34.00, 23.00], 'ec': [0.00, 0.00, 0.00, 0.00, 0.00]}),
                   pd.DataFrame({'horizon_number': [1, 2, 3, 4, 5], 'thickness': [0.23, 0.10, 0.11, 0.39, 0.97], 'wc': [45.00, 43.00, 42.00, 34.00, 23.00], 'ec': [0.00, 0.00, 0.00, 0.00, 0.00]}),
                   pd.DataFrame({'horizon_number': [1, 2, 3, 4, 5], 'thickness': [0.23, 0.10, 0.11, 0.39, 0.97], 'wc': [45.00, 43.00, 42.00, 34.00, 23.00], 'ec': [0.00, 0.00, 0.00, 0.00, 0.00]})]

parameters_for_calibration_no_stress = ['Soil water depletion factor for canopy expansion (p-exp) - Upper threshold',
                                      'Soil water depletion factor for canopy expansion (p-exp) - Lower threshold',
                                      'Shape factor for water stress coefficient for canopy expansion (0.0 = straight line)',
                                      'Soil water depletion fraction for stomatal control (p - sto) - Upper threshold',
                                      'Shape factor for water stress coefficient for stomatal control (0.0 = straight line)',
                                      'Soil water depletion factor for canopy senescence (p - sen) - Upper threshold',
                                      'Shape factor for water stress coefficient for canopy senescence (0.0 = straight line)',
                                      'Soil water depletion factor for pollination (p - pol) - Upper threshold',
                                      'Vol% for Anaerobiotic point (* (SAT - [vol%]) at which deficient aeration occurs *)',
                                      'Canopy growth coefficient (CGC): Increase in canopy cover (fraction soil cover per day)',
                                      'Canopy decline coefficient (CDC): Decrease in canopy cover (in fraction per day)',
                                      'Reference Harvest Index (HIo) (%)',
                                      'Water Productivity normalized for ETo and CO2 (WP*) (gram/m2)']

crop_parameters_rounds_no_stress = [2, 2, 1, 2, 1, 2, 1, 2, None, 5, 5, None, 1]
fertility_stress_range_no_stress = [0,0.1]
range_percent_no_stress = 50
N_no_stress = 8

#ШАГ 1. ОСНОВНОЙ КОД
aquacrop_project_folder = os.path.join(aquacrop_all_projects_folder, project_name_base)
crop_parameters_result_no_stress, error_no_stress, crop_file_calibrated_no_stress = aquacrop_run_variety_calibration(
     project_name_base=project_name_base,
     aquacrop_project_folder=aquacrop_project_folder,
     latitude=latitude,
     longitude=longitude,
     yield_measured=yield_measured_no_stress,
     simulation_starts=simulation_starts_no_stress,
     simulation_ends=simulation_ends_no_stress,
     growing_season_starts=growing_season_starts_no_stress,
     growing_season_ends=growing_season_ends_no_stress,
     crop_ref=crop_ref,
     crop_parameters_dict_new=crop_parameters_dict_new,
     fertility_stress_range=fertility_stress_range_no_stress,
     parameters_for_calibration=parameters_for_calibration_no_stress,
     crop_parameters_rounds=crop_parameters_rounds_no_stress,
     range_percent=range_percent_no_stress,
     soil_df=soil_df,
     swo_dfs=swo_dfs_no_stress,
     gwt_depth=gwt_depth,
     gwt_ec=gwt_ec,
     N=N_no_stress,
     fertility_stress_calibration=False)


#ШАГ 2. ВХОДНЫЕ ДАННЫЕ ДЛЯ КАЛИБРОВКИ СТРЕССА ПЛОДОРОДИЯ (ЗЛАТА БАЗОВАЯ ТЕХНОЛОГИЯ)

yield_measured_stress = [2.7, 5.61, 5.01, 5.21, 8.23, 8.17, 8.54, 5.91, 6.39, 8.79]                                      #Yield measured for calibration

simulation_starts_stress = [20110401, 20120401, 20130401, 20140401, 20150401, 20160401, 20170401, 20180401, 20190401, 20200401]             #Simulation start dates list (yyyymmdd)
simulation_ends_stress = [20110915, 20120915, 20130915, 20140915, 20150915, 20160915, 20170915, 20180915, 20190915, 20200915]               #Simulation end dates list (yyyymmdd)
growing_season_starts_stress = [20110428, 20120426, 20130505, 20140419, 20150506, 20160427, 20170430, 20180509, 20190505, 20200428]         #Onset of the growing period (yyyymmdd)
growing_season_ends_stress = [20110915, 20120915, 20130915, 20140915, 20150915, 20160915, 20170915, 20180915, 20190915, 20200915]

#Set Initial soil water content for each year (simulation start dates)
swo_dfs_stress = [pd.DataFrame({'horizon_number': [1, 2, 3, 4, 5], 'thickness': [0.23, 0.10, 0.11, 0.39, 0.97], 'wc': [45.00, 43.00, 42.00, 34.00, 23.00], 'ec': [0.00, 0.00, 0.00, 0.00, 0.00]}),
               pd.DataFrame({'horizon_number': [1, 2, 3, 4, 5], 'thickness': [0.23, 0.10, 0.11, 0.39, 0.97], 'wc': [45.00, 43.00, 42.00, 34.00, 23.00], 'ec': [0.00, 0.00, 0.00, 0.00, 0.00]}),
               pd.DataFrame({'horizon_number': [1, 2, 3, 4, 5], 'thickness': [0.23, 0.10, 0.11, 0.39, 0.97], 'wc': [45.00, 43.00, 42.00, 34.00, 23.00], 'ec': [0.00, 0.00, 0.00, 0.00, 0.00]}),
               pd.DataFrame({'horizon_number': [1, 2, 3, 4, 5], 'thickness': [0.23, 0.10, 0.11, 0.39, 0.97], 'wc': [45.00, 43.00, 42.00, 34.00, 23.00], 'ec': [0.00, 0.00, 0.00, 0.00, 0.00]}),
               pd.DataFrame({'horizon_number': [1, 2, 3, 4, 5], 'thickness': [0.23, 0.10, 0.11, 0.39, 0.97], 'wc': [45.00, 43.00, 42.00, 34.00, 23.00], 'ec': [0.00, 0.00, 0.00, 0.00, 0.00]}),
               pd.DataFrame({'horizon_number': [1, 2, 3, 4, 5], 'thickness': [0.23, 0.10, 0.11, 0.39, 0.97], 'wc': [45.00, 43.00, 42.00, 34.00, 23.00], 'ec': [0.00, 0.00, 0.00, 0.00, 0.00]}),
               pd.DataFrame({'horizon_number': [1, 2, 3, 4, 5], 'thickness': [0.23, 0.10, 0.11, 0.39, 0.97], 'wc': [45.00, 43.00, 42.00, 34.00, 23.00], 'ec': [0.00, 0.00, 0.00, 0.00, 0.00]}),
               pd.DataFrame({'horizon_number': [1, 2, 3, 4, 5], 'thickness': [0.23, 0.10, 0.11, 0.39, 0.97], 'wc': [45.00, 43.00, 42.00, 34.00, 23.00], 'ec': [0.00, 0.00, 0.00, 0.00, 0.00]}),
               pd.DataFrame({'horizon_number': [1, 2, 3, 4, 5], 'thickness': [0.23, 0.10, 0.11, 0.39, 0.97], 'wc': [45.00, 43.00, 42.00, 34.00, 23.00], 'ec': [0.00, 0.00, 0.00, 0.00, 0.00]}),
               pd.DataFrame({'horizon_number': [1, 2, 3, 4, 5], 'thickness': [0.23, 0.10, 0.11, 0.39, 0.97], 'wc': [45.00, 43.00, 42.00, 34.00, 23.00], 'ec': [0.00, 0.00, 0.00, 0.00, 0.00]})]

parameters_for_calibration_stress = ['Response of canopy expansion is not considered']

crop_parameters_rounds_stress = [2]
fertility_stress_range_stress = [1,75]
range_percent_stress = 10
N_stress = 8

crop_parameters_result_stress, error_stress, crop_file_calibrated_stress = aquacrop_run_variety_calibration(
     project_name_base=project_name_base,
     aquacrop_project_folder=aquacrop_project_folder,
     latitude=latitude,
     longitude=longitude,
     yield_measured=yield_measured_stress,
     simulation_starts=simulation_starts_stress,
     simulation_ends=simulation_ends_stress,
     growing_season_starts=growing_season_starts_stress,
     growing_season_ends=growing_season_ends_stress,
     crop_ref=crop_file_calibrated_no_stress,
     crop_parameters_dict_new=crop_parameters_dict_new,
     fertility_stress_range=fertility_stress_range_stress,
     parameters_for_calibration=parameters_for_calibration_stress,
     crop_parameters_rounds=crop_parameters_rounds_stress,
     range_percent=range_percent_stress,
     soil_df=soil_df,
     swo_dfs=swo_dfs_stress,
     gwt_depth=gwt_depth,
     gwt_ec=gwt_ec,
     N=N_stress,
     fertility_stress_calibration=True)

#ШАГ 3. ПОЧВЕННЫЕ И КЛИМАТИЧЕСКИЕ СЦЕНАРИИ
#Выбираем файл культуры crop_file_calibrated_stress или crop_file_calibrated_no_stress (без стресса)
#Значение fertility stress с предыдущего шага или 0 без стресса
crop_file = crop_file_calibrated_stress
fertility_stress_value = int(crop_parameters_result_stress['fertility_stress'])

#придумывает cписок почв для симуляции
soil_dfs = [
pd.DataFrame({'horizon_number': [1, 2, 3, 4, 5],
              'thickness': [0.23, 0.10, 0.11, 0.39, 0.97],
              'sat': [48.0, 46.0, 45.0, 41.0, 39.0],
              'fc': [45.0, 43.0, 42.0, 34.0, 23.0],
              'wp': [14.0, 15.0, 16.0, 12.0, 7.0],
              'ksat': [602.0, 312.0, 167.0, 282.0, 1186.0],
              'penetrability': [100, 100, 100, 100, 100],
              'gravel': [0, 0, 0, 0, 0]}),

pd.DataFrame({'horizon_number': [1, 2, 3, 4, 5],
              'thickness': [0.50, 0.50, 0.50, 0.50, 0.50],
              'sat': [46.0, 46.0, 46.0, 46.0, 46.0],
              'fc': [29.0, 29.0, 29.0, 29.0, 29.0],
              'wp': [13.0, 13.0, 13.0, 13.0, 13.0],
              'ksat': [1200.0, 1200.0, 1200.0, 1200.0, 1200.0],
              'penetrability': [100, 100, 100, 100, 100],
              'gravel': [0, 0, 0, 0, 0]})
]

#пользователь выбирает года и даты начала для проведения симуляции (С 1984)
simulation_starts_scenarios = [19900401, 19910401, 19920401]             #Simulation start dates list (yyyymmdd)
simulation_ends_scenarios = [19900915, 19910915, 19920915]               #Simulation end dates list (yyyymmdd)
growing_season_starts_scenarios = [19900501, 19910501, 19920501]         #Onset of the growing period (yyyymmdd)
growing_season_ends_scenarios = [19900915, 19910915, 19920915]           #End of the growing period (yyyymmdd)
gwt_depth_scenarios = 10
gwt_ec_scenarios = 0

years = [str(i)[:4] for i in simulation_starts_scenarios]

#определяем начальную влажность для симуляций
swo_dfs_scenarios = [pd.DataFrame({'horizon_number': [1, 2, 3, 4, 5], 'thickness': [0.23, 0.10, 0.11, 0.39, 0.97], 'wc': [45.00, 43.00, 42.00, 34.00, 23.00], 'ec': [0.00, 0.00, 0.00, 0.00, 0.00]}),
               pd.DataFrame({'horizon_number': [1, 2, 3, 4, 5], 'thickness': [0.23, 0.10, 0.11, 0.39, 0.97], 'wc': [45.00, 43.00, 42.00, 34.00, 23.00], 'ec': [0.00, 0.00, 0.00, 0.00, 0.00]}),
               pd.DataFrame({'horizon_number': [1, 2, 3, 4, 5], 'thickness': [0.23, 0.10, 0.11, 0.39, 0.97], 'wc': [45.00, 43.00, 42.00, 34.00, 23.00], 'ec': [0.00, 0.00, 0.00, 0.00, 0.00]})]

for soil_n, soil_df in enumerate(soil_dfs):
    for n, year in enumerate(years):
        simulation_start = simulation_starts_scenarios[n]
        simulation_end = simulation_ends_scenarios[n]
        growing_season_start = growing_season_starts_scenarios[n]
        growing_season_end = growing_season_ends_scenarios[n]
        swo_df = swo_dfs_scenarios[n]
        df = aquacrop_run_for_one_point(
           project_name=project_name_base,
           aquacrop_project_folder=aquacrop_project_folder,
           latitude=latitude,
           longitude=longitude,
           simulation_start=simulation_start,
           simulation_end=simulation_end,
           growing_season_start=growing_season_start,
           growing_season_end=growing_season_end,
           crop_ref=crop_file,
           crop_parameters_dict_new=crop_parameters_dict_new,
           fertility_stress=fertility_stress_value,
           soil_df=soil_df,
           swo_df=swo_df,
           gwt_depth=gwt_depth_scenarios,
           gwt_ec=gwt_ec_scenarios)

        df.to_csv(f'./RESULTS/{project_name_base}_soil{soil_n}_year{year}.csv')


