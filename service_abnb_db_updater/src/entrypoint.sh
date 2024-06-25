#!/bin/sh

# Controlla la variabile d'ambiente FIRST_RUN
if [ "$FIRST_RUN" = "true" ]; then
    echo "Prima esecuzione: inizializzazione del database..."
    python init_db.py
else
    echo "Aggiornamento del database..."
fi

# Esegui lo script di aggiornamento del database
python update_db.py

# Mantieni il container in esecuzione
tail -f /dev/null
