from decimal import Decimal
import pandas as pd
import json
from datetime import datetime
import unittest
import tempfile
import os
import psycopg2

from db_connection import ABNBDBScraperConnection


def create_abnbscraper_df_from_json(filepath):
    if os.path.exists(filepath):
    # Read the JSON file into a pandas DataFrame
        with open(filepath, 'r') as file:
            json_data = json.load(file)
            df = pd.DataFrame(json_data)

            # Creare le colonne aggiuntive
            df['location'] = df.apply(lambda x: {'lat': x['lat'], 'lon': x['lon']}, axis=1)
            df['price'] = df['priceStaying'].apply(lambda x: float(x))
            df['pricecleaning'] = df['priceCleaning'].apply(lambda x: float(x))
            df['rented'] = False
            df['created_ts'] = datetime.now()
            df['updating_logs'] = None

            # Riorganizzare le colonne secondo l'ordine richiesto
            df = df[['id', 'name', 'location', 'price', 'pricecleaning', 'checkin', 'checkout', 'rented', 'created_ts', 'updating_logs']]

            return df
    else:
        print(f"File {filepath} not found.")
    
    return None

def create_abnbscraper_df_from_db(query, params):
    db = ABNBDBScraperConnection()
    result = db.execute_query(query, params)
    df = pd.DataFrame(result['rows'], columns=result['column_names'])
    decimal_columns = [col for col in df.columns if isinstance(df[col].iloc[0], Decimal)]    
    for col in decimal_columns:
        df[col] = df[col].astype(float)
    
    return df

class TestCreateDataFrameFromJson(unittest.TestCase):
    def setUp(self):
        # Esempio di JSON per il test
        self.json_data = '''[
                {
                    "name": "Vista a 180\u00b0 sul Lago Maggiore e sulle Alpi",
                    "id": "755274115372467598",
                    "lat": 45.79495,
                    "lon": 8.53644,
                    "priceStaying": 93,
                    "priceCleaning": 37,
                    "checkin": "2024-07-08",
                    "checkout": "2024-07-09"
                },
        ]'''

        # Creare un file JSON temporaneo per il test
        self.test_file = tempfile.NamedTemporaryFile(delete=False, mode='w')
        self.test_file.write(self.json_data)
        self.test_file.close()

    def tearDown(self):
        # Rimuovere il file temporaneo
        os.unlink(self.test_file.name)

    def test_create_dataframe(self):
        # Usare la funzione per leggere il file e creare il DataFrame
        df = create_abnbscraper_df_from_json(self.test_file.name)
        
        # Verificare che il DataFrame abbia le colonne giuste
        expected_columns = ['id', 'name', 'location', 'price', 'pricecleaning', 'checkin', 'checkout', 'rented', 'created_ts', 'updating_logs']
        self.assertListEqual(list(df.columns), expected_columns)
        
        # Verificare alcuni valori specifici
        self.assertEqual(df.loc[0, 'name'], 'Appartamento 1')
        self.assertEqual(df.loc[1, 'pricecleaning'], 25)
        self.assertFalse(df.loc[0, 'rented'])
        self.assertIsNone(df.loc[0, 'updating_logs'])
        
        # Verificare che 'created_ts' sia un datetime
        self.assertIsInstance(df.loc[0, 'created_ts'], datetime)

if __name__ == '__main__':
    unittest.main()
