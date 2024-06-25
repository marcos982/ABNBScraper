import datetime
from bs4 import BeautifulSoup
import requests

import json
import os




def getResultsFor(URL):
    resultsForUrl = []

    def scrape_page(page_url):
        """Extracts HTML from a webpage"""
    
        answer = requests.get(page_url)
        content = answer.content
        soup = BeautifulSoup(content, features='html.parser')
    
        return soup

    soup = scrape_page(URL)
# print(soup.prettify())

    script_tag = soup.find(id='data-injector-instances')
#print(script_tag.text)

    json_data = json.loads(script_tag.text)

    if "root > core-guest-spa" in json_data:
        core_guest_spa_data = json_data["root > core-guest-spa"]

        json_with_niobeMinimalClientData = None
        for data in core_guest_spa_data:
            if data[0] == 'Hyperloop10Token':            
                json_with_niobeMinimalClientData = data[1]
                break
    
        if not json_with_niobeMinimalClientData:
            print("Hyperloop10Token non trovato nel JSON.")

        niobeMinimalClientData = json_with_niobeMinimalClientData["niobeMinimalClientData"]
        # print("niobeMinimalClientData:")
        # print(niobeMinimalClientData) 

        json_withMapResults = None
        for data in niobeMinimalClientData:
            if data[0].startswith('StaysSearch'):
                json_withMapResults = data[1]
                #print(json_withMapResuts)
                mapResults = json_withMapResults['data']['presentation']['staysSearch']['mapResults']['mapSearchResults']

                for mapResult in mapResults:
                    # print(mapResult)
                    listing = mapResult['listing']
                    name = listing['name']
                    id = listing['id']
                    lat = listing['coordinate']['latitude']
                    lon = listing['coordinate']['longitude']
                    priceStaying = mapResult['pricingQuote']['structuredStayDisplayPrice']['explanationData']['priceDetails'][0]['items'][0].get('priceString', None)
                    priceStaying = int(''.join(filter(str.isdigit, priceStaying)))
                    priceCleaning = mapResult['pricingQuote']['structuredStayDisplayPrice']['explanationData']['priceDetails'][0]['items'][1].get('priceString', None)
                    priceCleaning = int(''.join(filter(str.isdigit, priceCleaning)))
                
                    # print({
                    #     'name': name,
                    #     'id': id,
                    #     'lat': lat,
                    #     'lon': lon,
                    #     'priceStaying': priceStaying,
                    #     'priceCleaning': priceCleaning
                    # })

                    resultsForUrl.append({
                    'name': name,
                    'id': id,
                    'lat': lat,
                    'lon': lon,
                    'priceStaying': priceStaying,
                    'priceCleaning': priceCleaning
                })

                break

    else:
        print("core-guest-spa non trovato nel JSON.")

    return resultsForUrl

# divs_with_exact_classes = soup.find_all(lambda tag: tag.name == 'div' and tag.get('class') == ['1l1h97y', 'atm_d2_1kqhmmj', 'dir', 'dir-ltr'])

# # Stampa i risultati
# for parent_div in divs_with_exact_classes:
#     print("CAZZO")
#     print(parent_div.prettify())

# script_tag = soup.find_all('script')
# print(script_tag)
      
# URL = 'https://www.airbnb.it/s/Meina--NO/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2024-07-01&monthly_length=3&monthly_end_date=2024-10-01&price_filter_input_type=0&channel=EXPLORE&date_picker_type=calendar&checkin=2024-06-21&checkout=2024-06-23&query=Meina%2C%20NO&place_id=ChIJewN8995zhkcRgmQnvnFohzA&adults=2&source=structured_search_input_header&search_type=user_map_move&search_mode=regular_search&price_filter_num_nights=2&ne_lat=45.80248048037412&ne_lng=8.541345832322806&sw_lat=45.78367263518005&sw_lng=8.534842701478496&zoom=10&zoom_level=10&search_by_map=true'
URL_preCheckIn = 'https://www.airbnb.it/s/Meina--NO/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2024-07-01&monthly_length=3&monthly_end_date=2024-10-01&price_filter_input_type=0&channel=EXPLORE&date_picker_type=calendar&'
URL_postCheckout = '&query=Meina%2C%20NO&place_id=ChIJewN8995zhkcRgmQnvnFohzA&adults=2&source=structured_search_input_header&search_type=user_map_move&search_mode=regular_search&price_filter_num_nights=2&ne_lat=45.80248048037412&ne_lng=8.541345832322806&sw_lat=45.78367263518005&sw_lng=8.534842701478496&zoom=10&zoom_level=10&search_by_map=true'

start_date = datetime.date.today()
end_date = datetime.date(2024, 7, 30) 

current_date = start_date
globalResult = []
while current_date <= end_date:
    checkin = current_date.strftime('%Y-%m-%d')
    checkout = (current_date + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    ci_co_str = '' + f"checkin={current_date.strftime('%Y-%m-%d')}&checkout={(current_date + datetime.timedelta(days=1)).strftime('%Y-%m-%d')}"
    URL = URL_preCheckIn + ci_co_str + URL_postCheckout

    # print(getResultsFor(URL))
    print("Calling getResultsFor()...", URL)
    results = getResultsFor(URL)

    for result in results:        
        result["checkin"] = checkin
        result["checkout"] = checkout
        globalResult.append(result)    

    current_date += datetime.timedelta(days=1)

print(json.dumps(globalResult, indent=4))

output_dir = "/outputs"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

output_file = datetime.date.today().strftime("%Y_%m_%d") + "_output.json"
output_path = os.path.join(output_dir, output_file)

with open(output_path, "w") as file:
    file.write(json.dumps(globalResult, indent=4))

# Per ogni risultato nel database vedi se: si deve segnalare come AFFITATO (offerta non più presete in globalResults); si deve aggiornare il prezzo (ofefrta presente in globalResults con prezzo diverso); non si deve fare nulla (offerta presente uguale in globalResults)

# Aggungi i risultati in globalResults che non erano nel database

