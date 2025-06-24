# Library Management System - Django API

This project is a **Library Management System** built using Django and Django REST Framework. It includes APIs for managing books, issuing/returning them, handling user profiles, and sub-admin permissions.

---

## 📁 Features

### 📖 Book Management

* Add, update, delete books (`BookStructure` model).
* Track individual copies with unique statuses (`BookCopy`).
* API to issue and return books.

### 📅 Book Transactions

* `IssueBook` model records book issuance.
* Track due dates, return dates, and borrowing history.

### 👤 User & Customer Profile

* Django's default `User` model extended with `CustomerCreate`.
* Profile picture, phone, age, and other personal info.
* Password change and profile update endpoints.

### 👨‍💼 Sub-Admin Management

* Sub-admins have limited access controlled via Django groups and permissions.
* APIs to create, update, view, and delete sub-admins.

### 📑 Documentation

* **Swagger/OpenAPI** support using `drf-yasg`.

---

## ⚙️ Setup Instructions

### Prerequisites

* Python >= 3.9
* pipenv / venv (recommended)
* PostgreSQL (optional, default SQLite)

### Installation

```bash
# Clone the repo
$ git clone https://github.com/your-username/library-management-system.git
$ cd library-management-system

# Create and activate virtual environment
$ python -m venv venv
$ source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
$ pip install -r requirements.txt

# Apply migrations
$ python manage.py makemigrations
$ python manage.py migrate

# Create superuser
$ python manage.py createsuperuser

# Run development server
$ python manage.py runserver
```

---

## 🌐 API Overview

All routes are prefixed with `/api/`

### Book Endpoints

* `POST /books/create/` - Create a book
* `GET /books/` - List all books
* `PATCH /books/update/<id>/` - Update book
* `DELETE /books/delete/<id>/` - Delete book

### Book Issuing

* `POST /books/issue/<book_structure_id>/` - Issue a book
* `POST /books/return/` - Return a book
* `GET /books/user/orders/` - List issued books by user

### User Management

* `GET /user/details/<user_id>/` - View own profile
* `PATCH /user/update/<user_id>/` - Update profile
* `PATCH /user/change-password/<user_id>/` - Change password

### Sub-Admin Management

* `POST /sub-admins/create/` - Create sub-admin
* `PATCH /sub-admins/update/<id>/` - Update sub-admin
* `GET /sub-admins/` - List all sub-admins
* `GET /sub-admins/<id>/` - View sub-admin details
* `DELETE /sub-admins/delete/<id>/` - Delete sub-admin

---

## 🏃 Permissions & Roles

### Super Admin

* Full control: can CRUD everything.

### Sub Admin

* Can be assigned permissions like:

  * `ReadBook`
  * `UpdateBook`
  * `DeleteBook`

Permissions are enforced using custom permission classes.

---

## 🔧 Tech Stack

* Django 5+
* Django REST Framework
* drf-yasg (for Swagger docs)
* SQLite (or PostgreSQL)
* JWT or session authentication

---

## 🔍 Swagger Documentation

Visit:

```
http://localhost:8000/swagger/
```

---

## 🛠️ Development Notes

* Signals (`post_save`) used to create `CustomerCreate` profile automatically.
* Swagger schemas handled with `swagger_auto_schema` decorators.
* File uploads (e.g., profile pictures) supported using `MultiPartParser`.

---

## ✉️ Contact

For queries, open an issue or reach out to `aryan@example.com` (replace with real contact).

---

## 🚀 Future Improvements

* Add search and filtering for books.
* Pagination for list endpoints.
* Late return penalties.
* Role-based dashboard views.

---

## 🏆 License

This project is licensed under the MIT License.
