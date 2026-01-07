# Multi-Tenant Appointment Scheduling System

## 👋 About This Project

This project is a **backend-focused SaaS application** built to practice and demonstrate **real-world system design and database concepts** using Python, Flask, and PostgreSQL.

Instead of focusing on UI, the emphasis here is on **how real SaaS products are designed internally** — especially how they handle **multiple businesses (tenants)** safely and efficiently using a single database.

This repository is meant to reflect the kind of thinking expected from a **backend or platform engineer**.

---

## 🤔 What Problem Does This Solve?

Many service-based businesses like salons, clinics, or consultants need a way to:

* Manage staff members
* Offer multiple services
* Define working hours and availability
* Allow customers to book appointments

Building separate systems for each business doesn’t scale. A SaaS solution should allow **many businesses to use the same platform**, without ever seeing each other’s data.

That’s exactly what this project is about.

---

## 🎯 What This Project Focuses On

This project is intentionally designed to highlight:

* Multi-tenant database design
* Clean relational schema modeling
* Data isolation using `tenant_id`
* Preventing double bookings
* Transaction-safe operations
* Scalability and performance thinking

UI, frontend frameworks, and styling are intentionally kept out of scope.

---

## 🏗️ High-Level Architecture

```
Client (API Consumer)
        ↓
Flask REST API
        ↓
PostgreSQL (Single Database, Multiple Tenants)
```

* Backend: Flask (Python)
* Database: PostgreSQL
* ORM: SQLAlchemy (with raw SQL where needed)
* Architecture style: Monolithic (by design, for clarity)

---

## 🧩 How Multi-Tenancy Works Here

Each business is treated as a **tenant**.

Instead of separate databases per business, this system uses:

**One database + one schema + a `tenant_id` column in every table**

### Data Isolation Rules

* Every table includes `tenant_id`
* Every query is scoped by `tenant_id`
* Indexes are optimized for tenant-based access
* Foreign keys ensure tenant-level consistency

This is a widely used approach in real SaaS products because it balances **cost, scalability, and maintainability**.

---

## 🗄️ Database Design Overview

The database is designed first, before writing APIs.

### Core Tables

* `tenants` – represents a business
* `users` – owners, staff, and customers
* `services` – services offered by a tenant
* `staff` – staff members linked to users
* `availability` – staff working hours
* `appointments` – booked time slots

### Design Principles

* UUIDs as primary keys
* Strong foreign key relationships
* Constraints to enforce data integrity
* Indexes to support scale

---

## ⏱️ Appointment Booking Flow

When an appointment is booked:

1. The tenant and staff are validated
2. Staff availability is checked
3. Existing appointments are checked for overlap
4. The booking is created inside a database transaction

This ensures:

* No double booking
* Safe concurrent requests
* Consistent data even under load

---

## 📂 Project Structure

```
multi-tenant-appointment-saas/
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── models/
│   └── routes/
│
├── database/
│   ├── schema.sql
│   ├── constraints.sql
│   └── indexes.sql
│
├── migrations/
├── SYSTEM_DESIGN.md
├── requirements.txt
├── run.py
└── README.md
```

---

## 🚀 Running the Project Locally

### Requirements

* Python 3.10+
* PostgreSQL
* Virtual environment (recommended)

### Setup

```bash
git clone <repo-url>
cd multi-tenant-appointment-saas

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

Database setup and schema evolution are documented inside the `database/` folder.

---

## 🧠 Why This Project Is Interview-Friendly

This repository makes it easy to explain:

* How multi-tenant SaaS systems work
* Why `tenant_id` based isolation is used
* How databases help prevent race conditions
* How appointment conflicts are avoided
* How the system can scale to thousands of businesses

---

## 🔮 Possible Future Improvements

* Role-based access control (RBAC)
* Payments and subscriptions
* Audit logging
* Database partitioning
* Caching with Redis

---
