"""bd.py
This is a custom module to get a DataFrame based on a SQL query
This module needs the installation of the following packages:
* os: For path management and directory creation
* pyodbc: Create the database connection
* pandas: return a DataFrame object
* warnings: Ignore the warning to have a cleaner terminal
* dotenv: load environment variables
Contains the following function:
* sql_to_df: Return a DataFrame base on a SQLquery. use:
    import db
    db.sql_to_df(query)
"""

import os
import pyodbc
import urllib
import pandas as pd
import warnings
import sqlalchemy as sa
from dotenv import load_dotenv

load_dotenv()
warnings.filterwarnings("ignore")

def get_conn(use_live=True)->pyodbc.Connection:
    """Function to make the connection with sql management studio

    Args:
        use_live (bool): Use or not the live database

    Returns:
        pyodbc.Connection: Database connection
    """
    if use_live:
        SERVER = os.getenv('SERVER')
        DATABASE = os.getenv('DATABASE')
        USER_NAME = os.getenv('USER_NAME')
        PASSWORD = os.getenv('DATABASE_PASSWORD')
    else:
        SERVER = os.getenv('SERVER_JASPER')
        DATABASE = os.getenv('DATABASE_JASPER')
        USER_NAME = os.getenv('USER_NAME_JASPER')
        PASSWORD = os.getenv('DATABASE_PASSWORD_JASPER')

    conn_str = urllib.parse.quote_plus(
        f"""DRIVER={{ODBC Driver 17 for SQL Server}};
        SERVER={SERVER};
        DATABASE={DATABASE};
        UID={USER_NAME};
        PWD={PASSWORD}"""
        )
    conn = sa.create_engine(f"""mssql+pyodbc:///?odbc_connect={conn_str}""")
    return conn

def sql_to_df(query:str, use_live:bool=True)->pd.DataFrame:
    """Function to get info from a database base in a Query

    Args:
        query (str): String with the query statement
        use_live (bool): Use or not the live database

    Returns:
        pd.DataFrame: Dataframe with the info result of the query
    """    
    conn = get_conn(use_live)
    return pd.read_sql_query(query, conn)

def df_to_sql(df:pd.DataFrame, table_name:str, use_live:bool=False, columns:list=None):
    if not df.empty:

        to_str = lambda x: f"'{x}'"
        base_query = """INSERT INTO {TABLE}
                    ({FIELDS})
                    VALUES {VALUES}"""

        if columns:
            fields = ', '.join([col for col in columns])
            df = df[columns].copy()
        else:
            fields = ', '.join([col for col in df.columns])

        values = []
        for _, row in df.iterrows():
            data = ', '.join([to_str(val) if isinstance(val, str) else str(val) for val in row.values])
            values.append(f'({data})')
        values = ',\n'.join(values)
        
        final_query = base_query.format(TABLE= table_name,
                                FIELDS= fields,
                                VALUES= values)
        conn = get_conn(use_live)
        cursor = conn.cursor()
        cursor.execute(final_query)
        conn.commit()
        cursor.close()


if __name__ == '__main__':
    query = """SELECT * FROM [dbo].[Lookup_ClaimStatus];"""
    df = sql_to_df(query, use_live=True)
    print(df)