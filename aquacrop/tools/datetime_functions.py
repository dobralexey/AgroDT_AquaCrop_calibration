def elapse_date(dt):
    if dt.month == 1:
        month_add = 0
    if dt.month == 2:
        month_add = 31
    if dt.month == 3:
        month_add = 59.25
    if dt.month == 4:
        month_add = 90.25
    if dt.month == 5:
        month_add = 120.25
    if dt.month == 6:
        month_add = 151.25
    if dt.month == 7:
        month_add = 181.25
    if dt.month == 8:
        month_add = 212.25
    if dt.month == 9:
        month_add = 243.25
    if dt.month == 10:
        month_add = 273.25
    if dt.month == 11:
        month_add = 304.25
    if dt.month == 12:
        month_add = 334.25

    elapse_date = int((dt.year - 1901) * 365.25 + month_add + dt.day)
    return elapse_date