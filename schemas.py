from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional


class LeaseBase(BaseModel):
    tower_id: str
    tower_name: str
    location: str
    landlord_name: str
    landlord_contact: str
    lease_start_date: date
    lease_end_date: date
    monthly_rent: float
    escalation_rate: float
    notes: Optional[str] = ""


class LeaseCreate(LeaseBase):
    pass


class Lease(LeaseBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class PermitBase(BaseModel):
    tower_id: str
    tower_name: str
    permit_number: str
    permit_type: str
    issued_date: date
    expiry_date: date
    issuing_authority: str
    notes: Optional[str] = ""


class PermitCreate(PermitBase):
    pass


class Permit(PermitBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
