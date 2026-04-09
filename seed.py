"""Run this once to populate the database with sample data."""
from datetime import date, timedelta
import models
import database

models.Base.metadata.create_all(bind=database.engine)

db = database.SessionLocal()

# Clear existing records
db.query(models.Lease).delete()
db.query(models.Permit).delete()
db.commit()

TODAY = date(2026, 4, 10)

leases = [
    models.Lease(
        tower_id="TWR-001",
        tower_name="KL Central Tower",
        location="Jalan Ampang, Kuala Lumpur",
        landlord_name="Ahmad bin Hassan",
        landlord_contact="ahmad.hassan@example.com",
        lease_start_date=date(2024, 1, 1),
        lease_end_date=TODAY + timedelta(days=200),
        monthly_rent=2500.00,
        escalation_rate=3.0,
        notes="5-year lease, renewal option available",
    ),
    models.Lease(
        tower_id="TWR-002",
        tower_name="Petaling Jaya North Tower",
        location="Jalan Utama, Petaling Jaya",
        landlord_name="Siti Rahimah binti Yusof",
        landlord_contact="siti.rahimah@example.com",
        lease_start_date=date(2021, 6, 1),
        lease_end_date=TODAY + timedelta(days=60),
        monthly_rent=1800.00,
        escalation_rate=2.5,
        notes="Renewal negotiation in progress",
    ),
    models.Lease(
        tower_id="TWR-003",
        tower_name="Shah Alam Industrial Tower",
        location="Persiaran Industri, Shah Alam",
        landlord_name="Tan Boon Keat",
        landlord_contact="tanbk@example.com",
        lease_start_date=date(2020, 3, 15),
        lease_end_date=TODAY + timedelta(days=20),
        monthly_rent=3200.00,
        escalation_rate=4.0,
        notes="URGENT: Landlord requesting 15% rent increase",
    ),
    models.Lease(
        tower_id="TWR-004",
        tower_name="Subang Jaya Rooftop Tower",
        location="SS15, Subang Jaya",
        landlord_name="Rajesh Kumar",
        landlord_contact="rajesh.kumar@example.com",
        lease_start_date=date(2019, 9, 1),
        lease_end_date=TODAY - timedelta(days=15),
        monthly_rent=2100.00,
        escalation_rate=3.5,
        notes="Lease expired — legal team reviewing options",
    ),
    models.Lease(
        tower_id="TWR-005",
        tower_name="Cheras Hilltop Tower",
        location="Jalan Cheras, Kuala Lumpur",
        landlord_name="Lim Siew Lan",
        landlord_contact="limsiewlan@example.com",
        lease_start_date=date(2023, 11, 1),
        lease_end_date=TODAY + timedelta(days=400),
        monthly_rent=2800.00,
        escalation_rate=3.0,
        notes="New lease, favourable terms secured",
    ),
]

permits = [
    models.Permit(
        tower_id="TWR-001",
        tower_name="KL Central Tower",
        permit_number="DBKL/ANT/2024/001",
        permit_type="Antenna Installation",
        issued_date=date(2024, 1, 15),
        expiry_date=TODAY + timedelta(days=270),
        issuing_authority="Dewan Bandaraya KL (DBKL)",
        notes="Annual renewal required",
    ),
    models.Permit(
        tower_id="TWR-002",
        tower_name="Petaling Jaya North Tower",
        permit_number="MBPJ/BLDG/2021/045",
        permit_type="Building Permit",
        issued_date=date(2021, 7, 1),
        expiry_date=TODAY + timedelta(days=45),
        issuing_authority="Majlis Bandaraya Petaling Jaya",
        notes="Renewal submitted, pending approval",
    ),
    models.Permit(
        tower_id="TWR-003",
        tower_name="Shah Alam Industrial Tower",
        permit_number="MBSA/ANT/2020/112",
        permit_type="Antenna Installation",
        issued_date=date(2020, 4, 1),
        expiry_date=TODAY + timedelta(days=15),
        issuing_authority="Majlis Bandaraya Shah Alam",
        notes="URGENT: Renewal application must be submitted immediately",
    ),
    models.Permit(
        tower_id="TWR-004",
        tower_name="Subang Jaya Rooftop Tower",
        permit_number="MPSJ/ZON/2019/089",
        permit_type="Zoning Approval",
        issued_date=date(2019, 10, 1),
        expiry_date=TODAY - timedelta(days=10),
        issuing_authority="Majlis Perbandaran Subang Jaya",
        notes="Expired — legal review ongoing",
    ),
    models.Permit(
        tower_id="TWR-001",
        tower_name="KL Central Tower",
        permit_number="MCMC/FREQ/2024/330",
        permit_type="Frequency License",
        issued_date=date(2024, 3, 1),
        expiry_date=TODAY + timedelta(days=320),
        issuing_authority="MCMC",
        notes="5G frequency allocation — B78 band",
    ),
    models.Permit(
        tower_id="TWR-005",
        tower_name="Cheras Hilltop Tower",
        permit_number="DBKL/BLDG/2023/201",
        permit_type="Building Permit",
        issued_date=date(2023, 12, 1),
        expiry_date=TODAY + timedelta(days=75),
        issuing_authority="Dewan Bandaraya KL (DBKL)",
        notes="Structure inspection passed",
    ),
]

db.add_all(leases)
db.add_all(permits)
db.commit()
db.close()

print("Sample data inserted successfully!")
print(f"  Leases  : {len(leases)}")
print(f"  Permits : {len(permits)}")
