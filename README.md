# 📚 Book Management System (Full-Stack)

> **Flask API + React Frontend** using **Microsoft SQL Server (MSSQL)**.
> A complete system to manage digital library records with User Authentication (JWT).

---

## 📋 Table of Contents

1. [⚡ Quick Start (5 Minutes)](#-quick-start-5-minutes)
2. [✅ Prerequisites](#-prerequisites)
3. [🛠️ Step-by-Step Backend Setup](#️-step-by-step-backend-setup)
4. [💻 Step-by-Step Frontend Setup](#-step-by-step-frontend-setup)
5. [🚀 Running the Application](#-running-the-app)
6. [🔍 API Documentation](#-api-endpoints)
7. [🧪 Testing](#-testing)
8. [❓ Troubleshooting](#-troubleshooting)

---

## ⚡ Quick Start (5 Minutes)

### 1. Start SQL Server (Docker)
```bash
docker run -d --name mssql -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=Sakshi@mssql" -p 1433:1433 mcr.microsoft.com/mssql/server:2022-latest
```

### 2. Start Backend
```bash
cd Server
python3 -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
python3 app.py
```

### 3. Start Frontend
```bash
cd Client
npm install
npm run dev
```

---

## ✅ Prerequisites

Before starting, ensure you have the following installed:

| Tool | Required Version | Purpose |
|------|------------------|---------|
| **Python** | 3.10+ | Backend API |
| **Node.js** | 18+ or 21+ | Frontend UI |
| **Docker** | Latest | Running SQL Server |
| **ODBC Driver**| 17 or 18 | Database Connection |

---

## 🛠️ Step-by-Step Backend Setup

### STEP 1: Run MSSQL Database
The easiest way to run SQL Server is via Docker. Open your terminal and run:

```bash
docker run -d \
  --name mssql \
  -e "ACCEPT_EULA=Y" \
  -e "MSSQL_SA_PASSWORD=Sakshi@mssql" \
  -p 1433:1433 \
  mcr.microsoft.com/mssql/server:2022-latest
```
*Wait about 15 seconds for the database to initialize.*

### STEP 2: Create the Database
The Flask app looks for a database named `BookManagement`. You need to create it once:

**Linux/Mac:**
```bash
docker exec -it mssql /opt/mssql-tools/bin/sqlcmd \
   -S localhost -U sa -P Sakshi@mssql \
   -Q "CREATE DATABASE BookManagement"
```

**Windows (PowerShell):**
```powershell
docker exec -it mssql /opt/mssql-tools/bin/sqlcmd `
   -S localhost -U sa -P Sakshi@mssql `
   -Q "CREATE DATABASE BookManagement"
```

### STEP 3: Python Environment
Navigate to the `Server` folder and set up your virtual environment:

```bash
cd Server
python3 -m venv venv

# Activate Environment
source venv/bin/activate # Windows: .\venv\Scripts\activate

# Install Dependencies
pip install -r requirements.txt
```

### STEP 4: Configuration (.env)
Create a `.env` file inside the `Server` folder to store your secrets:

```env
JWT_SECRET_KEY=your_random_secret_string
MSSQL_CONNECTION_STRING=DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=BookManagement;UID=sa;PWD=Sakshi@mssql;TrustServerCertificate=yes;Encrypt=no;
```

---

## 💻 Step-by-Step Frontend Setup

1. **Navigate to the Client folder:**
   ```bash
   cd Client
   ```

2. **Install Node modules:**
   ```bash
   npm install
   ```

3. **Configure API URL:**
   Ensure your frontend points to `http://localhost:5000` (the default Flask port).

---

## 🚀 Running the App

### 1. Start the Flask Server
```bash
cd Server
source venv/bin/activate
python3 app.py
```
*The server will run at `http://localhost:5000`. It will automatically create the necessary tables (`book` and `users`) on its first run.*

### 2. Start the React UI
```bash
cd Client
npm run dev
```
*The UI will run at `http://localhost:5173`.*

---

## 🔍 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/register` | Create a new user account |
| `POST` | `/login` | Login to receive a JWT Token |
| `GET` | `/me` | Get profile of logged-in user |

### Book Management (Requires JWT Token)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Fetch all books |
| `POST` | `/create` | Add a new book |
| `PUT` | `/update/<id>` | Update an existing book |
| `DELETE` | `/delete/<id>` | Remove a book |

---

## 🧪 Testing

### 1. Backend Unit Tests (Pytest)
```bash
cd Server
bash run-pytest.sh
```

### 2. API Integration Tests (Newman)
```bash
cd Server/tests/postman_newman
./run-newman-tests.sh
```

### 3. End-to-End Tests (Playwright)
```bash
cd Client
npx playwright test
```

---

## ❓ Troubleshooting

### "Login failed for user 'sa'"
* **Cause:** Incorrect password or Docker container not ready.
* **Fix:** Ensure the `MSSQL_SA_PASSWORD` in your Docker command matches the `PWD` in your connection string.

### "ModuleNotFoundError: No module named 'pyodbc'"
* **Cause:** Virtual environment not activated.
* **Fix:** Run `source venv/bin/activate` before starting the app.

### "ODBC Driver Not Found"
* **Cause:** The SQL Server driver is not installed on your host OS.
* **Fix:**
    * **Ubuntu:** `sudo apt-get install msodbcsql18`
    * **Windows:** Download "Microsoft ODBC Driver for SQL Server" from the official Microsoft site.

### "CORS Error" in Browser
* **Cause:** Frontend trying to hit a different port/origin.
* **Fix:** The backend is configured with `flask-cors`. Ensure you are hitting the correct URL: `http://localhost:5000`.

---

*This project is for educational purposes.*
### for docker compose 
