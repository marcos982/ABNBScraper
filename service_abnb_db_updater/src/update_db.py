import pandas as pd
import json
import os
import datetime
import psycopg2
from db_connection import ABNBDBScraperConnection


from create_df import create_abnbscraper_df_from_db, create_abnbscraper_df_from_json

def update_db(currentResults: pd.DataFrame, json_data: dict):
    # Your code here
    pass

print("Break 0")

# Get the current date
current_date = datetime.datetime.now().strftime("%Y_%m_%d")

pd.set_option('display.max_rows', 10)  # Adjust as needed
pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.width', None)  # Use maximum width available
pd.set_option('display.max_colwidth', None)  # Show full content of each column


# Define the file path
# file_path = f"/inputs/{current_date}_output.json"
file_path = f"/inputs/2024_06_23_output.json"

# # Connect to the PostgreSQL database
# conn = psycopg2.connect(
#     host="db",
#     port=5432,
#     database="ABNSCraper",
#     user="postgres",
#     password="password"
# )
db = ABNBDBScraperConnection()

currentResults = create_abnbscraper_df_from_json(file_path)
grouped_results = currentResults.groupby(['checkin', 'checkout'])
print(grouped_results)

# Iterate over each group
for checkin_checkout_date, current_ci_co_date_json_df in grouped_results:
    checkin_date, checkout_date = checkin_checkout_date

    # Get dataframe for current checkin/checkout from table abnbscraper
    query = "SELECT * FROM abnscraper WHERE checkin = %s AND checkout = %s"
    params = (checkin_date, checkout_date)
    db_current_checkin_checkout_df = create_abnbscraper_df_from_db(query, params)
    # print(db_current_checkin_checkout_df.to_string)

    # Iterate and compare
    for index, db_row in db_current_checkin_checkout_df.iterrows():
        print(f"Current DB ROW: {db_row}")
        # Find matching record in db_current_checkin_checkout_df
        matching_json_row = current_ci_co_date_json_df[(current_ci_co_date_json_df['id'] == db_row['id'])]
        print(f"Match: {matching_json_row}")

        # If there is a match, compare the fields to see if there is an update
        if not matching_json_row.empty:
            exclude_columns = ['pkey', 'id', 'checkin', 'checkout', 'rented', 'created_ts', 'updating_logs']
            other_fields = [col for col in db_current_checkin_checkout_df.columns if col not in exclude_columns]

            updating_log = {
                    "id": f"{db_row['id']}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            updated_fields = []

            # Assuming 'other_fields' is a list of other column names to compare
            for field in other_fields:
                if db_row[field] != matching_json_row.iloc[0][field]:
                    # Log the update
                    updated_fields.append({
                            "field_updated": field,
                            "old_value": db_row[field],
                            "new_value": matching_json_row.iloc[0][field]
                    })
                    # Update the field in db_current_checkin_checkout_df (or directly in the database as required)

            if updated_fields:
                updating_log["updated_fields"] = updated_fields
                db.update_database(db_row['pkey'], updating_log)
                
            # In any case, remove the matched record from db_current_checkin_checkout_df and from current_ci_co_date_json_df
            db_current_checkin_checkout_df = db_current_checkin_checkout_df.drop(index=index)
            current_ci_co_date_json_df = current_ci_co_date_json_df.drop(index=matching_json_row.index[0])


    # At this point, db_current_checkin_checkout_df contains only the records that are no longer present in the current JSON data: we assume they are rented!
    # Update the 'rented' field for these records
    db_current_checkin_checkout_df['rented'] = True
    for index, db_row in db_current_checkin_checkout_df.iterrows():
        updating_log = {
                "id": f"{db_row['id']}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
                "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "updated_fields": [
                        {
                                "field_updated": "rented",
                                "old_value": db_row['rented'],
                                "new_value": True
                        }
                ]
        }
        db.update_database(db_row['pkey'], updating_log)

    # At this point, current_ci_co_date_json_df contains only the records that are not present in the database: we assume they are new!
    # Add these records to the database
    for index, new_row in current_ci_co_date_json_df.iterrows():
        db.insert_record(new_row)

print("END")




