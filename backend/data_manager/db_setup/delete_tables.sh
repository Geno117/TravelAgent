#!/bin/bash

DB_FILE="travel_agent.db"

# Check if database exists
if [ ! -f "$DB_FILE" ]; then
    echo "No database file found at $DB_FILE."
    exit 0
fi

# Prompt user
read -p "Are you sure you want to delete '$DB_FILE'? [y/N]: " confirm

# Convert to lowercase and check
confirm=$(echo "$confirm" | tr '[:upper:]' '[:lower:]')

if [[ "$confirm" == "y" || "$confirm" == "yes" ]]; then
    rm "$DB_FILE"
    echo "Database file '$DB_FILE' has been deleted."
else
    echo "Teardown cancelled."
fi