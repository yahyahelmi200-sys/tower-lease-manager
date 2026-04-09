from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import date, timedelta

import models
import schemas
import database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Tower Permit & Lease Manager")

app.mount("/static", StaticFiles(directory="static"), name="static")


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return FileResponse("static/index.html")


# ── Dashboard ─────────────────────────────────────────────────────────────────

@app.get("/api/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    today = date.today()

    leases = db.query(models.Lease).all()
    permits = db.query(models.Permit).all()

    def days_left(d):
        return (d - today).days

    lease_stats = {
        "total": len(leases),
        "active": sum(1 for l in leases if days_left(l.lease_end_date) > 90),
        "expiring_soon": sum(1 for l in leases if 0 < days_left(l.lease_end_date) <= 90),
        "expired": sum(1 for l in leases if days_left(l.lease_end_date) <= 0),
    }

    permit_stats = {
        "total": len(permits),
        "active": sum(1 for p in permits if days_left(p.expiry_date) > 90),
        "expiring_soon": sum(1 for p in permits if 0 < days_left(p.expiry_date) <= 90),
        "expired": sum(1 for p in permits if days_left(p.expiry_date) <= 0),
    }

    alerts = []
    for l in leases:
        d = days_left(l.lease_end_date)
        if d <= 90:
            alerts.append({
                "type": "Lease",
                "tower_id": l.tower_id,
                "name": l.tower_name,
                "detail": f"Landlord: {l.landlord_name}",
                "contact": l.landlord_contact,
                "days_left": d,
                "deadline": str(l.lease_end_date),
            })
    for p in permits:
        d = days_left(p.expiry_date)
        if d <= 90:
            alerts.append({
                "type": "Permit",
                "tower_id": p.tower_id,
                "name": p.tower_name,
                "detail": f"{p.permit_type} — {p.permit_number}",
                "contact": p.issuing_authority,
                "days_left": d,
                "deadline": str(p.expiry_date),
            })

    alerts.sort(key=lambda x: x["days_left"])

    return {"leases": lease_stats, "permits": permit_stats, "alerts": alerts}


# ── Leases ────────────────────────────────────────────────────────────────────

@app.get("/api/leases", response_model=List[schemas.Lease])
def get_leases(db: Session = Depends(get_db)):
    return db.query(models.Lease).all()


@app.post("/api/leases", response_model=schemas.Lease, status_code=201)
def create_lease(lease: schemas.LeaseCreate, db: Session = Depends(get_db)):
    db_lease = models.Lease(**lease.model_dump())
    db.add(db_lease)
    db.commit()
    db.refresh(db_lease)
    return db_lease


@app.put("/api/leases/{lease_id}", response_model=schemas.Lease)
def update_lease(lease_id: int, lease: schemas.LeaseCreate, db: Session = Depends(get_db)):
    db_lease = db.query(models.Lease).filter(models.Lease.id == lease_id).first()
    if not db_lease:
        raise HTTPException(status_code=404, detail="Lease not found")
    for key, val in lease.model_dump().items():
        setattr(db_lease, key, val)
    db.commit()
    db.refresh(db_lease)
    return db_lease


@app.delete("/api/leases/{lease_id}")
def delete_lease(lease_id: int, db: Session = Depends(get_db)):
    db_lease = db.query(models.Lease).filter(models.Lease.id == lease_id).first()
    if not db_lease:
        raise HTTPException(status_code=404, detail="Lease not found")
    db.delete(db_lease)
    db.commit()
    return {"message": "Deleted"}


# ── Permits ───────────────────────────────────────────────────────────────────

@app.get("/api/permits", response_model=List[schemas.Permit])
def get_permits(db: Session = Depends(get_db)):
    return db.query(models.Permit).all()


@app.post("/api/permits", response_model=schemas.Permit, status_code=201)
def create_permit(permit: schemas.PermitCreate, db: Session = Depends(get_db)):
    db_permit = models.Permit(**permit.model_dump())
    db.add(db_permit)
    db.commit()
    db.refresh(db_permit)
    return db_permit


@app.put("/api/permits/{permit_id}", response_model=schemas.Permit)
def update_permit(permit_id: int, permit: schemas.PermitCreate, db: Session = Depends(get_db)):
    db_permit = db.query(models.Permit).filter(models.Permit.id == permit_id).first()
    if not db_permit:
        raise HTTPException(status_code=404, detail="Permit not found")
    for key, val in permit.model_dump().items():
        setattr(db_permit, key, val)
    db.commit()
    db.refresh(db_permit)
    return db_permit


@app.delete("/api/permits/{permit_id}")
def delete_permit(permit_id: int, db: Session = Depends(get_db)):
    db_permit = db.query(models.Permit).filter(models.Permit.id == permit_id).first()
    if not db_permit:
        raise HTTPException(status_code=404, detail="Permit not found")
    db.delete(db_permit)
    db.commit()
    return {"message": "Deleted"}


# ── Seed ──────────────────────────────────────────────────────────────────────

@app.post("/api/seed")
def seed_data(db: Session = Depends(get_db)):
    db.query(models.Lease).delete()
    db.query(models.Permit).delete()
    db.commit()

    today = date.today()

    leases = [
        models.Lease(tower_id="TWR-001", tower_name="KL Central Tower",
            location="Jalan Ampang, Kuala Lumpur", landlord_name="Ahmad bin Hassan",
            landlord_contact="ahmad.hassan@example.com", lease_start_date=date(2024, 1, 1),
            lease_end_date=today + timedelta(days=200), monthly_rent=2500.0,
            escalation_rate=3.0, notes="5-year lease, renewal option available"),
        models.Lease(tower_id="TWR-002", tower_name="Petaling Jaya North Tower",
            location="Jalan Utama, Petaling Jaya", landlord_name="Siti Rahimah binti Yusof",
            landlord_contact="siti.rahimah@example.com", lease_start_date=date(2021, 6, 1),
            lease_end_date=today + timedelta(days=60), monthly_rent=1800.0,
            escalation_rate=2.5, notes="Renewal negotiation in progress"),
        models.Lease(tower_id="TWR-003", tower_name="Shah Alam Industrial Tower",
            location="Persiaran Industri, Shah Alam", landlord_name="Tan Boon Keat",
            landlord_contact="tanbk@example.com", lease_start_date=date(2020, 3, 15),
            lease_end_date=today + timedelta(days=20), monthly_rent=3200.0,
            escalation_rate=4.0, notes="URGENT: Landlord requesting 15% rent increase"),
        models.Lease(tower_id="TWR-004", tower_name="Subang Jaya Rooftop Tower",
            location="SS15, Subang Jaya", landlord_name="Rajesh Kumar",
            landlord_contact="rajesh.kumar@example.com", lease_start_date=date(2019, 9, 1),
            lease_end_date=today - timedelta(days=15), monthly_rent=2100.0,
            escalation_rate=3.5, notes="Lease expired — legal team reviewing options"),
        models.Lease(tower_id="TWR-005", tower_name="Cheras Hilltop Tower",
            location="Jalan Cheras, Kuala Lumpur", landlord_name="Lim Siew Lan",
            landlord_contact="limsiewlan@example.com", lease_start_date=date(2023, 11, 1),
            lease_end_date=today + timedelta(days=400), monthly_rent=2800.0,
            escalation_rate=3.0, notes="New lease, favourable terms secured"),
    ]

    permits = [
        models.Permit(tower_id="TWR-001", tower_name="KL Central Tower",
            permit_number="DBKL/ANT/2024/001", permit_type="Antenna Installation",
            issued_date=date(2024, 1, 15), expiry_date=today + timedelta(days=270),
            issuing_authority="Dewan Bandaraya KL (DBKL)", notes="Annual renewal required"),
        models.Permit(tower_id="TWR-002", tower_name="Petaling Jaya North Tower",
            permit_number="MBPJ/BLDG/2021/045", permit_type="Building Permit",
            issued_date=date(2021, 7, 1), expiry_date=today + timedelta(days=45),
            issuing_authority="Majlis Bandaraya Petaling Jaya", notes="Renewal submitted, pending approval"),
        models.Permit(tower_id="TWR-003", tower_name="Shah Alam Industrial Tower",
            permit_number="MBSA/ANT/2020/112", permit_type="Antenna Installation",
            issued_date=date(2020, 4, 1), expiry_date=today + timedelta(days=15),
            issuing_authority="Majlis Bandaraya Shah Alam", notes="URGENT: Renewal application must be submitted"),
        models.Permit(tower_id="TWR-004", tower_name="Subang Jaya Rooftop Tower",
            permit_number="MPSJ/ZON/2019/089", permit_type="Zoning Approval",
            issued_date=date(2019, 10, 1), expiry_date=today - timedelta(days=10),
            issuing_authority="Majlis Perbandaran Subang Jaya", notes="Expired — legal review ongoing"),
        models.Permit(tower_id="TWR-001", tower_name="KL Central Tower",
            permit_number="MCMC/FREQ/2024/330", permit_type="Frequency License",
            issued_date=date(2024, 3, 1), expiry_date=today + timedelta(days=320),
            issuing_authority="MCMC", notes="5G frequency allocation — B78 band"),
        models.Permit(tower_id="TWR-005", tower_name="Cheras Hilltop Tower",
            permit_number="DBKL/BLDG/2023/201", permit_type="Building Permit",
            issued_date=date(2023, 12, 1), expiry_date=today + timedelta(days=75),
            issuing_authority="Dewan Bandaraya KL (DBKL)", notes="Structure inspection passed"),
    ]

    db.add_all(leases)
    db.add_all(permits)
    db.commit()
    return {"message": "Sample data loaded", "leases": len(leases), "permits": len(permits)}
