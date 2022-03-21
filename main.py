import argparse
import base64
import os
import pandas as pd
import requests
import sqlalchemy
import warnings

from constants import Constants
from datetime import date, datetime, timedelta
from dotenv import load_dotenv
from email_service import EmailService
from io import StringIO
from pandas.core.common import SettingWithCopyWarning
from query import Query
from sqlalchemy.sql.expression import bindparam
from sqlalchemy.types import String
from sqlalchemy.sql import text

load_dotenv()
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

parser = argparse.ArgumentParser()

parser.add_argument('--start_date', help='Start Date')
parser.add_argument('--end_date', help='End Date')
parser.add_argument('--year', help='Year')
parser.add_argument('--to', help='Recipients')
parser.add_argument('--cc', help='Carbon copies')
args = parser.parse_args()

POSTMARK_KEY = os.getenv('POSTMARK_KEY')
emailClient = EmailService(POSTMARK_KEY)

class WeeklyOnboardedUsers:

    def __init__(self, start_date, end_date, current_year):

        self.start_date = start_date
        self.end_date = end_date
        self.current_year = current_year

        self.serverdb = sqlalchemy.create_engine(
            sqlalchemy.engine.url.URL(
                drivername='mysql+pymysql',
                username=os.getenv('MYSQL_USER'),
                password=os.getenv('MYSQL_PASSWORD'),
                database=os.getenv('MYSQL_DB'),
                host=os.getenv('MYSQL_HOST'),
                port=os.getenv('MYSQL_PORT')
                # query={
                #     'unix_socket': '/cloudsql/{}'.format(Constants.cloud_sql_connection_name)
                # }
            ),
        )

    def get_weekly_onboarded_users(self):

        users_df = pd.read_sql(Query.MEMBERS_DATA.format(start_date=self.start_date, end_date=self.end_date), self.serverdb)
        current_year_users_df = pd.read_sql(Query.CURRENT_YEAR_MEMBERS_DATA.format(current_year=self.current_year), self.serverdb)

        self.to_excel(users_df, current_year_users_df)

    def to_excel(self, df1, df2):

        writer = pd.ExcelWriter(
            path=self.get_folder_location() + "/" + Constants.FILE_NAME,
            engine='xlsxwriter'
        )

        df1.to_excel(writer, sheet_name="Last Week Onboarded Users", index=False)
        df2.to_excel(writer, sheet_name="Current year Onboarded Users", index=False)
        writer.save()
        self.convert_to_binary()

    def convert_to_binary(self):

        data = open(self.get_folder_location() + "/" + Constants.FILE_NAME, 'rb').read()
        base64_encoded = base64.b64encode(data).decode('UTF-8')
        self.send_email(base64_encoded)
        print("Email has been triggered")

    def get_folder_location(self):

        PATH = os.path.join(Constants.BASE_PATH)

        if not os.path.isdir(PATH):
            os.makedirs(PATH)

        return PATH

    def send_email(self, data):
        emailClient.send_email(
        os.getenv('SENDER'),
        args.to if args.to else os.getenv('RECIPIENTS'),
        args.cc if args.cc else os.getenv('CARBON_COPIES'),
        'AUTO GENERATED: Onboarded Users from {start_date} to {end_date}'.format(start_date=self.start_date, end_date=self.end_date), 
        "This is an auto generated email via POSTMARK!",
        [{"Name": "Onboarded-Users.xlsx", "Content": data, "ContentType": "application/vnd.ms-excel"}]   
    )


if __name__ == "__main__":

    current_date = datetime.now()
    idx = (current_date.weekday() + 1) % 7
    saturday_ = (current_date - timedelta(7+idx-6)).strftime('%Y-%m-%d')

    current_date_ = current_date.strftime('%Y-%m-%d')
    current_year_ = current_date.strftime('%Y')
    
    vimeo = WeeklyOnboardedUsers(
        args.start_date if args.start_date else str(saturday_),
        args.end_date if args.end_date else str(current_date_),
        args.year if args.year else str(current_year_)
    )
    vimeo.get_weekly_onboarded_users()