# source: http://www.google.com/search?q=days+in+year
# source: http://www.google.com/search?q=days+in+month
DAYS_IN_YEAR = 365.242199
DAYS_IN_MONTH = 30.4368499

def days_to_years(days):
    """Converts the value of days into years floating point.

    >>> from decimal import Decimal
    >>> days_to_years(3829)
    10.483454569278836
    >>> days_to_years('3829')
    10.483454569278836
    >>> days_to_years(Decimal('3829'))
    10.483454569278836
    >>> days_to_years(-3829)
    >>> days_to_years('-3829')
    >>> days_to_years(Decimal('-3829'))
    >>> days_to_years(None)
    """
    if days is None:
        return
    days = float(str(days))
    if days < 0:
        return
    return days / DAYS_IN_YEAR

def days_to_age(days, min_years=3, to_string=True):
    """Converts the value of days into an age in years.

    >>> from decimal import Decimal
    >>> days_to_age(3829)
    '10y, 5m'
    >>> days_to_age('3829')
    '10y, 5m'
    >>> days_to_age(Decimal('3829'))
    '10y, 5m'
    >>> days_to_age(393)
    '12m'
    >>> days_to_age(3)
    'Newborn'
    >>> days_to_age(3829, min_years=11)
    '125m'
    >>> days_to_age(3829, to_string=False)
    10.483454569278836
    >>> days_to_age(-3829)
    >>> days_to_age('-3829')
    >>> days_to_age(Decimal('-3829'))
    >>> days_to_age(None)
    """
    if days is None:
        return
    # handles Decimal type
    days = float(str(days))
    if days < 0:
        return

    if not to_string:
        return days / DAYS_IN_YEAR

    if (days // DAYS_IN_YEAR) < min_years:
        mths = int(days // DAYS_IN_MONTH)
        if mths == 0:
            return 'Newborn'
        return '%sm' % mths

    yrs = int(days // DAYS_IN_YEAR)
    mths = int((days % DAYS_IN_YEAR) // DAYS_IN_MONTH)

    if mths > 0:
        return '%sy, %sm' % (yrs, mths)
    return '%sy' % yrs

def years_to_age(years, min_years=3, to_string=True):
    """Converts the value of years into an age in years.

    >>> from decimal import Decimal
    >>> years_to_age(7.2)
    '7y, 2m'
    >>> years_to_age('7.2')
    '7y, 2m'
    >>> years_to_age(Decimal('7.2'))
    '7y, 2m'
    >>> years_to_age(4.5, to_string=False)
    4.5
    >>> years_to_age(-7.2)
    >>> years_to_age('-7.2')
    >>> years_to_age(Decimal('-7.2'))
    >>> years_to_age(None)
    """
    if years is None:
        return
    days = float(str(years)) * DAYS_IN_YEAR
    if days < 0:
        return
    return days_to_age(days, min_years, to_string)

def dates_to_age(date1, date2, min_years=3, to_string=True):
    """Calculates an age in years based on two dates.

    >>> from datetime import datetime, date
    >>> dates_to_age(datetime(2002, 2, 14), datetime(2009, 5, 1))
    '7y, 2m'
    >>> dates_to_age(datetime(2009, 5, 1), datetime(2002, 2, 14))
    '7y, 2m'
    >>> dates_to_age(datetime(2002, 2, 14), None)
    >>> dates_to_age(None, datetime(2009, 5, 1))
    >>> dates_to_age(date(2002, 2, 14), date(2009, 5, 1))
    '7y, 2m'
    >>> dates_to_age(date(2009, 5, 1), date(2002, 2, 14))
    '7y, 2m'
    >>> dates_to_age(date(2002, 2, 14), None)
    >>> dates_to_age(None, date(2009, 5, 1))
    """
    if date1 is None or date2 is None:
        return
    if date1 > date2:
        date1, date2 = date2, date1
    days = (date2 - date1).days
    return days_to_age(days, min_years, to_string)
