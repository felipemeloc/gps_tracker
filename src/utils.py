import re
import pandas as pd

def clean_locksmith_name(col:pd.Series)->pd.Series:
    return col.str.lower().replace(r'wgtk[\s]*[\-]*', '', regex=True).str.replace(r'\(.*\)', '', regex=True).str.replace(r'[\s]+',' ',regex=True).str.strip().str.capitalize()

def fix_post_code_format(post_code:str)->str:
    post_code = re.sub(r'[^A-Z0-9]+', '', post_code.upper())
    return f'{post_code[:-3]} {post_code[-3:]}'

def clean_position(coord:tuple)->tuple:
    return tuple([float(item) for item in coord.split(',')])