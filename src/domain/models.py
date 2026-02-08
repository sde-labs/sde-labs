"""
Domain models - pure data structures with validation
"""
from pydantic import BaseModel, field_validator


class Alert(BaseModel):
    """
    Alert domain model with built-in validation.
    
    TODO (Week 2): Add validators for:
    - latitude: must be between -90 and 90
    - longitude: must be between -180 and 180
    - alert_type: must be one of the valid types
    """
    timestamp: str
    site_id: str
    alert_type: str
    severity: str
    latitude: float
    longitude: float

    
    # TODO: Add @field_validator for latitude
    # Hint: @field_validator('latitude')
    #       def check_latitude(cls, v):
    #           if not -90 <= v <= 90:
    #               raise ValueError('latitude must be between -90 and 90')
    #           return v

    @field_validator("latitude")
    def check_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError("latitude must be between -90 and 90")
        return v
    
    # TODO: Add @field_validator for longitude

    @field_validator("longitude")
    def check_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError("longitude must be between -180 and 180")
        return v
    
    # TODO: Add @field_validator for alert_type
    # Valid types: LEAK, BLOCKAGE, PRESSURE, TEMPERATURE, ACOUSTIC

    @field_validator("alert_type")
    def check_alert_type(cls, v):
        valid_types = ("LEAK", "BLOCKAGE", "PRESSURE", "TEMPERATURE", "ACOUSTIC")
        if v not in valid_types:
            valid_types_list = ", ".join(valid_types)
            raise ValueError(f"alert_type must be one of: {valid_types_list}")
        return v
