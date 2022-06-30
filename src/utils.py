"""utils.py

Contains the following functions:
* clean_locksmith_name: Ruturn a pd.Series base on a pd.Series
    the columns is form by locksmiths names, use:
        import utils
        utils.clean_locksmith_name(column = YOUR_DF['YOUR_COLUMN_NAME'])
        
* fix_post_code_format: Fix a postcode string in a valid form, use:
        import utils
        utils.fix_post_code_format(post_code = YOUR_POSTCODE)
        
* clean_position: Transform the string coordinates into a tuple
    of floats, use:
        import utils
        utils.clean_position(coord = YOUR_COORDINATE_STRING)
"""
import re
import pandas as pd

def clean_locksmith_name(column:pd.Series)->pd.Series:
    """Helper function to clean the locksmith name,
    this function gets rids of 'WGTK -' string or
    similar and anything with this format '(something)'.
    For example the text:
        'WGTK - Juan Smith (temp)(V8aj)'
    will be clean as
        'Juan smith'

    Args:
        col (pd.Series): Column with the records of locksmiths' names

    Returns:
        pd.Series: Column with the records of locksmiths' names after cleaning
    """    
    return column.str.lower(
        ).replace(
            r'wgtk[\s]*[\-]*', '', regex=True
        ).str.replace(
            r'\(.*\)', '', regex=True
        ).str.replace(
            r'[\s]+',' ',regex=True
        ).str.strip().str.capitalize()

def fix_post_code_format(post_code:str)->str:
    """Helper function to clean a string of a postcode.
    This function transforms the text to the format
    need by the Nominatim function to return the coordinates.

    Args:
        post_code (str): string of a postcode

    Returns:
        str: string of a cleaned postcode
    """    
    post_code = re.sub(r'[^A-Z0-9]+', '', post_code.upper())
    return f'{post_code[:-3]} {post_code[-3:]}'

def clean_position(coord:str)->tuple:
    """Helper function to transform the raw coordinates
    (string form) given by the Roedan API to a tuple of floats

    Args:
        coord (str): coordinates in string form

    Returns:
        tuple: coordinates
    """    
    return tuple([float(item) for item in coord.split(',')])