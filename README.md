# 📚 Library Management System - Django REST API

A comprehensive **Library Management System** built with Django and Django REST Framework, featuring JWT authentication, role-based permissions, book management, user profiles, and automated email verification.

![Django](https://img.shields.io/badge/Django-5.2.1-green)
![DRF](https://img.shields.io/badge/DRF-3.16.0-blue)
![JWT](https://img.shields.io/badge/JWT-Authentication-orange)
![Swagger](https://img.shields.io/badge/Swagger-Documentation-purple)
![Python](https://img.shields.io/badge/Python-3.9+-yellow)

---

## 🎯 Features Overview

### 🔐 Authentication & Security
- **JWT Authentication** with access and refresh tokens
- **Email verification** with OTP system
- **Token blacklisting** for secure logout
- **Role-based permissions** (Super Admin, Sub-Admin, User)
- **Password validation** and secure password change

### 📖 Book Management
- **Book Structure Management**: Add, update, delete books with metadata
- **Book Copy Tracking**: Individual copy management with status tracking
- **Book Issuance System**: Issue and return books with due date tracking
- **Borrowing History**: Complete transaction history for users

### 👤 User Management
- **User Registration**: Secure user registration with email verification
- **Profile Management**: Extended user profiles with personal information
- **Profile Pictures**: File upload support for user avatars
- **Customer Profiles**: Automatic profile creation via Django signals

### 👨‍💼 Sub-Admin System
- **Permission-based Access**: Granular permissions for sub-admins
- **CRUD Operations**: Full management of sub-admin accounts
- **Role Assignment**: Assign specific permissions to sub-admins

### 📚 API Documentation
- **Swagger/OpenAPI**: Interactive API documentation
- **Comprehensive Endpoints**: Well-documented REST API
- **Authentication Headers**: JWT Bearer token support

---

## 🛠️ Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| **Backend Framework** | Django | 5.2.1 |
| **API Framework** | Django REST Framework | 3.16.0 |
| **Authentication** | JWT (Simple JWT) | 5.5.0 |
| **Documentation** | drf-yasg | 1.21.10 |
| **Database** | PostgreSQL (Production) / SQLite (Development) | - |
| **Image Processing** | Pillow | 11.2.1 |
| **Email** | SMTP with TLS | - |
| **Testing** | Django Test Framework | - |

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python** 3.9 or higher
- **pip** (Python package installer)
- **Git** (for version control)
- **PostgreSQL** (for production) or **SQLite** (for development)
- **Virtual Environment** (recommended)

### System Requirements
- **RAM**: Minimum 2GB (4GB recommended)
- **Storage**: 1GB free space
- **OS**: Windows, macOS, or Linux

---

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
# Clone the repository
git clone https://github.com/your-username/library-management-system.git

# Navigate to project directory
cd library-management-system
```

### 2. Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the project root:

```bash
# Database Configuration
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=db.sqlite3
DATABASE_USER=
DATABASE_PASSWORD=
DATABASE_HOST=
DATABASE_PORT=

# Email Configuration (for OTP verification)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_PORT=587
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Django Secret Key (generate a new one for production)
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 5. Database Setup

```bash
# Create database migrations
python manage.py makemigrations

# Apply migrations to database
python manage.py migrate
```

### 6. Create Superuser

```bash
# Create admin user
python manage.py createsuperuser

# Follow the prompts to set username, email, and password
```

### 7. Run the Development Server

```bash
# Start the development server
python manage.py runserver

# The server will start at http://127.0.0.1:8000/
```

---

## 🌐 API Endpoints

### 🔐 Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/register/` | Register new user | No |
| `POST` | `/api/login/` | User login (JWT tokens) | No |
| `POST` | `/api/logout/` | Logout (blacklist token) | Yes |
| `POST` | `/api/new-access-token/` | Generate new access token | No |
| `POST` | `/api/verify_email/` | Verify email with OTP | No |

### 📚 Book Management Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/books/create/` | Create new book | Yes |
| `GET` | `/books/` | List all books | Yes |
| `GET` | `/books/<id>/` | Get book details | Yes |
| `PATCH` | `/books/update/<id>/` | Update book | Yes |
| `DELETE` | `/books/delete/<id>/` | Delete book | Yes |
| `POST` | `/books/issue/<book_structure_id>/` | Issue a book | Yes |
| `POST` | `/books/return/` | Return a book | Yes |
| `GET` | `/books/user/orders/` | User's borrowed books | Yes |

### 👤 User Profile Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/user-profile/details/<user_id>/` | Get user profile | Yes |
| `PATCH` | `/user-profile/update/<user_id>/` | Update profile | Yes |
| `PATCH` | `/user-profile/change-password/<user_id>/` | Change password | Yes |

### 👨‍💼 Sub-Admin Management Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/sub-admin/create/` | Create sub-admin | Yes |
| `GET` | `/sub-admin/` | List all sub-admins | Yes |
| `GET` | `/sub-admin/<id>/` | Get sub-admin details | Yes |
| `PATCH` | `/sub-admin/update/<id>/` | Update sub-admin | Yes |
| `DELETE` | `/sub-admin/delete/<id>/` | Delete sub-admin | Yes |

---

## 🔐 Authentication & Permissions

### JWT Token Configuration

```python
# Token lifetime settings
ACCESS_TOKEN_LIFETIME = 5 minutes
REFRESH_TOKEN_LIFETIME = 1 day
ROTATE_REFRESH_TOKENS = True
BLACKLIST_AFTER_ROTATION = True
```

### Role-Based Permissions

#### 🏆 Super Admin
- Full CRUD access to all resources
- Can manage sub-admins and their permissions
- Access to admin panel

#### 👨‍💼 Sub-Admin
- Limited permissions based on assigned groups
- Can manage books (if permission granted)
- Can view user profiles (if permission granted)

#### 👤 Regular User
- Can view available books
- Can issue and return books
- Can manage own profile
- Can change password

### Permission Examples

```python
# Book permissions
'books.read_book'
'books.create_book'
'books.update_book'
'books.delete_book'

# User permissions
'user_app.view_customercreate'
'user_app.change_customercreate'
```

---

## 📖 API Usage Examples

### 1. User Registration

```bash
curl -X POST http://127.0.0.1:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepassword123",
    "confirm_password": "securepassword123"
  }'
```

### 2. User Login

```bash
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "securepassword123"
  }'
```

### 3. Create a Book (with JWT token)

```bash
curl -X POST http://127.0.0.1:8000/books/create/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "publisher": "Scribner",
    "isbn": "978-0743273565",
    "publication_year": 1925,
    "genre": "Fiction"
  }'
```

### 4. Issue a Book

```bash
curl -X POST http://127.0.0.1:8000/books/issue/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
      "issue_date": "2025-06-25",
      "return_date": "2025-06-25"
  }'
```

---

## 📚 Database Models

### Core Models

#### BookStructure
```python
- title: CharField
- author: CharField
- publisher: CharField
- isbn: CharField
- publication_year: IntegerField
- genre: CharField
- created_at: DateTimeField
- updated_at: DateTimeField
```

#### BookCopy
```python
- book_instance: ForeignKey(BookStructure)
- copy_number: IntegerField
- status: CharField (Available, Issued, Lost, Damaged)
- created_at: DateTimeField
- updated_at: DateTimeField
```

#### IssueBook
```python
- book: ForeignKey(BookCopy)
- user: ForeignKey(User)
- issue_date: DateTimeField
- due_date: DateField
- returned_on: DateTimeField (nullable)
- is_returned: BooleanField
```

#### CustomerCreate
```python
- user: OneToOneField(User)
- first_name: CharField
- last_name: CharField
- phone: CharField
- age: IntegerField
- profile_picture: ImageField
- is_email_verified: BooleanField
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=library_db
DATABASE_USER=your_db_user
DATABASE_PASSWORD=your_db_password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Email Settings
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_PORT=587
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

### JWT Settings

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

---

## 📖 API Documentation

### Swagger UI

Access the interactive API documentation at:
```
http://127.0.0.1:8000/swagger/
```

### Features
- **Interactive Testing**: Test endpoints directly from the browser
- **Authentication**: JWT Bearer token support
- **Request/Response Examples**: Detailed examples for each endpoint
- **Schema Validation**: Automatic request/response validation


---

## 📝 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🏆 Acknowledgments

- Django REST Framework team
- Simple JWT contributors
- drf-yasg maintainers

---

**Made with ❤️ using Django and Django REST Framework**
