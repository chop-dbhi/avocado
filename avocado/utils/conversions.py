# source: google.com calculator
DAYS_IN_YEAR = 365.242199
DAYS_IN_MONTH = 30.4368499

def days_to_age(value):
    "Converts the value of days into an age."
    if value is None:
        return
    # convert to string before float in case of Decimal
    flt = float(str(value))
    
    if flt // DAYS_IN_YEAR < 3:
        mths = int(flt // DAYS_IN_MONTH)
        if mths == 0:
            return 'Newborn'
        return '%sm' % mths

    yrs = int(flt // DAYS_IN_YEAR)
    mths = int((flt % DAYS_IN_YEAR) // DAYS_IN_MONTH)
    
    if mths > 0:
        return '%sy, %sm' % (yrs, mths)
    return '%sy' % yrs

def years_to_age(value):
    "Converts the value of years into an age."
    if value is None:
        return
    flt = float(str(value)) * DAYS_IN_YEAR
    return days_to_age(flt)

def dates_to_age(date1, date2):
    "Calculates an age based on two dates"
    if date1 is None or date2 is None:
        return
    if date1 > date2:
        date1, date2 = date2, date1
    days = (date2 - date1).days
    return days_to_age(days)