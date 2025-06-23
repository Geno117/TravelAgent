#trip manager
#manage trips
import uuid
import json
from datetime import datetime

from pydantic import BaseModel, ValidationError, field_validator, model_validator
from typing import Optional


class ValidationErrors(Exception):
    """Custom validation error for Trip manager"""
    pass


class Trip(BaseModel):
    trip_uuid: str
    user_uuid: str
    name: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    destination: str
    preferences: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("trip_uuid", "user_uuid", "name", "destination")
    @classmethod
    def validate_required_strings(cls, v):
        if not isinstance(v, str) or v.strip() == "":
            raise ValidationErrors("This field is required")
        return v

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_dates(cls, v):
        #check if date is valid but keep as string
        if v and isinstance(v, str):
            try:
                datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValidationErrors("Invalid date format. Use YYYY-MM-DD.")
        return v
            
    @model_validator(mode='before')
    @classmethod
    def check_dates(cls, values):
        if values.get("start_date") and values.get("end_date"):
            start = datetime.strptime(values["start_date"], "%Y-%m-%d")
            end = datetime.strptime(values["end_date"], "%Y-%m-%d")
            if start > end:
                raise ValidationErrors("Start date must be before end date")
        return values


class TripManager():
    def __init__(self, data_manager):
        self.db = data_manager

    def add_trip(self, trip_info):
        # Generate trip_uuid internally
        trip_uuid = str(uuid.uuid4())
        # Create Trip object with generated trip_uuid and provided trip_info
        trip = Trip(trip_uuid=trip_uuid, **trip_info)

        self.db.execute(f"INSERT INTO Trip (trip_uuid, user_uuid, name, start_date, end_date, destination, preferences, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (trip_uuid, trip.user_uuid, trip.name, trip.start_date, trip.end_date, trip.destination, trip.preferences, trip.notes))

        return trip_uuid

    def edit_trip(self, trip_id, trip_info):
        # For edit, we use the existing trip_id
        trip = Trip(trip_uuid=trip_id, **trip_info)

        self.db.execute(f"UPDATE Trip SET user_uuid=?, name=?, start_date=?, end_date=?, destination=?, preferences=?, notes=? WHERE trip_uuid=?", (trip.user_uuid, trip.name, trip.start_date, trip.end_date, trip.destination, trip.preferences, trip.notes, trip_id))

    def cancel_trip(self, trip_id):
        self.db.execute(f"DELETE FROM Trip WHERE trip_uuid=?", (trip_id,))
        return trip_id

    def get_trip(self, trip_id):
        self.db.execute(f"SELECT * FROM Trip WHERE trip_uuid=?", (trip_id,))
        trip = self.db.cursor.fetchone()
        #check if trip exists
        if trip is None:
            raise ValidationErrors("Trip does not exist")
        
        # Return as dictionary with named fields
        # Database columns: trip_uuid, user_uuid, name, start_date, end_date, destination, preferences, notes
        return {
            "trip_uuid": trip[0],
            "user_uuid": trip[1], 
            "name": trip[2],
            "start_date": trip[3],
            "end_date": trip[4],
            "destination": trip[5],
            "preferences": trip[6],
            "notes": trip[7]
        }

    # def get_all_trips(self):
    #     self.db.execute(f"SELECT * FROM Trip")
    #     return self.db.fetchall()
    
    def get_all_trips_by_user(self, user_id):
        self.db.execute(f"SELECT * FROM Trip WHERE user_uuid=?", (user_id,))
        trips = self.db.cursor.fetchall()
        
        # Convert each trip tuple to a dictionary
        # Database columns: trip_uuid, user_uuid, name, start_date, end_date, destination, preferences, notes
        return [
            {
                "trip_uuid": trip[0],
                "user_uuid": trip[1], 
                "name": trip[2],
                "start_date": trip[3],
                "end_date": trip[4],
                "destination": trip[5],
                "preferences": trip[6],
                "notes": trip[7]
            }
            for trip in trips
        ]
    