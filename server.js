const express = require('express');
const Database = require('better-sqlite3');
const path = require('path');

const app = express();
const db = new Database('tower_lease.db');

app.use(express.json());
app.use('/static', express.static(path.join(__dirname, 'static')));

// ── Database Setup ────────────────────────────────────────────────────────────

db.exec(`
  CREATE TABLE IF NOT EXISTS leases (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    tower_id         TEXT NOT NULL,
    tower_name       TEXT NOT NULL,
    location         TEXT NOT NULL,
    landlord_name    TEXT NOT NULL,
    landlord_contact TEXT NOT NULL,
    lease_start_date TEXT NOT NULL,
    lease_end_date   TEXT NOT NULL,
    monthly_rent     REAL NOT NULL,
    escalation_rate  REAL NOT NULL,
    notes            TEXT DEFAULT ''
  );

  CREATE TABLE IF NOT EXISTS permits (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    tower_id          TEXT NOT NULL,
    tower_name        TEXT NOT NULL,
    permit_number     TEXT NOT NULL,
    permit_type       TEXT NOT NULL,
    issued_date       TEXT NOT NULL,
    expiry_date       TEXT NOT NULL,
    issuing_authority TEXT NOT NULL,
    notes             TEXT DEFAULT ''
  );
`);

// ── Helpers ───────────────────────────────────────────────────────────────────

function daysLeft(dateStr) {
  const today = new Date(); today.setHours(0, 0, 0, 0);
  return Math.round((new Date(dateStr) - today) / 86400000);
}

function addDays(n) {
  const d = new Date(); d.setHours(0, 0, 0, 0); d.setDate(d.getDate() + n);
  return d.toISOString().slice(0, 10);
}

// ── Routes ────────────────────────────────────────────────────────────────────

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'static', 'index.html'));
});

// Dashboard
app.get('/api/dashboard', (req, res) => {
  const leases  = db.prepare('SELECT * FROM leases').all();
  const permits = db.prepare('SELECT * FROM permits').all();

  const leaseStats = {
    total:         leases.length,
    active:        leases.filter(l => daysLeft(l.lease_end_date) > 90).length,
    expiring_soon: leases.filter(l => { const d = daysLeft(l.lease_end_date); return d > 0 && d <= 90; }).length,
    expired:       leases.filter(l => daysLeft(l.lease_end_date) <= 0).length,
  };

  const permitStats = {
    total:         permits.length,
    active:        permits.filter(p => daysLeft(p.expiry_date) > 90).length,
    expiring_soon: permits.filter(p => { const d = daysLeft(p.expiry_date); return d > 0 && d <= 90; }).length,
    expired:       permits.filter(p => daysLeft(p.expiry_date) <= 0).length,
  };

  const alerts = [];
  leases.forEach(l => {
    const d = daysLeft(l.lease_end_date);
    if (d <= 90) alerts.push({
      type: 'Lease', tower_id: l.tower_id, name: l.tower_name,
      detail: `Landlord: ${l.landlord_name}`, contact: l.landlord_contact,
      days_left: d, deadline: l.lease_end_date,
    });
  });
  permits.forEach(p => {
    const d = daysLeft(p.expiry_date);
    if (d <= 90) alerts.push({
      type: 'Permit', tower_id: p.tower_id, name: p.tower_name,
      detail: `${p.permit_type} — ${p.permit_number}`, contact: p.issuing_authority,
      days_left: d, deadline: p.expiry_date,
    });
  });
  alerts.sort((a, b) => a.days_left - b.days_left);

  res.json({ leases: leaseStats, permits: permitStats, alerts });
});

// ── Leases CRUD ───────────────────────────────────────────────────────────────

app.get('/api/leases', (req, res) => {
  res.json(db.prepare('SELECT * FROM leases').all());
});

app.post('/api/leases', (req, res) => {
  const { tower_id, tower_name, location, landlord_name, landlord_contact,
          lease_start_date, lease_end_date, monthly_rent, escalation_rate, notes } = req.body;
  const stmt = db.prepare(`
    INSERT INTO leases (tower_id, tower_name, location, landlord_name, landlord_contact,
      lease_start_date, lease_end_date, monthly_rent, escalation_rate, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`);
  const info = stmt.run(tower_id, tower_name, location, landlord_name, landlord_contact,
                        lease_start_date, lease_end_date, monthly_rent, escalation_rate, notes || '');
  res.status(201).json(db.prepare('SELECT * FROM leases WHERE id = ?').get(info.lastInsertRowid));
});

app.put('/api/leases/:id', (req, res) => {
  const { tower_id, tower_name, location, landlord_name, landlord_contact,
          lease_start_date, lease_end_date, monthly_rent, escalation_rate, notes } = req.body;
  db.prepare(`
    UPDATE leases SET tower_id=?, tower_name=?, location=?, landlord_name=?, landlord_contact=?,
      lease_start_date=?, lease_end_date=?, monthly_rent=?, escalation_rate=?, notes=?
    WHERE id=?`).run(tower_id, tower_name, location, landlord_name, landlord_contact,
                     lease_start_date, lease_end_date, monthly_rent, escalation_rate, notes || '',
                     req.params.id);
  res.json(db.prepare('SELECT * FROM leases WHERE id = ?').get(req.params.id));
});

app.delete('/api/leases/:id', (req, res) => {
  db.prepare('DELETE FROM leases WHERE id = ?').run(req.params.id);
  res.json({ message: 'Deleted' });
});

// ── Permits CRUD ──────────────────────────────────────────────────────────────

