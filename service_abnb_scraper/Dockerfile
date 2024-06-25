# Usa l'immagine di base Jupyter con Spark
FROM python:3.10-alpine

WORKDIR /usr/src/

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src/abnbscraper.py .

CMD [ "python", "./abnbscraper.py" ]