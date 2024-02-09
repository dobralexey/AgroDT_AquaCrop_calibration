import numpy as np
from rosetta import rosetta, SoilData

def rosetta_soil_model(soil_df, soil_texture='loamy sand', penetrability=100, gravel=0):

    data = np.array(soil_df.iloc[:, 1:])
    mean, stdev, codes = rosetta(3, SoilData.from_array(data))

    Qr = mean[:, 0]
    Qs = mean[:, 1]
    log10a = mean[:, 2]
    a = 10**log10a
    log10n = mean[:, 3]
    n = 10**log10n
    m = 1 - 1/n
    log10ksat = mean[:, 4]
    ksat = 10**log10ksat
    ksat_mm = 10* ksat

    if (soil_texture == 'sand') or (soil_texture == 'loamy sand'):
        h_fc = 101.972
    else:
        h_fc = 305.915
    h_wp = 15295.7

    Qfc = Qr + (Qs - Qr)/((1+(a*h_fc)**n)**m)
    Qwp = Qr + (Qs - Qr)/((1+(a*h_wp)**n)**m)

    soil_df['horizon_number'] = soil_df.index + 1
    soil_df['thickness'] = (soil_df['Depth'].apply(lambda x: int(x.split('-')[1]) - int(x.split('-')[0])))/100
    soil_df['sat'] = Qs * 100
    soil_df['fc'] = Qfc * 100
    soil_df['wp'] = Qwp * 100
    soil_df['ksat'] = ksat_mm
    soil_df['penetrability'] = penetrability
    soil_df['gravel'] = gravel

    soil_df['sat'] = soil_df['sat'].apply(lambda x: int(x))
    soil_df['fc'] = soil_df['fc'].apply(lambda x: int(x))
    soil_df['wp'] = soil_df['wp'].apply(lambda x: int(x))
    soil_df_const = soil_df[['horizon_number', 'thickness', 'sat', 'fc', 'wp', 'ksat', 'penetrability', 'gravel']]

    return soil_df_const

