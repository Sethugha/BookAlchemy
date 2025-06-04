# 📚 Library Management Application

A **Library Management System** built with **Python**, featuring a Flask-based REST API and SQLAlchemy for ORM-backed database access. 
The frontend is designed with **JavaScript**, with a focus on **senior-friendly usability** through an intuitive and accessible UI.
Currently the frontend is not separated from the backend thus it is at time not necesary to implement CORS.
---

### 🛠️ Technologies Used

* **Backend:** Python, Flask, Flask-SQLAlchemy
* **Frontend:** Vanilla JavaScript, HTML5, CSS3
* **Database:** SQLite

---

### ✨ Features

* 🔧 **CRUD Operations** for books and authors
* 🧓 **Senior-friendly UI:** large buttons, clear labels, and simple navigation
* 🔗 **RESTful API** with clean endpoint structure
* 🗄️ **Persistent Storage** using SQLAlchemy ORM
* 📑 **Modular Codebase** with separation of concerns between UI, logic, and database access

---

### 🚀 Getting Started

#### Prerequisites

* Python 3.x
* pip / venv
  

#### Installation

```bash
git clone https://github.com/Sethugha/BookAlchemy.git
cd BookAlchemy
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

#### Running the Application

```bash
python3 app.py
```

Frontend files are located in `/static` and served directly via Flask.

---


➡️ Full API documentation in future at `/api/docs` 

---

### 👩‍💻 Future Enhancements

* [ ] User authentication and roles
* [ ] Search and filter functionality
* [ ] UI internationalization/localization
* [ ] Dark mode toggle

---

### 🧠 Inspiration & Accessibility

This project was designed with real-world usability in mind, especially for **older users** who benefit from simplified interfaces. The visual design avoids clutter and prioritizes legibility and ease of use.

---

Let me know if you want to add deployment instructions (e.g., for Heroku, Docker), a license, or contributor section!
