# Import the datetime and dateutil modules
import datetime
import dateutil.relativedelta
from typing import Union


def get_date_with_duration(duration_in_years: Union[int, str]):
    """
    Returns a year in the past with the given duration in years
    e.g. if duration_in_years = 2 or 2 years ago, then the year returned will be 2 years in the past

    Parameters
    ----------
    duration_in_years: ``Union[int, str]``
        The duration in years for which the date is to be calculated

    Returns
    -------
    ``int``
        The year in the past with the given duration in years

    """
    if isinstance(duration_in_years, str):
        duration_in_years = int(duration_in_years.split(" ")[0])
        
    current_date = datetime.date.today()
    duration = dateutil.relativedelta.relativedelta(years=duration_in_years)
    past_date = current_date - duration
    
    return past_date.year


def duration_to_seconds(duration: str):
    """
    Returns the duration in seconds for the given duration

    Parameters
    ----------
    duration: ``str``
        The duration in the format HH:MM:SS or MM:SS or SS

    Returns
    -------
    ``int``
        The duration in seconds for the given duration
    """
    duration = duration.split(":")
    
    if len(duration) == 3:
        return int(duration[0]) * 3600 + int(duration[1]) * 60 + int(duration[2])
    elif len(duration) == 2:
        return int(duration[0]) * 60 + int(duration[1])
    else:
        return int(duration[0])
