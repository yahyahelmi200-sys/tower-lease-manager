from sqlalchemy import Column, Integer, String, Date, Float
from database import Base


class Lease(Base):
    __tablename__ = "leases"

    id = Column(Integer, primary_key=True, index=True)
    tower_id = Column(String)
    tower_name = Column(String)
    location = Column(String)
    landlord_name = Column(String)
    landlord_contact = Column(String)
    lease_start_date = Column(Date)
    lease_end_date = Column(Date)
    monthly_rent = Column(Float)
    escalation_rate = Column(Float)
    notes = Column(String, default="")


class Permit(Base):
    __tablename__ = "permits"

    id = Column(Integer, primary_key=True, index=True)
    tower_id = Column(String)
    tower_name = Column(String)
    permit_number = Column(String)
    permit_type = Column(String)
    issued_date = Column(Date)
    expiry_date = Column(Date)
    issuing_authority = Column(String)
    notes = Column(String, default="")
