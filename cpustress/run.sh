#!/usr/bin/with-contenv bashio

DURATION=$(bashio::config 'duration')
echo "Duration: $DURATION"

# Načtení z options.json pomocí jq, záložní hodnota je 300

# Pokud by jq vrátilo prázdný řetězec nebo null
if [ -z "$DURATION" ] || [ "$DURATION" = "null" ]; then
    DURATION=300
fi

echo "Spouštím zátěžový test na ${DURATION} sekund..."

stress-ng --cpu 0 --timeout "${DURATION}s"

echo "Zátěžový test dokončen."