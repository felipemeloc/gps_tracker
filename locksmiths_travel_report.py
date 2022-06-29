import os
import src.db as db
import pandas as pd
import dataframe_image as dfi
from src.utils import clean_locksmith_name
from travel_sheet_report import generate_reports
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
# Define project main path
MAIN_FOLDER = os.getenv('MAIN_PATH')

csv_path = os.path.join(MAIN_FOLDER, 'csv')

image_path = os.path.join(MAIN_FOLDER, 'images/test.png')

################################## Query Load #####################################

query_path = os.path.join(MAIN_FOLDER, 'queries')

TS_completed_jobs_by_locksmith = open(os.path.join(query_path,
                    'TS_completed_jobs_by_locksmith.sql'), 'r').read()

def get_completed_locksmith_report():
    average_stat = pd.read_csv(os.path.join(csv_path, 'average_stat.csv'))
    
    completed_jobs = db.sql_to_df(TS_completed_jobs_by_locksmith)
    if not completed_jobs.empty:
        completed_jobs['Locksmith'] = clean_locksmith_name(completed_jobs['Locksmith'])
        completed_jobs = completed_jobs.groupby('Locksmith', as_index=False).sum()
        report = completed_jobs.merge(average_stat, on='Locksmith', how='left')
        report['£ per mile'] = report['Revenue'] / report['Miles covered']
        return report.sort_values(['Revenue', 'Jobs'], ascending=False)
    else:
        return pd.DataFrame()

def df_to_image(df, image_path):
    df_style = df.style.format({"Revenue": "£{}"},
                            na_rep=" ", precision=2
                    ).hide_index(
                    # ).set_caption("Locksmith Jobs completed summary"
                    ).set_table_styles(
                        [{'selector': 'th.col_heading',
                        'props': 'text-align: center;'},
                        {'selector': 'td', 
                        'props': 'text-align: center; font-family: " Quicksand";'},
                        {'selector': 'th:not(.index_name)',
                        'props': 'background-color: #023858; color: white;'},#first headers background color. Second headers font color
                        {'selector': 'td', 
                        'props': [
                            ('border-style','solid'), ('border-color', 'white'),#grid color
                            ('border-width','1px')
                            ]}
                        ]
                    ).set_properties(
                        **{'background-color': '#b4c4df'}# table background color
                    )
                            #.bar(subset=['£ per mile'], color='#d65f5f')
    dfi.export(df_style, image_path)

if __name__ == '__main__' :
    generate_reports()
    report = get_completed_locksmith_report()
    if os.path.exists(image_path):
        os.remove(image_path)
    if not report.empty:
        df_to_image(report, image_path)
    print(report)
