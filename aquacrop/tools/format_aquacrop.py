import os
import pandas as pd
from datetime import datetime
from aquacrop.tools.datetime_functions import elapse_date
from aquacrop.tools.soil_texture_functions import (soil_class_number,
                                                   soil_class_description,
                                                   cr_a,
                                                   cr_b,
                                                   curve_number_calc,
                                                   rew_calc)

def create_aquacrop_meteo_files(project_name, meteo_csvfile_path, meteo_files_folder):
    '''

    :param project_name:
    :param meteo_csvfile_path:
    :param meteo_files_folder:
    :return:
    '''

    df = pd.read_csv(meteo_csvfile_path, index_col=0)
    df.index = pd.to_datetime(df.index, format='%Y%m%d')

    start_day = df.index[0].day
    start_month = df.index[0].month
    start_year = df.index[0].year

    # CLIMATE
    climate_file = f'{project_name}.CLI'
    climate_file_path = os.path.join(meteo_files_folder, climate_file)
    with open(climate_file_path, 'w') as f:
        f.write(f'{project_name}\n')
        f.write(' 7.1   : AquaCrop Version (August 2023)\n')
        f.write(f'{project_name}.Tnx\n')
        f.write(f'{project_name}.ETo\n')
        f.write(f'{project_name}.PLU\n')
        f.write(f'MaunaLoa.CO2')

    # TEMPERATURE
    temperature_file = f'{project_name}.Tnx'
    temperature_file_path = os.path.join(meteo_files_folder, temperature_file)
    df['Tn_str'] = df['Tn'].apply(lambda x: str(round(x, 1)))
    df['Tx_str'] = df['Tx'].apply(lambda x: str(round(x, 1)))
    df['Tnx_str'] = df['Tn_str'] + '\t' + df['Tx_str'] + '\n'
    with open(temperature_file_path, 'w') as f:
        f.write(f'{project_name}\n')
        f.write(f'     1  : Daily records (1=daily, 2=10-daily and 3=monthly data)\n')
        f.write(f'     {start_day}  : First day of record (1, 11 or 21 for 10-day or 1 for months)\n')
        f.write(f'     {start_month}  : First month of record\n')
        f.write(f'  {start_year}  : First year of record (1901 if not linked to a specific year))\n')
        f.write('\n')
        f.write('  Tmin (C)   TMax (C)\n')
        f.write('=======================\n')
        f.writelines(df['Tnx_str'])

    # PRECIPITATION (RAIN)
    rain_file = f'{project_name}.PLU'
    rain_file_path = os.path.join(meteo_files_folder, rain_file)
    df['Pr_str'] = df['Pr'].apply(lambda x: str(round(x, 1)) + '\n')
    with open(rain_file_path, 'w') as f:
        f.write(f'{project_name}\n')
        f.write(f'     1  : Daily records (1=daily, 2=10-daily and 3=monthly data)\n')
        f.write(f'     {start_day}  : First day of record (1, 11 or 21 for 10-day or 1 for months)\n')
        f.write(f'     {start_month}  : First month of record\n')
        f.write(f'  {start_year}  : First year of record (1901 if not linked to a specific year))\n')
        f.write('\n')
        f.write('  Total Rain (mm) \n')
        f.write('======================= \n')
        f.writelines(df['Pr_str'])

    # ET0
    eto_file = f'{project_name}.ETo'
    eto_file_path = os.path.join(meteo_files_folder, eto_file)
    df['ET0_str'] = df['ET0'].apply(lambda x: str(round(x, 1)) + '\n')
    with open(eto_file_path, 'w') as f:
        f.write(f'{project_name}\n')
        f.write(f'     1  : Daily records (1=daily, 2=10-daily and 3=monthly data)\n')
        f.write(f'     {start_day}  : First day of record (1, 11 or 21 for 10-day or 1 for months)\n')
        f.write(f'     {start_month}  : First month of record\n')
        f.write(f'  {start_year}  : First year of record (1901 if not linked to a specific year))\n')
        f.write('\n')
        f.write('  Average ETo (mm/day) \n')
        f.write('======================= \n')
        f.writelines(df['ET0_str'])

    return climate_file, temperature_file, rain_file, eto_file

