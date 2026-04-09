# Tower Permit & Lease Manager

Aplikasi web sederhana untuk mengelola perjanjian sewa lahan dan permit menara telekomunikasi. Dirancang untuk operator telco dalam memantau tanggal jatuh tempo sewa dan permit, serta menerima peringatan otomatis sebelum deadline.

---

## Daftar Isi

- [Fitur](#fitur)
- [Tech Stack](#tech-stack)
- [Struktur Proyek](#struktur-proyek)
- [Cara Menjalankan](#cara-menjalankan)
- [API Reference](#api-reference)
- [Panduan Penggunaan](#panduan-penggunaan)
- [Logika Status & Alert](#logika-status--alert)
- [Contoh Data](#contoh-data)

---

## Fitur

- **Dashboard** — Summary bar ringkas untuk sewa dan permit (total, aktif, akan berakhir, kadaluarsa), disusul alert feed berbentuk notification card yang diurutkan dari yang paling mendesak
- **Greeting kontekstual** — Sapaan pagi/siang/sore otomatis, dengan pesan berbeda jika ada item urgent
- **Alert Feed** — Setiap item yang hampir kadaluarsa ditampilkan sebagai card dengan garis warna di sisi kiri (merah = urgent/expired, kuning = dalam 90 hari)
- **Manajemen Sewa Lahan** — CRUD lengkap untuk perjanjian sewa lahan (tower ID, nama landlord, kontak, tanggal sewa, harga bulanan, eskalasi harga)
- **Manajemen Permit** — CRUD lengkap untuk permit menara (nomor permit, jenis permit, otoritas penerbit, tanggal berlaku dan kadaluarsa)
- **Status Badge** — Indikator warna (hijau/kuning/merah) berdasarkan sisa hari berlaku
- **Sample Data** — Data contoh 5 menara dengan lokasi Malaysia, dimuat lewat tombol "Load sample data" di bagian bawah sidebar

---

## Tech Stack

| Layer     | Teknologi                  |
|-----------|----------------------------|
| Backend   | Node.js + Express.js       |
| Database  | SQLite (via better-sqlite3)|
| Frontend  | HTML + CSS + Vanilla JS    |
| API       | REST JSON                  |

> Tidak memerlukan framework frontend (React/Vue) maupun database server (PostgreSQL/MySQL). Cukup Node.js dan satu file database SQLite.

---

## Struktur Proyek

```
tower-lease-manager/
├── server.js           # Server utama — Express app, routes, seed data
├── package.json        # Konfigurasi Node.js dan dependencies
├── tower_lease.db      # File database SQLite (dibuat otomatis saat pertama kali dijalankan)
├── static/
│   └── index.html      # Single-page frontend (UI, CSS, JavaScript)
└── README.md
```

> File `database.py`, `models.py`, `schemas.py`, `main.py`, `seed.py`, dan `requirements.txt` adalah sisa implementasi Python/FastAPI sebelumnya dan tidak digunakan.

---

## Cara Menjalankan

### Prasyarat

- [Node.js](https://nodejs.org/) versi 18 atau lebih baru

### Langkah Instalasi

**1. Clone atau download proyek**

```bash
git clone <url-repo>
cd tower-lease-manager
```

**2. Install dependencies**

```bash
npm install
```

**3. Jalankan server**

```bash
npm start
```

**4. Buka di browser**

```
http://localhost:3000
```

**5. Muat data contoh** *(opsional)*

Klik tombol **"Load sample data"** di bagian bawah sidebar untuk mengisi database dengan 5 data sewa dan 6 data permit contoh.

---

## API Reference

Base URL: `http://localhost:3000`

### Dashboard

| Method | Endpoint        | Deskripsi                                           |
|--------|-----------------|-----------------------------------------------------|
| GET    | `/api/dashboard` | Statistik ringkasan dan daftar alert deadline      |

**Contoh Response `/api/dashboard`:**
```json
{
  "leases": {
    "total": 5,
    "active": 2,
    "expiring_soon": 2,
    "expired": 1
  },
  "permits": {
    "total": 6,
    "active": 2,
    "expiring_soon": 3,
    "expired": 1
  },
  "alerts": [
    {
      "type": "Lease",
      "tower_id": "TWR-004",
      "name": "Subang Jaya Rooftop Tower",
      "detail": "Landlord: Rajesh Kumar",
      "contact": "rajesh.kumar@example.com",
      "days_left": -16,
      "deadline": "2026-03-25"
    }
  ]
}
```

---

### Sewa Lahan (Leases)

| Method | Endpoint            | Deskripsi               |
|--------|---------------------|-------------------------|
| GET    | `/api/leases`        | Ambil semua data sewa  |
| POST   | `/api/leases`        | Tambah data sewa baru  |
| PUT    | `/api/leases/:id`    | Update data sewa       |
| DELETE | `/api/leases/:id`    | Hapus data sewa        |

**Body Request (POST / PUT):**
```json
{
  "tower_id": "TWR-001",
  "tower_name": "KL Central Tower",
  "location": "Jalan Ampang, Kuala Lumpur",
  "landlord_name": "Ahmad bin Hassan",
  "landlord_contact": "ahmad.hassan@example.com",
  "lease_start_date": "2024-01-01",
  "lease_end_date": "2026-12-31",
  "monthly_rent": 2500.00,
  "escalation_rate": 3.0,
  "notes": "5-year lease, renewal option available"
}
```

---

### Permit

| Method | Endpoint             | Deskripsi                |
|--------|----------------------|--------------------------|
| GET    | `/api/permits`        | Ambil semua data permit |
| POST   | `/api/permits`        | Tambah data permit baru |
| PUT    | `/api/permits/:id`    | Update data permit      |
| DELETE | `/api/permits/:id`    | Hapus data permit       |

**Body Request (POST / PUT):**
```json
{
  "tower_id": "TWR-001",
  "tower_name": "KL Central Tower",
  "permit_number": "DBKL/ANT/2024/001",
  "permit_type": "Antenna Installation",
  "issued_date": "2024-01-15",
  "expiry_date": "2026-01-14",
  "issuing_authority": "Dewan Bandaraya KL (DBKL)",
  "notes": "Annual renewal required"
}
```

**Jenis Permit yang Tersedia:**
- `Antenna Installation`
- `Building Permit`
- `Zoning Approval`
- `Frequency License`
- `Environmental Clearance`
- `Other`

---

### Seed Data

| Method | Endpoint    | Deskripsi                                        |
|--------|-------------|--------------------------------------------------|
| POST   | `/api/seed`  | Reset database dan isi ulang dengan data contoh |

> **Perhatian:** Endpoint ini akan menghapus semua data yang ada.

---

## Panduan Penggunaan

### Dashboard

Halaman utama terdiri dari dua bagian:

- **Summary bar** — dua baris ringkas (sewa & permit) yang menampilkan jumlah total, aktif, akan berakhir, dan kadaluarsa secara sekilas
- **Alert feed** — daftar notification card untuk semua item yang kadaluarsa dalam 90 hari ke depan, diurutkan dari yang paling mendesak. Card berwarna merah menandakan item sudah kadaluarsa atau sisa kurang dari 30 hari; kuning untuk 31–90 hari

### Menambah Data Sewa Baru

1. Klik menu **Land Leases** di sidebar
2. Klik tombol **Add Lease**
3. Isi form yang muncul, lalu klik **Save lease**

### Menambah Permit Baru

1. Klik menu **Permits** di sidebar
2. Klik tombol **Add Permit**
3. Isi form yang muncul, lalu klik **Save permit**

### Mengedit atau Menghapus Data

- Klik **Edit** pada baris yang ingin diubah, lakukan perubahan, lalu klik **Save**
- Klik **Delete** untuk menghapus — akan muncul konfirmasi sebelum data benar-benar dihapus

### Memantau Alert

Kembali ke **Dashboard** untuk melihat semua deadline yang mendekat. Sapaan di bagian atas akan berubah secara otomatis jika ada item yang mendesak.

---

## Logika Status & Alert

Status ditentukan berdasarkan jumlah hari tersisa dari tanggal hari ini:

| Kondisi                  | Badge              | Warna  | Alert Feed       |
|--------------------------|--------------------|--------|------------------|
| Lebih dari 90 hari       | `Active`           | Hijau  | Tidak muncul     |
| 31 — 90 hari             | `X days left`      | Kuning | Garis kiri kuning|
| 1 — 30 hari              | `Urgent — X days`  | Merah  | Garis kiri merah |
| 0 hari atau sudah lewat  | `Expired`          | Merah  | Garis kiri merah |

Alert Feed pada Dashboard hanya menampilkan item dengan sisa **90 hari atau kurang**, diurutkan dari yang paling mendesak. Item yang sudah kadaluarsa muncul paling atas.

---

## Contoh Data

Data sample yang dimuat melalui tombol **"Load Sample Data"** mencakup menara-menara fiktif di Malaysia:

### Sewa Lahan

| Tower ID | Nama Menara               | Landlord              | Status          |
|----------|---------------------------|-----------------------|-----------------|
| TWR-001  | KL Central Tower          | Ahmad bin Hassan      | Active          |
| TWR-002  | Petaling Jaya North Tower | Siti Rahimah          | Expiring (~60d) |
| TWR-003  | Shah Alam Industrial Tower| Tan Boon Keat         | Urgent (~20d)   |
| TWR-004  | Subang Jaya Rooftop Tower | Rajesh Kumar          | Expired         |
| TWR-005  | Cheras Hilltop Tower      | Lim Siew Lan          | Active          |

### Permit

| Tower ID | Permit No.           | Jenis                | Otoritas         | Status          |
|----------|----------------------|----------------------|------------------|-----------------|
| TWR-001  | DBKL/ANT/2024/001    | Antenna Installation | DBKL             | Active          |
| TWR-002  | MBPJ/BLDG/2021/045   | Building Permit      | MBPJ             | Expiring (~45d) |
| TWR-003  | MBSA/ANT/2020/112    | Antenna Installation | MBSA             | Urgent (~15d)   |
| TWR-004  | MPSJ/ZON/2019/089    | Zoning Approval      | MPSJ             | Expired         |
| TWR-001  | MCMC/FREQ/2024/330   | Frequency License    | MCMC             | Active          |
| TWR-005  | DBKL/BLDG/2023/201   | Building Permit      | DBKL             | Expiring (~75d) |
