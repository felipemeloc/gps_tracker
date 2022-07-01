import pandas as pd
import src.utils as utils


def read_api_response(url:str)->dict:
    df_list = pd.read_html(url)
    tables = {}
    next_good = False
    for item in df_list:
        if 'device' in item.iloc[0,0].lower():
            device= item.iloc[0,1]
            next_good= True
        elif next_good and item.columns[0] == 'Position A':
            tables[device]= item
            next_good = False            
    return tables

def get_full_response_table(url:str)->pd.DataFrame:
    df_dict = read_api_response(url)
    df_list = []
    for key, val in df_dict.items():
        tmp_df = val.copy()
        tmp_df['Locksmith'] = key
        df_list.append(tmp_df)
    return clean_report(pd.concat(df_list, ignore_index=True))

def clean_report(df:pd.DataFrame)->pd.DataFrame:
    rename_dict = {'Route length': 'Route length (Mi)',
                   'Average speed': 'Average speed (mph)',
                   'Top speed': 'Top speed (mph)'}
    df.rename(columns=rename_dict, inplace=True)
    for col in rename_dict.values():
        df[col] = df[col].str.replace('[a-zA-Z\s]', '', regex=True).astype(float)
    for col in ['Left', 'End', 'Departure time']:
        df[col] = pd.to_datetime(df[col])
    for col in ['Duration', 'Time at location']:
        df[col] = pd.to_timedelta(df[col])
    for col in ['Position A', 'Position B']:
        if col in df.columns:
            df[col+'_lat'] = df[col].apply(lambda x: x.split(',')[0]).astype(float)
            df[col+'_long'] = df[col].apply(lambda x: x.split(',')[-1]).astype(float)
            df.drop(columns=[col])
    df['Locksmith'] = utils.clean_locksmith_name(df['Locksmith'])
    return df[["Position A_lat",
                "Position A_long",
                "Left",
                "Duration",
                "Route length (Mi)",
                "Position B_lat",
                "Position B_long",
                "End",
                "Time at location",
                "Departure time",
                "Average speed (mph)",
                "Top speed (mph)",
                "Locksmith"]]