import os
import pandas as pd
from aquacrop.run.aquacrop_run_variety_calibration import aquacrop_run_variety_calibration

#----USER DEFINED PARAMETERS----
aquacrop_all_projects_folder = 'C:/Users/user/PycharmProjects/AgroDT_AquaCrop_calibration/aquacrop/main/projects/'
project_name_base = 'default_project'

latitude = 59.425032                                                               #Latitude in degrees (from -90 to 90)
longitude = 30.031902                                                              #Longitude in degrees (from -180 to 180)

yield_measured = [2.6, 2.5, 2.1, 2.7, 2.9]                                         #Yield measured for calibration
simulation_starts = [20100401, 20110401, 20120401, 20130401, 20140401]             #Simulation start dates list (yyyymmdd)
simulation_ends = [20100901, 20110901, 20120901, 20130901, 20140901]               #Simulation end dates list (yyyymmdd)
growing_season_starts = [20100501, 20110501, 20120501, 20130501, 20140501]         #Onset of the growing period (yyyymmdd)
growing_season_ends = [20100825, 20110825, 20120825, 20130825, 20140825]           #End of the growing period (yyyymmdd)
# crop_list = os.listdir('./CROPS')
crop_ref = 'Canola.CRO'                                                            #Reference crop

crop_parameters_dict_new = {'Number of plants per hectare': 2000000,
                            'Calendar Days: from sowing to emergence': 10,
                            'Calendar Days: from sowing to maximum rooting depth': 59,
                            'Calendar Days: from sowing to start senescence': 97,
                            'Calendar Days: from sowing to maturity (length of crop cycle)': 116,
                            'Calendar Days: from sowing to flowering': 54,
                            'Length of the flowering stage (days)': 19,
                            'Building up of Harvest Index starting at flowering (days)': 51,
                            'Minimum effective rooting depth (m)': 0.3,
                            'Maximum effective rooting depth (m)': 2.0
                            }

#Soil constants (up to 5 layers!)
soil_df = pd.DataFrame({'horizon_number': [1, 2, 3, 4, 5],
                        'thickness': [0.50, 0.50, 0.50, 0.50, 0.50],
                        'sat': [46.0, 46.0, 46.0, 46.0, 46.0],
                        'fc': [29.0, 29.0, 29.0, 29.0, 29.0],
                        'wp': [13.0, 13.0, 13.0, 13.0, 13.0],
                        'ksat': [1200.0, 1200.0, 1200.0, 1200.0, 1200.0],
                        'penetrability': [100, 100, 100, 100, 100],
                        'gravel': [0, 0, 0, 0, 0]})


#Set Initial soil water content for each year (simulation start dates)
swo_dfs = [pd.DataFrame({'horizon_number': [1, 2, 3, 4, 5], 'thickness': [0.50, 0.50, 0.50, 0.50, 0.50], 'wc': [29.00, 15.00, 10.00, 10.00, 10.00], 'ec': [0.00, 0.00, 0.00, 0.00, 0.00]}),
           pd.DataFrame({'horizon_number': [1, 2, 3, 4, 5], 'thickness': [0.50, 0.50, 0.50, 0.50, 0.50], 'wc': [29.00, 15.00, 10.00, 10.00, 10.00], 'ec': [0.00, 0.00, 0.00, 0.00, 0.00]}),
           pd.DataFrame({'horizon_number': [1, 2, 3, 4, 5], 'thickness': [0.50, 0.50, 0.50, 0.50, 0.50], 'wc': [29.00, 15.00, 10.00, 10.00, 10.00], 'ec': [0.00, 0.00, 0.00, 0.00, 0.00]}),
           pd.DataFrame({'horizon_number': [1, 2, 3, 4, 5], 'thickness': [0.50, 0.50, 0.50, 0.50, 0.50], 'wc': [29.00, 15.00, 10.00, 10.00, 10.00], 'ec': [0.00, 0.00, 0.00, 0.00, 0.00]}),
           pd.DataFrame({'horizon_number': [1, 2, 3, 4, 5], 'thickness': [0.50, 0.50, 0.50, 0.50, 0.50], 'wc': [29.00, 15.00, 10.00, 10.00, 10.00], 'ec': [0.00, 0.00, 0.00, 0.00, 0.00]})]


#----DEFAULT PARAMETERS----

fertility_stress_range = [1,75]
gwt_depth = 10
gwt_ec = 0
N = 2
parameters_for_calibration = ['Soil water depletion factor for canopy expansion (p-exp) - Upper threshold',
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
                              'Reference Harvest Index (HIo) (%)']
crop_parameters_rounds = [2, 2, 1, 2, 1, 2, 1, 2, None, 5, 5, None]
range_percent = 10


#------MAIN CODE-------
aquacrop_project_folder = os.path.join(aquacrop_all_projects_folder, project_name_base)
crop_parameters_result, error = aquacrop_run_variety_calibration(project_name_base=project_name_base,
                                                                 aquacrop_project_folder=aquacrop_project_folder,
                                                                 latitude=latitude,
                                                                 longitude=longitude,
                                                                 yield_measured=yield_measured,
                                                                 simulation_starts=simulation_starts,
                                                                 simulation_ends=simulation_ends,
                                                                 growing_season_starts=growing_season_starts,
                                                                 growing_season_ends=growing_season_ends,
                                                                 crop_ref=crop_ref,
                                                                 crop_parameters_dict_new=crop_parameters_dict_new,
                                                                 fertility_stress_range=fertility_stress_range,
                                                                 parameters_for_calibration=parameters_for_calibration,
                                                                 crop_parameters_rounds=crop_parameters_rounds,
                                                                 range_percent=range_percent,
                                                                 soil_df=soil_df,
                                                                 swo_dfs=swo_dfs,
                                                                 gwt_depth=gwt_depth,
                                                                 gwt_ec=gwt_ec,
                                                                 N=N)