def create_aquacrop_calendar_file(project_name, growing_season_start, calendar_file_folder):
    '''
    Fucntion to create AquaCrop calendar file
    :param project_name:
    :param growing_season_start:
    :param data_path:
    :return: calendar file name
    '''
    growing_season_start_dt = datetime.strptime(str(growing_season_start), '%Y%m%d')
    growing_season_start_doy = growing_season_start_dt.strftime('%j')

    calendar_file = f'{project_name}.CAL'
    calendar_file_path = os.path.join(calendar_file_folder, calendar_file)

    with open(calendar_file_path, 'w') as f:
        f.write(f'{project_name}\n')
        f.write('         7.1  : AquaCrop Version (August 2023)\n')
        f.write('         0    : The onset of the growing period is fixed on a specific date\n')
        f.write('        -9    : Day-number (1 ... 366) of the Start of the time window for the onset criterion: Not applicable\n')
        f.write('        -9    : Length (days) of the time window for the onset criterion: Not applicable\n')
        f.write(f'       {growing_season_start_doy}    : Day-number (1 ... 366) for the onset of the growing period\n')
        f.write('        -9    : Number of successive days: Not applicable\n')
        f.write('        -9    : Number of occurrences: Not applicable')

    return calendar_file


def modify_aquacrop_crop_file(project_name, crop_parameters_dict_new, crop_file_folder,
                         crop_ref_folder, crop_ref='Canola.CRO'):
    '''

    :param project_name:
    :param crop_parameters_dict_new:
    :param crop_file_folder:
    :param crop_ref_folder:
    :param crop_ref:
    :return:
    '''

    crop_ref_path = os.path.join(crop_ref_folder, crop_ref)
    with open(crop_ref_path) as f:
        lines = f.readlines()

    values = [i.strip().split(':', 1)[0].strip() for i in lines[1:]]
    parameters = [i.strip().split(':', 1)[1].strip() for i in lines[1:]]

    ser = pd.Series(data=values, index=parameters)
    ser.update(crop_parameters_dict_new)

    crop_file = f'{project_name}_{crop_ref}'
    crop_file_path = os.path.join(crop_file_folder, crop_file)

    with open(crop_file_path, 'w') as f:
        f.write(f'{project_name}\n')
        for k, v in ser.items():
            v_modify = '  ' + str(v)
            v_modify = v_modify + ' ' * (15 - len(v_modify))
            f.write(f'{v_modify}: {k}\n')

    return crop_file

def modify_aquacrop_crop_file_after_calibration(project_name, crop_parameters_dict_new, crop_file_folder,
                         crop_ref_folder, crop_ref='Canola.CRO'):
    '''

    :param project_name:
    :param crop_parameters_dict_new:
    :param crop_file_folder:
    :param crop_ref_folder:
    :param crop_ref:
    :return:
    '''

    crop_ref_path = os.path.join(crop_ref_folder, crop_ref)
    with open(crop_ref_path) as f:
        lines = f.readlines()

    values = [i.strip().split(':', 1)[0].strip() for i in lines[1:]]
    parameters = [i.strip().split(':', 1)[1].strip() for i in lines[1:]]

    ser = pd.Series(data=values, index=parameters)
    ser.update(crop_parameters_dict_new)

    crop_file = f'{project_name}{crop_ref}'
    crop_file_path = os.path.join(crop_file_folder, crop_file)

    with open(crop_file_path, 'w') as f:
        f.write(f'{project_name}\n')
        for k, v in ser.items():
            v_modify = '  ' + str(v)
            v_modify = v_modify + ' ' * (15 - len(v_modify))
            f.write(f'{v_modify}: {k}\n')

    return crop_file


def modify_aquacrop_fertility_management_file(project_name, management_file_folder, management_ref='Default.MAN', fertility_stress=0):
    '''

    :param project_name:
    :param management_file_folder:
    :param management_ref:
    :param fertility_stress:
    :return:
    '''

    management_ref_path = os.path.join(management_file_folder, management_ref)
    with open(management_ref_path) as f:
        lines = f.readlines()

    if len(str(fertility_stress)) > 1:
        lines[4] = lines[4].replace(' 0', str(fertility_stress))
    else:
        lines[4] = lines[4].replace('0', str(fertility_stress))

    management_file = f'{project_name}.MAN'
    management_file_path = os.path.join(management_file_folder, management_file)
    with open(management_file_path, 'w') as f:
        f.writelines(lines)

    return management_file

