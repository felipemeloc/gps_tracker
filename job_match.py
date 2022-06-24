import os
import src.db as db
import src.utils as utils
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
# Define project main path
MAIN_FOLDER = os.getenv('MAIN_PATH')

################################## Query Load #####################################

query_path = os.path.join(MAIN_FOLDER, 'queries')

TS_completed_jobs = open(os.path.join(query_path,
                    'TS_completed_jobs.sql'), 'r').read()


completed_jobs = db.sql_to_df(TS_completed_jobs)
completed_jobs['Locksmith'] = utils.clean_locksmith_name(completed_jobs['Locksmith'])
print(completed_jobs)