docker run -d --rm --name dummy -v json_snapshots:/root alpine tail -f /dev/null && docker cp service_abnb_scraper/outputs/2024_06_16_output.json dummy:/root/2024_06_16_output.json && docker cp service_abnb_scraper/outputs/2024_06_23_output.json dummy:/root/2024_06_23_output.json && docker stop dummy 

<br>

docker-compose down --volumes && rm -fr service_db/postgres_data

<br>

docker-compose up -d --no-deps --build  