import pandas as pd


URL= "https://track.roedan.com/api/generate_report?user_api_hash=%242y%2410%241bRB9V2n0RIU2LmzQ8BUMelSOXIoUvh.SdCMCSnCMPPmyZDzBZA6S&lang=en&format=html&type=39&date_from=2022-06-17+00%3A00%3A00&date_to=2022-06-18+00%3A00%3A00&devices%5B0%5D=51&devices%5B1%5D=72&devices%5B2%5D=26&devices%5B3%5D=93&devices%5B4%5D=55&devices%5B5%5D=95&devices%5B6%5D=57&devices%5B7%5D=11&devices%5B8%5D=19&devices%5B9%5D=80&devices%5B10%5D=24&devices%5B11%5D=96&devices%5B12%5D=16&devices%5B13%5D=54&devices%5B14%5D=58&devices%5B15%5D=98&devices%5B16%5D=94&devices%5B17%5D=21&devices%5B18%5D=89&devices%5B19%5D=52&devices%5B20%5D=65&devices%5B21%5D=107&devices%5B22%5D=68&devices%5B23%5D=17&stops=300&send_to_email=&generate=1"


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
        tmp_df['locksmith'] = key
        df_list.append(tmp_df)
    return clean_report(pd.concat(df_list, ignore_index=True))

def clean_report(df):
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
    df['locksmith'] = df['locksmith'].str.lower().replace(r'wgtk[\s]*[\-]*[\s]*', '', regex=True).str.capitalize()
    return df

if __name__ == '__main__':
    df = get_full_response_table(URL)
    df = clean_report(df)
    df.to_csv('sample.csv', index=False)
    
    print(df.head())
    print(df['locksmith'].unique())