app.get('/api/permits', (req, res) => {
  res.json(db.prepare('SELECT * FROM permits').all());
});

app.post('/api/permits', (req, res) => {
  const { tower_id, tower_name, permit_number, permit_type, issued_date,
          expiry_date, issuing_authority, notes } = req.body;
  const stmt = db.prepare(`
    INSERT INTO permits (tower_id, tower_name, permit_number, permit_type,
      issued_date, expiry_date, issuing_authority, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)`);
  const info = stmt.run(tower_id, tower_name, permit_number, permit_type,
                        issued_date, expiry_date, issuing_authority, notes || '');
  res.status(201).json(db.prepare('SELECT * FROM permits WHERE id = ?').get(info.lastInsertRowid));
});

app.put('/api/permits/:id', (req, res) => {
  const { tower_id, tower_name, permit_number, permit_type, issued_date,
          expiry_date, issuing_authority, notes } = req.body;
  db.prepare(`
    UPDATE permits SET tower_id=?, tower_name=?, permit_number=?, permit_type=?,
      issued_date=?, expiry_date=?, issuing_authority=?, notes=?
    WHERE id=?`).run(tower_id, tower_name, permit_number, permit_type,
                     issued_date, expiry_date, issuing_authority, notes || '',
                     req.params.id);
  res.json(db.prepare('SELECT * FROM permits WHERE id = ?').get(req.params.id));
});

app.delete('/api/permits/:id', (req, res) => {
  db.prepare('DELETE FROM permits WHERE id = ?').run(req.params.id);
  res.json({ message: 'Deleted' });
});

// ── Seed ──────────────────────────────────────────────────────────────────────

app.post('/api/seed', (req, res) => {
  db.prepare('DELETE FROM leases').run();
  db.prepare('DELETE FROM permits').run();

  const leases = [
    ['TWR-001', 'KL Central Tower',           'Jalan Ampang, Kuala Lumpur',        'Ahmad bin Hassan',         'ahmad.hassan@example.com',   '2024-01-01', addDays(200),  2500, 3.0, '5-year lease, renewal option available'],
    ['TWR-002', 'Petaling Jaya North Tower',   'Jalan Utama, Petaling Jaya',        'Siti Rahimah binti Yusof', 'siti.rahimah@example.com',   '2021-06-01', addDays(60),   1800, 2.5, 'Renewal negotiation in progress'],
    ['TWR-003', 'Shah Alam Industrial Tower',  'Persiaran Industri, Shah Alam',     'Tan Boon Keat',            'tanbk@example.com',          '2020-03-15', addDays(20),   3200, 4.0, 'URGENT: Landlord requesting 15% rent increase'],
    ['TWR-004', 'Subang Jaya Rooftop Tower',   'SS15, Subang Jaya',                 'Rajesh Kumar',             'rajesh.kumar@example.com',   '2019-09-01', addDays(-15),  2100, 3.5, 'Lease expired — legal team reviewing options'],
    ['TWR-005', 'Cheras Hilltop Tower',        'Jalan Cheras, Kuala Lumpur',        'Lim Siew Lan',             'limsiewlan@example.com',     '2023-11-01', addDays(400),  2800, 3.0, 'New lease, favourable terms secured'],
  ];

  const permits = [
    ['TWR-001', 'KL Central Tower',          'DBKL/ANT/2024/001',   'Antenna Installation', '2024-01-15', addDays(270), 'Dewan Bandaraya KL (DBKL)',         'Annual renewal required'],
    ['TWR-002', 'Petaling Jaya North Tower', 'MBPJ/BLDG/2021/045',  'Building Permit',      '2021-07-01', addDays(45),  'Majlis Bandaraya Petaling Jaya',    'Renewal submitted, pending approval'],
    ['TWR-003', 'Shah Alam Industrial Tower','MBSA/ANT/2020/112',   'Antenna Installation', '2020-04-01', addDays(15),  'Majlis Bandaraya Shah Alam',        'URGENT: Renewal application must be submitted'],
    ['TWR-004', 'Subang Jaya Rooftop Tower', 'MPSJ/ZON/2019/089',   'Zoning Approval',      '2019-10-01', addDays(-10), 'Majlis Perbandaran Subang Jaya',    'Expired — legal review ongoing'],
    ['TWR-001', 'KL Central Tower',          'MCMC/FREQ/2024/330',  'Frequency License',    '2024-03-01', addDays(320), 'MCMC',                              '5G frequency allocation — B78 band'],
    ['TWR-005', 'Cheras Hilltop Tower',      'DBKL/BLDG/2023/201',  'Building Permit',      '2023-12-01', addDays(75),  'Dewan Bandaraya KL (DBKL)',         'Structure inspection passed'],
  ];

  const insLease = db.prepare(`INSERT INTO leases
    (tower_id,tower_name,location,landlord_name,landlord_contact,lease_start_date,lease_end_date,monthly_rent,escalation_rate,notes)
    VALUES (?,?,?,?,?,?,?,?,?,?)`);
  leases.forEach(l => insLease.run(...l));

  const insPerm = db.prepare(`INSERT INTO permits
    (tower_id,tower_name,permit_number,permit_type,issued_date,expiry_date,issuing_authority,notes)
    VALUES (?,?,?,?,?,?,?,?)`);
  permits.forEach(p => insPerm.run(...p));

  res.json({ message: 'Sample data loaded', leases: leases.length, permits: permits.length });
});

// ── Start ─────────────────────────────────────────────────────────────────────

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`\n  Tower Permit & Lease Manager`);
  console.log(`  Running at: http://localhost:${PORT}\n`);
});