def create_aquacrop_soil_file(project_name, soil_file_folder, soil_df):
    '''
    :param soil_df:
    :param project_name:
    :param soilfile_folder:
    :return: soilfile_path
    '''
    horizons_number = len(soil_df)
    rew = rew_calc(fc=soil_df['fc'].iloc[0], air=soil_df['wp'].iloc[0] / 2)
    curve_number = curve_number_calc(ksat=soil_df['ksat'].iloc[0])

    soil_df['soil_class_number'] = soil_df.apply(lambda x: soil_class_number(x.sat, x.fc, x.wp, x.ksat), axis=1)
    soil_df['soil_class_description'] = soil_df.apply(lambda x: soil_class_description(x.sat, x.fc, x.wp, x.ksat), axis=1)
    soil_df['cr_a'] = soil_df.apply(lambda x: cr_a(x.soil_class_number, x.ksat), axis=1)
    soil_df['cr_b'] = soil_df.apply(lambda x: cr_b(x.soil_class_number, x.ksat), axis=1)

    soil_file = f'{project_name}.SOL'
    soil_file_path = os.path.join(soil_file_folder, soil_file)

    with open(soil_file_path, 'w') as f:
        f.write(f'{project_name}\n')
        f.write(f'        7.1                 : AquaCrop Version (August 2023)\n')
        f.write(f'       {curve_number}                   : CN (Curve Number)\n')
        f.write(f'        {rew}                   : Readily evaporable water from top layer (mm)\n')
        f.write(f'        {horizons_number}                   : number of soil horizons\n')
        f.write(f'       -9                   : variable no longer applicable\n')
        f.write('  Thickness  Sat   FC    WP     Ksat   Penetrability  Gravel  CRa       CRb           description\n')
        f.write(
            '  ---(m)-   ----(vol %)-----  (mm/day)      (%)        (%)    -----------------------------------------\n')

        for i in range(len(soil_df)):
            thickness_i = round(soil_df['thickness'].iloc[i], 2)
            sat_i = round(soil_df['sat'].iloc[i], 1)
            fc_i = round(soil_df['fc'].iloc[i], 1)
            wp_i = round(soil_df['wp'].iloc[i], 1)
            ksat_i = round(soil_df['ksat'].iloc[i], 1)
            penetrability_i = round(soil_df['penetrability'].iloc[i])
            gravel_i = round(soil_df['gravel'].iloc[i])
            cr_a_i = round(soil_df['cr_a'].iloc[i], 6)
            cr_b_i = round(soil_df['cr_b'].iloc[i], 6)
            soil_class_description_i = soil_df['soil_class_description'].iloc[i]
            f.write(f'    {thickness_i:.2f}    {sat_i:.1f}  {fc_i:.1f}  {wp_i:.1f}  {ksat_i:.1f}        {penetrability_i:.0f}         {gravel_i:.0f}     {cr_a_i:.6f}  {cr_b_i:.6f}   {soil_class_description_i}\n')

    return soil_file

def create_aquacrop_gwt_file(project_name, gwt_file_folder, depth=2, ec=0):

    gwt_file = f'{project_name}.GWT'
    gwt_file_path = os.path.join(gwt_file_folder, gwt_file)

    with open(gwt_file_path, 'w') as f:
        f.write(f'{project_name}\n')
        f.write(f'     7.1   : AquaCrop Version (August 2023)\n')
        f.write(f'     1     : groundwater table at fixed depth and with constant salinity\n')
        f.write(f'\n')
        f.write(f'   Day    Depth (m)    ECw (dS/m)\n')
        f.write(f'====================================\n')
        f.write(f'     1      {depth:.2f}          {ec:.1f}')

    return gwt_file

def create_aquacrop_swo_file(project_name, swo_file_folder, swo_df):
    '''

    :param project_name:
    :param swo_file_folder:
    :param swo_df:
    :return:
    '''
    horizons_number = len(swo_df)

    swo_file = f'{project_name}.SW0'
    swo_file_path = os.path.join(swo_file_folder, swo_file)

    with open(swo_file_path, 'w') as f:
        f.write(f'{project_name}\n')
        f.write(f'    7.1   : AquaCrop Version (August 2023)\n')
        f.write(f'   -9.00  : initial canopy cover that can be reached without water stress will be used as default\n')
        f.write(f'    0.000 : biomass (ton/ha) produced before the start of the simulation period\n')
        f.write(f'   -9.00  : initial effective rooting depth that can be reached without water stress will be used as default\n')
        f.write(f'    0.0   : water layer (mm) stored between soil bunds (if present)\n')
        f.write(f'    0.00  : electrical conductivity (dS/m) of water layer stored between soil bunds (if present)\n')
        f.write(f'    0     : soil water content specified for specific layers\n')
        f.write(f'    {horizons_number}     : number of layers considered\n')
        f.write(f'\n')
        f.write(f'Thickness layer (m)     Water content (vol%)     ECe(dS/m)\n')
        f.write(f'==============================================================\n')
        for i in range(len(swo_df)):
            thickness_i = round(swo_df['thickness'].iloc[i], 2)
            wc_i = round(swo_df['wc'].iloc[i], 2)
            ec_i = round(swo_df['ec'].iloc[i], 2)
            f.write(f'         {thickness_i:.2f}                {wc_i:.2f}                  {ec_i:.2f}\n')

    return swo_file

