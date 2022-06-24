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
import pandas as pd
import warnings
from dotenv import load_dotenv

load_dotenv()
warnings.filterwarnings("ignore")

def get_conn()->pyodbc.Connection:
    """Function to make the connection with sql management studio
    Returns:
        pyodbc.Connection: Database connection
    """    
    SERVER = os.getenv('SERVER')
    DATABASE = os.getenv('DATABASE')
    USER_NAME = os.getenv('USER_NAME')
    PASSWORD = os.getenv('DATABASE_PASSWORD')

    conn_str = ("Driver={SQL Server};"
                f"Server={SERVER};"
                f"Database={DATABASE};"
                f"UID={USER_NAME};"
                f"PWD={PASSWORD};")
    conn = pyodbc.connect(conn_str)
    return conn

def sql_to_df(query:str)->pd.DataFrame:
    """Function to get info from a database base in a Query
    Args:
        query (str): String with the query statement
    Returns:
        pd.DataFrame: Dataframe with the info result of the query
    """    
    conn = get_conn()
    return pd.read_sql_query(query, conn)

if __name__ == '__main__':
    query = """SELECT * FROM [dbo].[Lookup_ClaimStatus];"""
    df = sql_to_df(query)
    print(df)