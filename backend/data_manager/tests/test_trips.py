# tests/test_trips.py

import pytest
from pydantic import ValidationError
from data_manager.trip_manager import TripManager, ValidationErrors
from data_manager.data_manager import DataManager

@pytest.fixture
def db_manager():
    db = DataManager(":memory:", "Trip")
    #table setup
    trip_sql = """CREATE TABLE IF NOT EXISTS Trip (
    trip_uuid TEXT PRIMARY KEY,
    user_uuid TEXT NOT NULL,
    name TEXT NOT NULL,
    start_date TEXT,
    end_date TEXT,
    destination TEXT NOT NULL,
    preferences TEXT,
    notes TEXT);
    """
    db.execute(trip_sql)
    user_sql = """CREATE TABLE IF NOT EXISTS UserProfile (
    uuid TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    dietary_restrictions TEXT,
    allergies TEXT,
    notes TEXT
    );
    """
    db.execute(user_sql)
    yield db
    db.close()

@pytest.fixture
def trip_manager(db_manager):
    return TripManager(db_manager)

def test_get_trip(trip_manager):
    # write trip direct to memory and recall using get_trip
    trip_uuid = "123e4567-e89b-12d3-a456-426614174000"
    trip_info = {
        "name": "Test Trip",
        "user_uuid": "123e4567-e89b-12d3-a456-426614174000",
        "start_date": "2025-01-01",
        "end_date": "2025-01-10",
        "destination": "Paris",
        "preferences": "Museums",
    }
    # Insert directly into database for testing
    trip_manager.db.execute("INSERT INTO Trip (trip_uuid, user_uuid, name, start_date, end_date, destination, preferences, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                           (trip_uuid, trip_info["user_uuid"], trip_info["name"], trip_info["start_date"], trip_info["end_date"], trip_info["destination"], trip_info["preferences"], None))
    retrieved_trip = trip_manager.get_trip(trip_uuid)
    assert retrieved_trip is not None
    assert retrieved_trip["name"] == "Test Trip"
    assert retrieved_trip["destination"] == "Paris"
    assert retrieved_trip["preferences"] == "Museums"

def test_add_trip_edit_trip_happy_case(trip_manager):
    trip_info = {
        "name": "Test Trip",
        "user_uuid": "123e4567-e89b-12d3-a456-426614174000",
        "start_date": "2025-01-01",
        "end_date": "2025-01-10",
        "destination": "Paris",
        "preferences": "Museums",
    }
    trip_uuid = trip_manager.add_trip(trip_info)
    assert trip_uuid is not None
    assert trip_uuid != ""

    retrieved_trip = trip_manager.get_trip(trip_uuid)
    assert retrieved_trip is not None
    assert retrieved_trip["name"] == "Test Trip"
    assert retrieved_trip["destination"] == "Paris"
    assert retrieved_trip["preferences"] == "Museums"

    #edit trip
    trip_info["name"] = "Edited Trip"
    trip_manager.edit_trip(trip_uuid, trip_info)
    retrieved_trip = trip_manager.get_trip(trip_uuid)
    assert retrieved_trip["name"] == "Edited Trip"

def test_add_trip_bad_validation(trip_manager):
    #test missing required fields
    trip_info = {
        "user_uuid": "123e4567-e89b-12d3-a456-426614174000",
        "name": "Test Trip",
        "start_date": "2025-01-01",
        "end_date": "2025-01-10",
    }
    with pytest.raises(ValidationError):
        trip_manager.add_trip(trip_info)
    trip_info["destination"] = ""
    
    #test empty required field
    with pytest.raises(ValidationErrors):
        trip_manager.add_trip(trip_info)
    trip_info["destination"] = "Paris"
    trip_info["name"] = ""
    with pytest.raises(ValidationErrors):
        trip_manager.add_trip(trip_info)
    trip_info["name"] = "Test Trip"

    #test invalid date format
    #test start date is valid
    trip_info["start_date"] = "2025-13-01"
    with pytest.raises(ValidationError):
        trip_manager.add_trip(trip_info)
    trip_info["start_date"] = "2025-01-01"
    #test end date is valid
    trip_info["end_date"] = "2025-13-10"
    with pytest.raises(ValidationError):
        trip_manager.add_trip(trip_info)
    trip_info["end_date"] = "2025-01-10"

    

    #test start date after end date
    trip_info["start_date"] = "2025-01-31"
    trip_info["end_date"] = "2025-01-01"
    with pytest.raises(ValidationErrors):
        trip_manager.add_trip(trip_info)
    trip_info["start_date"] = "2025-01-01"
    trip_info["end_date"] = "2025-01-31"
    #test non-string destination
    trip_info["destination"] = 123
    with pytest.raises(ValidationError):
        trip_manager.add_trip(trip_info)
    trip_info["destination"] = "Paris"
    #test non-string name
    trip_info["name"] = 123
    with pytest.raises(ValidationError):
        trip_manager.add_trip(trip_info)
    
    assert True

def test_bad_edit_trip(trip_manager):
    trip_info = {
        "name": "Test Trip",
        "user_uuid": "123e4567-e89b-12d3-a456-426614174000",
        "start_date": "2025-01-01",
        "end_date": "2025-01-10",
        "destination": "Paris",
    }
    trip_uuid = trip_manager.add_trip(trip_info)
    trip_info["name"] = 123
    with pytest.raises(ValidationError):
        trip_manager.edit_trip(trip_uuid, trip_info)
    trip_info["name"] = "Test Trip"
    trip_info["destination"] = 123
    with pytest.raises(ValidationError):
        trip_manager.edit_trip(trip_uuid, trip_info)
    

def test_cancel_trip(trip_manager):
    trip_info = {
        "name": "Test Trip",
        "user_uuid": "123e4567-e89b-12d3-a456-426614174000",
        "start_date": "2025-01-01",
        "end_date": "2025-01-10",
        "destination": "Paris",
    }
    trip_uuid = trip_manager.add_trip(trip_info)
    trip_manager.cancel_trip(trip_uuid)
    with pytest.raises(ValidationErrors):
        trip_manager.get_trip(trip_uuid)
    assert True

def test_get_all_trips_by_user(trip_manager):
    trip_info = {
        "name": "Test Trip",
        "user_uuid": "123e4567-e89b-12d3-a456-426614174000",
        "start_date": "2025-01-01",
        "end_date": "2025-01-10",
        "destination": "Paris",
    }
    trip_manager.add_trip(trip_info)
    trip_info["name"] = "Test Trip 2"
    trip_manager.add_trip(trip_info)
    trips = trip_manager.get_all_trips_by_user("123e4567-e89b-12d3-a456-426614174000")
    assert len(trips) == 2
    assert trips[0]["name"] == "Test Trip"
    assert trips[1]["name"] == "Test Trip 2"
    assert True

def test_add_and_get_trip(trip_manager):
    # Create trip info
    trip_info = {
        "name": "Test Trip",
        "user_uuid": "123e4567-e89b-12d3-a456-426614174000",
        "start_date": "2025-01-01",
        "end_date": "2025-01-10",
        "destination": "Paris",
        "preferences": "Museums",
        "notes": "Pack warm clothes"
    }

    # Add trip
    trip_uuid = trip_manager.add_trip(trip_info)

    # Check via TripManager
    fetched_trip = trip_manager.get_trip(trip_uuid)
    assert fetched_trip is not None
    assert fetched_trip["name"] == "Test Trip"
    assert fetched_trip["destination"] == "Paris"
    assert fetched_trip["preferences"] == "Museums"