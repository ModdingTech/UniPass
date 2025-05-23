# Bus Pass Management System

A comprehensive Bus Pass Management System built using Flask and SQLite.

## Features

- User Authentication (Login/Register)
- Bus Route Management
- Pass Application System
- Payment Processing
- Pass Status Tracking
- Pass History Management
- Admin Dashboard

## Tech Stack

- Backend: Python Flask
- Database: SQLite
- Frontend: HTML, CSS, JavaScript
- Authentication: Werkzeug Security
- PDF Generation: ReportLab

## Project Structure

```
bus_pass_system/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── pass.py
│   │   ├── route.py
│   │   └── payment.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── admin.py
│   │   └── api.py
│   └── static/
│       ├── css/
│       ├── js/
│       └── images/
├── templates/
├── tests/
├── requirements.txt
└── run.py
```

## Setup Instructions

1. Install Python 3.8 or higher
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Initialize the database:
   ```bash
   python run.py init-db
   ```
4. Run the application:
   ```bash
   python run.py
   ```

## Database Schema

### Users Table
- id (PK)
- name
- email (UNIQUE)
- password_hash
- age
- address
- created_at

### Bus Routes Table
- id (PK)
- route_name
- from_place
- to_place
- fare
- created_at

### Pass Types Table
- id (PK)
- type_name
- duration_days
- base_fare
- created_at

### Bus Passes Table
- id (PK)
- user_id (FK)
- route_id (FK)
- pass_type_id (FK)
- status
- application_date
- start_date
- expiry_date
- payment_status

### Pass History Table
- id (PK)
- pass_id (FK)
- status
- status_change_date
- notes

### Payments Table
- id (PK)
- pass_id (FK)
- amount
- payment_date
- payment_status
- payment_method

## API Documentation

### User Authentication
- POST /api/auth/login
- POST /api/auth/register

### Pass Management
- POST /api/pass/apply
- GET /api/pass/history
- GET /api/pass/current
- POST /api/pass/cancel

### Admin Dashboard
- GET /api/admin/stats
- GET /api/admin/pending
- POST /api/admin/approve

## Security Features

- Password hashing using Werkzeug
- Input validation
- CSRF protection
- Session management
- Rate limiting
- Secure file uploads

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
