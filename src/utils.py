import pandas as pd

def clean_locksmith_name(col:pd.Series)->pd.Series:
    return col.str.lower().replace(r'wgtk[\s]*[\-]*', '', regex=True).str.replace(r'\(.*\)', '', regex=True).str.replace(r'[\s]+',' ',regex=True).str.strip().str.capitalize()