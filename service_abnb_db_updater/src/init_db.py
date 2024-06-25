import json
import psycopg2
from datetime import datetime

fileName = "/inputs/2024_06_16_output.json"

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    host="db",
    port=5432,
    database="ABNSCraper",
    user="postgres",
    password="password"
)

# Open the FIRST_JSON file and load the JSON data
with open(fileName) as file:
    data = json.load(file)

# Iterate over each JSON record and insert it into the database
for record in data:
    # Extract the required fields from the record
    name = record["name"]
    id = record["id"]
    lat = record["lat"]
    lon = record["lon"]
    price = record["priceStaying"]
    price_cleaning = record["priceCleaning"]
    checkin = record["checkin"]
    checkout = record["checkout"]
    
    # Create the location JSON object
    location = {"lat": lat, "lon": lon}
    
    # Get the current timestamp
    created_ts = datetime.now()
 
    # Insert the record into the database
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO "public"."abnscraper" (id, name, location, price, pricecleaning, checkin, checkout, rented, created_ts, updating_logs)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NULL)
        ON CONFLICT (id, checkin, checkout) DO NOTHING;
    """, (id, name, json.dumps(location), price, price_cleaning, checkin, checkout, False, created_ts))
    conn.commit()
    cursor.close()

# Close the database connection
conn.close()