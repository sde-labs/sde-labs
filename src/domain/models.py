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
    
    # TODO: Add @field_validator for longitude
    
    # TODO: Add @field_validator for alert_type
    # Valid types: LEAK, BLOCKAGE, PRESSURE, TEMPERATURE, ACOUSTIC