def create_aquacrop_project_file(simulation_start, simulation_end, growing_season_start, growing_season_end,
                                 project_name, climate_file, temperature_file, rain_file, eto_file, calendar_file,
                                 crop_file, management_file, soil_file, gwt_file, swo_file, project_file_folder,
                                 aquacrop_data_path_folder, aquacrop_simul_path_folder):
    '''

    :param simulation_start:
    :param simulation_end:
    :param growing_season_start:
    :param growing_season_end:
    :param project_name:
    :param climate_file:
    :param temperature_file:
    :param eto_file:
    :param rain_file:
    :param calendar_file:
    :param crop_file:
    :param management_file:
    :param soil_file:
    :param gwt_file:
    :param swo_file:
    :param aquacrop_data_path:
    :param aquacrop_simul_path:
    :param aquacrop_project_file_folder:
    :return:
    '''

    simulation_start_dt = pd.to_datetime(simulation_start, format='%Y%m%d')
    simulation_end_dt = pd.to_datetime(simulation_end, format='%Y%m%d')
    growing_season_start_dt = pd.to_datetime(growing_season_start, format='%Y%m%d')
    growing_season_end_dt = pd.to_datetime(growing_season_end, format='%Y%m%d')

    simulation_start_elapse = elapse_date(simulation_start_dt)
    simulation_end_elapse = elapse_date(simulation_end_dt)
    growing_season_start_elapse = elapse_date(growing_season_start_dt)
    growing_season_end_elapse = elapse_date(growing_season_end_dt)

    project_file = f'{project_name}.PRO'
    project_file_path = os.path.join(project_file_folder, project_file)


    with open(project_file_path, 'w') as f:
        f.write(f'{project_name}\n')
        f.write(f'      7.1       : AquaCrop Version (August 2023)\n')
        f.write(f'      1         : Year number of cultivation (Seeding/planting year)\n')
        f.write(f'  {simulation_start_elapse}         : First day of simulation period   \n')
        f.write(f'  {simulation_end_elapse}         : Last day of simulation period\n')
        f.write(f'  {growing_season_start_elapse}         : First day of cropping period \n')
        f.write(f'  {growing_season_end_elapse}         : Last day of cropping period \n')
        f.write(f'-- 1. Climate (CLI) file\n')
        f.write(f'   {climate_file}\n')
        f.write(f"   '{aquacrop_data_path_folder}'\n")
        f.write(f'   1.1 Temperature (Tnx or TMP) file\n')
        f.write(f'   {temperature_file}\n')
        f.write(f"   '{aquacrop_data_path_folder}'\n")
        f.write(f'   1.2 Reference ET (ETo) file\n')
        f.write(f'   {eto_file}\n')
        f.write(f"   '{aquacrop_data_path_folder}'\n")
        f.write(f'   1.3 Rain (PLU) file\n')
        f.write(f'   {rain_file}\n')
        f.write(f"   '{aquacrop_data_path_folder}'\n")
        f.write(f'   1.4 Atmospheric CO2 concentration (CO2) file\n')
        f.write(f'   MaunaLoa.CO2\n')
        f.write(f"   '{aquacrop_simul_path_folder}'\n")
        f.write(f'-- 2. Calendar (CAL) file\n')
        f.write(f'   {calendar_file}\n')
        f.write(f"   '{aquacrop_data_path_folder}'\n")
        f.write(f'-- 3. Crop (CRO) file\n')
        f.write(f'   {crop_file}\n')
        f.write(f"   '{aquacrop_data_path_folder}'\n")
        f.write(f'-- 4. Irrigation management (IRR) file\n')
        f.write(f'   (None)\n')
        f.write(f'   (None)\n')
        f.write(f'-- 5. Field management (MAN) file\n')
        f.write(f'   {management_file}\n')
        f.write(f"   '{aquacrop_data_path_folder}'\n")
        f.write(f'-- 6. Soil profile (SOL) file\n')
        f.write(f'   {soil_file}\n')
        f.write(f"   '{aquacrop_data_path_folder}'\n")
        f.write(f'-- 7. Groundwater table (GWT) file\n')
        f.write(f'   {gwt_file}\n')
        f.write(f"   '{aquacrop_data_path_folder}'\n")
        f.write(f'-- 8. Initial conditions (SW0) file\n')
        f.write(f'   {swo_file}\n')
        f.write(f"   '{aquacrop_data_path_folder}'\n")
        f.write(f'-- 9. Off-season conditions (OFF) file\n')
        f.write(f'   (None)\n')
        f.write(f'   (None)\n')
        f.write(f'-- 10. Field data (OBS) file\n')
        f.write(f'   (None)\n')
        f.write(f'   (None)\n')


    return project_file

