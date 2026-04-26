# Multi-Tenant Appointment Scheduling SaaS

## 👋 Overview

This is a **backend-focused SaaS application** for managing appointments across multiple businesses (tenants).

The system allows different businesses to:
- Manage services
- Manage staff
- Create and manage appointment slots
- Handle bookings

The core focus of this project is **multi-tenant architecture, backend design, and data integrity**, rather than frontend/UI.

---

## 🎯 Key Features

- Multi-tenant system using a **single database**
- Role-based authentication (**Admin, Staff, User**) using JWT
- Service management per business
- Staff-based appointment slot creation
- Booking system with conflict prevention
- Flash/toast messages for user feedback
- Dockerized setup for easy deployment

---

## 🏗️ Tech Stack

- **Backend:** Flask (Python)
- **Database:** PostgreSQL (Render - cloud hosted)
- **ORM:** SQLAlchemy
- **Authentication:** Flask-JWT-Extended (cookies)
- **Containerization:** Docker + Docker Compose
- **Frontend:** Basic HTML + CSS (minimal UI)

---

## 🧠 Multi-Tenancy Design

This project uses a **shared database, shared schema** approach.

### How it works:
- Every table includes a `tenant_id`
- All queries are filtered by `tenant_id`
- Each business only accesses its own data

### Why this approach:
- Cost-efficient
- Scalable for multiple tenants
- Common in real SaaS products

---

## 🗄️ Database Models (Simplified)

- **Tenant** → represents a business
- **User** → authentication & roles
- **Staff** → staff members
- **Service** → services offered by tenant
- **MasterService** → global service list
- **Appointment** → slots (available / booked)

---

## ⏱️ Appointment Flow

### Slot Creation (Staff)
1. Select date & time
2. Select service
3. System checks for duplicate slot
4. Slot is created

### Booking (User)
1. Select available slot
2. System verifies availability
3. Slot is booked

---

## 🔒 Data Integrity

- Duplicate slots prevented using:
  ```
  (tenant_id, staff_id, service_id, time)
  ```
- Validation done at:
  - Application level (manual check)
  - Database level (unique constraint)

---

## 🐳 Running with Docker (Recommended)

### Start the app

```bash
docker-compose up --build
```

### Open in browser

```
http://localhost:5000
```

### Stop the app

```bash
docker-compose down
```

---

## 💻 Running Without Docker

```bash
python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
python app.py
```

---

## 🔐 Roles

- **Admin**
  - Manage services

- **Staff**
  - Create/manage slots

- **User**
  - Book appointments

---

## 🚧 Limitations

- Minimal UI (not frontend-focused)
- No payments/subscriptions
- No background jobs
- No caching (Redis not added yet)
- No API documentation

---

## 🚀 Future Improvements

- Redis (caching & slot locking)
- Kafka / Celery (async processing)
- Better RBAC system
- API-first architecture
- Nginx + Gunicorn setup
- Rate limiting

---

## 🧠 What This Project Demonstrates

- Multi-tenant backend design
- Database constraints & integrity
- Handling duplicate bookings
- Docker-based development workflow
- JWT authentication system

---

## 📌 Note

This project is built for **learning and demonstrating backend system design concepts**, not as a production-ready SaaS.
