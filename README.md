# Flask CRUD App with SQLite & React

## Description

This is a simple Flask CRUD application that manages a list of books stored in a **SQLite** database. The app allows users to create, read, update, and delete books through a React frontend.

## Project Structure

```
simple_book_management/
├── Client/                         # React frontend
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── README.md
├── Server/                         # Flask + SQLite backend
│   ├── app.py
│   ├── books.db                    # SQLite database file (auto-created)
│   ├── requirements.txt
│   ├── venv/
│   └── tests/
└── README.md
```

## Prerequisites

Ensure the following are installed on your system:

- **Python 3.8+**
- **Node.js 16+** (for React frontend)
- **pip** (Python package manager)
- **npm** (Node package manager)

> No external database installation required — SQLite is built into Python.

## Backend Setup (Flask + SQLite)

1. **Navigate to the server directory:**

   ```bash
   cd Server
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate        # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Flask application:**

   ```bash
   python3 app.py
   # Or using the venv directly:
   venv/bin/python3 app.py
   ```

   The backend will start on **http://localhost:5001**

   The `books.db` SQLite file is created automatically on first run — no manual database setup needed.

## Frontend Setup (React)

1. **Navigate to the client directory:**

   ```bash
   cd Client
   ```

2. **Install Node.js dependencies:**

   ```bash
   npm install
   ```

3. **Start the React development server:**

   ```bash
   npm run dev
   ```

   The frontend will start on **http://localhost:5173**

## Usage

1. Start the backend server (Flask on port **5001**)
2. Start the frontend client (React on port **5173**)
3. Open your browser and navigate to **http://localhost:5173**

You should see the book management interface where you can:

- View all books
- Add new books
- Edit existing books
- Delete books

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Retrieve all books |
| `POST` | `/create` | Create a new book |
| `PUT` | `/update/<id>` | Update a book by ID |
| `DELETE` | `/delete/<id>` | Delete a book by ID |

### Example Requests

#### Get All Books
```
GET http://localhost:5001/
```

#### Create a Book
```
POST http://localhost:5001/create
Content-Type: application/json

{
  "publisher": "O'Reilly",
  "name": "Learning Flask",
  "date": "2024-10-11",
  "Cost": 399.99
}
```

#### Update a Book
```
PUT http://localhost:5001/update/1
Content-Type: application/json

{
  "publisher": "Updated Publisher",
  "name": "Updated Book Name",
  "date": "2024-12-01",
  "Cost": 499.99
}
```

#### Delete a Book
```
DELETE http://localhost:5001/delete/1
```

## Technologies Used

### Backend
- **Flask** — Web framework
- **Flask-CORS** — Cross-Origin Resource Sharing
- **SQLite** — Lightweight file-based database (built into Python)

### Frontend
- **React** — UI framework
- **Axios** — HTTP client for API calls
- **Bootstrap** — Styling

## Testing

### Pytest (Unit Tests)

```bash
bash Server/run-pytest.sh
```

### Newman (API Tests)

```bash
cd Server/tests/postman_newman
./run-newman-tests.sh
```

### Playwright (E2E Tests)

```bash
cd Client
npx playwright test
```

Test reports are located in:
- `Server/tests/pytest/pytest-report.json`
- `Server/tests/postman_newman/newman-report.html`
- `Client/playwright-report/index.html`

## Troubleshooting

### Backend won't start — module not found
Make sure the virtual environment is activated before running:
```bash
source Server/venv/bin/activate
python3 Server/app.py
```

### Frontend can't connect to backend
- Verify the Flask server is running on port **5001**
- Check that CORS is enabled (it is by default via `flask-cors`)

### Virtual environment issues
```bash
# Recreate the venv if needed
rm -rf Server/venv
python3 -m venv Server/venv
source Server/venv/bin/activate
pip install -r Server/requirements.txt
```

## License

This project is for educational purposes.
