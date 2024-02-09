import pandas as pd


def get_crop_parameters_dict(cropfile_path='WheatGDD.CRO'):
    '''

    :param cropfile_path: sdsd
    :return: sdsdsd
    '''

    with open(cropfile_path) as f:
        lines = f.readlines()

    values = [i.strip().split(':', 1)[0].strip() for i in lines[1:]]
    parameters = [i.strip().split(':', 1)[1].strip() for i in lines[1:]]
    ser = pd.Series(data=values, index=parameters)

    return ser