def create_aquacrop_parameters_file(aquacrop_parameters_file_folder, project_name):

    parameters_file = f'{project_name}.PP1'
    parameters_file_path = os.path.join(aquacrop_parameters_file_folder, parameters_file)

    with open(parameters_file_path, 'w') as f:
        f.write(f'      4         : Evaporation decline factor for stage II\n')
        f.write(f'      1.10      : Ke(x) Soil evaporation coefficient for fully wet and non-shaded soil surface\n')
        f.write(f'      5         : Threshold for green CC below which HI can no longer increase (% cover)\n')
        f.write(f'     70         : Starting depth of root zone expansion curve (% of Zmin)\n')
        f.write(f'      5.00      : Maximum allowable root zone expansion (fixed at 5 cm/day)\n')
        f.write(f'     -6         : Shape factor for effect water stress on root zone expansion\n')
        f.write(f'     20         : Required soil water content in top soil for germination (% TAW)\n')
        f.write(f'      1.0       : Adjustment factor for FAO-adjustment soil water depletion (p) by ETo\n')
        f.write(f'      3         : Number of days after which deficient aeration is fully effective\n')
        f.write(f'      1.00      : Exponent of senescence factor adjusting drop in photosynthetic activity of dying crop\n')
        f.write(f'     12         : Decrease of p(sen) once early canopy senescence is triggered (% of p(sen))\n')
        f.write(f'     10         : Thickness top soil (cm) in which soil water depletion has to be determined\n')
        f.write(f'     30         : Depth [cm] of soil profile affected by water extraction by soil evaporation\n')
        f.write(f'      0.30      : Considered depth (m) of soil profile for calculation of mean soil water content for CN adjustment\n')
        f.write(f'      1         : CN is adjusted to Antecedent Moisture Class\n')
        f.write(f'     20         : Salt diffusion factor (capacity for salt diffusion in micro pores) [%]\n')
        f.write(f'    100         : Salt solubility [g/liter]\n')
        f.write(f'     16         : Shape factor for effect of soil water content gradient on capillary rise\n')
        f.write(f'     12.0       : Default minimum temperature (°C) if no temperature file is specified\n')
        f.write(f'     28.0       : Default maximum temperature (°C) if no temperature file is specified\n')
        f.write(f'      3         : Default method for the calculation of growing degree days\n')
        f.write(f'      1         : Daily rainfall is estimated by USDA-SCS procedure (when input is 10-day/monthly rainfall)\n')
        f.write(f'     70         : Percentage of effective rainfall (when input is 10-day/monthly rainfall)\n')
        f.write(f'      2         : Number of showers in a decade for run-off estimate (when input is 10-day/monthly rainfall)\n')
        f.write(f'      5         : Parameter for reduction of soil evaporation (when input is 10-day/monthly rainfall)\n')

    return parameters_file

def create_aquacrop_project_list(aquacrop_project_file_folder, project_list):
    '''
    :param aquacrop_project_file_folder:
    :param projects_list:
    :return:
    '''
    projects_list_name = 'ListProjects.txt'
    aquacrop_project_list_path = os.path.join(aquacrop_project_file_folder, projects_list_name)
    with open(aquacrop_project_list_path, 'w') as f:
        for project in project_list:
            f.write(f'{project}\n')

    return projects_list_name


def aquacrop_daily_out_to_csv_df(aquacrop_project_out_file_folder, aquacrop_project_out_csvfile_folder, project_name, csv_write=True):
    '''

    :param aquacrop_project_out_file_folder:
    :param project_name:
    :return:

    Variables names in Chapter 2 AquaCrop Reference Manual (p. 371 - 382)
    '''

    daily_out_file = f'{project_name}PROday.OUT'
    season_out_file = f'{project_name}PROseason.OUT'
    daily_out_file_path = os.path.join(aquacrop_project_out_file_folder, daily_out_file)

    df = pd.read_fwf(daily_out_file_path, skiprows=[0, 1, 3])
    df = df.loc[:, ~df.columns.str.replace("(\.\d+)$", "").duplicated()]
    if csv_write:
        daily_csv_file = f'{project_name}PROday.csv'
        daily_csv_file_path = os.path.join(aquacrop_project_out_csvfile_folder, daily_csv_file)
        df.to_csv(daily_csv_file_path)

    return daily_out_file, season_out_file, df
