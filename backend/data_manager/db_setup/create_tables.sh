#!/bin/bash

# Set the database file name
DB_FILE="travel_agent.db"

# SQL commands to create the tables
SQL=$(cat <<EOF
CREATE TABLE IF NOT EXISTS Trip (
    trip_uuid TEXT PRIMARY KEY,
    user_uuid TEXT NOT NULL,
    name TEXT NOT NULL,
    start_date TEXT,
    end_date TEXT,
    destination TEXT NOT NULL,
    preferences TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS UserProfile (
    uuid TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    dietary_restrictions TEXT,
    allergies TEXT,
    notes TEXT
);
EOF
)

# Execute the SQL commands
sqlite3 "$DB_FILE" "$SQL"

echo "Database setup completed: $DB_FILE"