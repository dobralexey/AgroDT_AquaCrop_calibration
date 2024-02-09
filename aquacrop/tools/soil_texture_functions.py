import numpy as np
def soil_class_number(sat, fc, wp, ksat):
    if wp >= 20:
        if (sat > 49) and (fc >= 40):
            soil_class_number = 4
        else:
            soil_class_number = 3
    else:
        if (fc < 23):
            soil_class_number = 1
        else:
            if (wp > 16) and (ksat < 100):
                soil_class_number = 3
            else:
                if (wp < 6) and (fc < 28) and (ksat > 750):
                    soil_class_number = 1
                else:
                    soil_class_number = 2
    return soil_class_number

def soil_class_description(sat, fc, wp, ksat):
    if wp >= 20:
        if (sat > 49) and (fc >= 40):
            soil_class_description = 'silty clay soil'
        else:
            soil_class_description = 'sandy clay soil'
    else:
        if (fc < 23):
            soil_class_description = 'sandy soil'
        else:
            if (wp > 16) and (ksat < 100):
                soil_class_description = 'sandy clay soil'
            else:
                if (wp < 6) and (fc < 28) and (ksat > 750):
                    soil_class_description = 'sandy soil'
                else:
                    soil_class_description = 'loamy soil'
    return soil_class_description

def cr_a(soil_class_number, ksat):
    if soil_class_number == 1:
        a = -0.3112 - ksat/100000
    if soil_class_number == 2:
        a = -0.4986 + 9*ksat/100000
    if soil_class_number == 3:
        a = -0.5677 - 4*ksat/100000
    if soil_class_number == 4:
        a = -0.6366 + 8*ksat/10000

    return a


def cr_b(soil_class_number, ksat):
    if soil_class_number == 1:
        b = -1.4936 + 0.2416 * np.log(ksat)
    if soil_class_number == 2:
        b = -2.1320 + 0.4778 * np.log(ksat)
    if soil_class_number == 3:
        b = -3.7189 + 0.5922 * np.log(ksat)
    if soil_class_number == 4:
        b = -1.9165 + 0.7063 * np.log(ksat)

    return b

def rew_calc(fc, air, ze=0.04):
    rew = round(1000*(fc/100 - air/100)*ze)
    if rew < 0:
        rew = 0
    if rew > 15:
        rew = 15
    return rew

def curve_number_calc(ksat):
    if ksat > 864:
        cn = 46
    if 347 <= ksat <= 864:
        cn = 61
    if 36 <= ksat <= 346:
        cn = 72
    if ksat <= 35:
        cn = 77
    return cn