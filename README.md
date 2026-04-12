# Barangay Mainit, Looc — Record Request System (Django demo)

Lightweight Django prototype for an in-memory **Barangay Record Request System**. Request records live in a Python module (`data_store.py`) while the development server runs; they are cleared when the process stops.

## Requirements

- Python 3.10+ (tested with the project’s local virtual environment)

## Run locally

From the project root (`BARANGAY RECORD REQUEST SYSTEM`):

1. **Create and activate a virtual environment** (if you have not already):

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

   On Windows PowerShell:

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Apply Django’s built-in migrations** (sessions and related apps; request data itself is still in-memory only):

   ```bash
   python manage.py migrate
   ```

4. **Start the server:**

   ```bash
   python manage.py runserver
   ```

5. Open **http://127.0.0.1:8000/** in your browser.

## Using the demo

- **Public:** Submit document requests and track them with the **reference number** shown after submission (no login).
- **Admin dashboard:** Go to **Admin** in the navigation, then sign in with username **`admin`** and password **`admin`**. From the dashboard you can approve, reject, set requests to **ready for pickup**, or **delete all** demo rows.

Django’s built-in admin UI is mounted at **http://127.0.0.1:8000/django-admin/** if you create a superuser; the barangay workflow uses the custom `/admin/login/` and `/admin/dashboard/` routes instead.

## Developer’s note

This is a **demo system**: no real database for citizen requests, **local only**, not suitable for production.
