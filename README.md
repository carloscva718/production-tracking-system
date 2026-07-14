# 🏭 Production Tracking System

A web application developed with **Python, Flask and MySQL** to digitize and monitor manufacturing processes using **QR codes**.

The objective of this project is to replace manual paper-based production records with a real-time digital system that tracks production batches throughout the factory.

---

## 📸 Screenshots

> Screenshots will be added as the project progresses.

| Login | Production Panel |
|-------|------------------|
| ![](screenshots/login.png) | ![](screenshots/menu-produccion.png) |

| New Batch | Dashboard |
|-----------|-----------|
| ![](screenshots/nuevo-lote.png) | ![](screenshots/dashboard.png) |

---

# ✨ Features

- 🔐 User authentication
- 👥 Role-based access control
- 📦 Production batch management
- 📱 Automatic QR code generation
- 🏭 Workstation selection
- ⏱️ Production time tracking
- 📊 Dashboard for production monitoring
- 💾 MySQL database integration

---

# 👤 User Roles

### 👷 Operator

- Login
- Select workstation
- Scan QR code
- Start production
- Finish production

---

### 📋 Production Manager

- Create production batches
- Generate QR codes
- View production batches

---

### 📊 Management

- Production dashboard
- Production monitoring
- Statistics and reports

---

### ⚙️ Administrator

- Full access
- User management
- System administration

---

# 🛠️ Technologies

- Python
- Flask
- MySQL
- HTML5
- CSS3
- Jinja2
- Werkzeug
- QRCode

---

# 🗄️ Database

Main tables:

- empleado
- lote
- maquina
- registro_trabajo

---

# 📂 Project Structure

```text
production-tracking-system/
│
├── app.py
├── crear_usuario.py
├── requirements.txt
├── README.md
│
├── static/
│
├── templates/
│
├── qr_generados/
│
└── screenshots/
```

---

# 🔄 Application Workflow

```text
Login
   │
   ▼
Select Workstation
   │
   ▼
Scan QR Code
   │
   ▼
Start Production
   │
   ▼
Finish Production
   │
   ▼
Production Dashboard
```

---

# 🎯 Project Purpose

This project was developed to demonstrate the implementation of a production tracking system capable of:

- Tracking production batches in real time.
- Recording manufacturing times.
- Monitoring workstation performance.
- Digitizing manual production processes.
- Providing production metrics through dashboards.

---

# 🚧 Project Status

**Currently under development**

### Implemented

- User authentication
- Role management
- Batch creation
- QR code generation
- Production registration
- Dashboard

### Planned

- Advanced dashboard
- Reports
- Production statistics
- User administration
- PDF report generation
- Production analytics

---

# 🚀 Installation

```bash
git clone https://github.com/carloscva718/production-tracking-system.git

cd production-tracking-system

pip install -r requirements.txt

python app.py
```

> **Note:** This repository is intended as a portfolio project. Database configuration and deployment are not included.

---

# 👨‍💻 Author

**Carlos Carrasco Gallego**

Portfolio project developed to demonstrate backend and full-stack development skills using **Python, Flask and MySQL**.

---

## 📄 License

This project is available under the MIT License.