# Usa l'immagine di base Jupyter con Spark
FROM python:3.10-alpine

WORKDIR /usr/src/

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src/* .
RUN chmod +x /usr/src/entrypoint.sh

# SOLO LA PRIMA VOLTA
# CMD ["sh", "-c", "python -u init_db.py && tail -f /dev/null"]

CMD ["sh", "-c", "python -u update_db.py && tail -f /dev/null"]


# CMD ["sh", "-c", "tail -f /dev/null"]

