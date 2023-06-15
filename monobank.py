import time
from datetime import date, timedelta

import pandas as pd
import monobank

# Initialize the client with your token
mono = monobank.Client('your_token_here')

def get_statements_as_df(account_id: str, start_date: date) -> pd.DataFrame:
    """
    Retrieve all operations from a given date to today for a specific account 
    and return them as a pandas DataFrame.
    """
    end_date = date.today()
    current_start_date = start_date
    statements = []

    # Fetch data in 30-day intervals
    while current_start_date <= end_date:
        # Make sure 'to' date is not more than 30 days from 'from' date and it's not a future date
        current_end_date = min(current_start_date + timedelta(days=30), end_date)
        try:
            statements.extend(mono.get_statements(account_id, current_start_date, current_end_date))
        except monobank.TooManyRequests:
            print("Too many requests. Waiting for 60 seconds before retrying.")
            time.sleep(60)  # wait for 60 seconds before retrying
            continue
        current_start_date = current_end_date + timedelta(days=1)

    # Convert the statements into a DataFrame
    df = pd.DataFrame(statements)

    # Normalize amounts and set correct time zone
    for column in ['amount', 'operationAmount', 'cashbackAmount', 'balance']:
        df[column] = df[column] / 100
    df['time'] = df['time'].dt.tz_localize('UTC').dt.tz_convert('US/Eastern')

    return df

# Get the history and save it to a CSV
history = get_statements_as_df('your_account_id_here', date(2022,10,4))
history.to_csv('monobank.csv')

# Handle potential "Too Many Requests" error
try:
    statements = mono.get_statements('your_account_id_here', date(2019,1,1), date(2019,1,30))
except monobank.TooManyRequests:
    print("Too many requests. Please wait and try again.")
