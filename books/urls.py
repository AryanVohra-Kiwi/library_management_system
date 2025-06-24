from django.urls import path
from .views import (
    create_books,
    display_all_books,
    get_book_details,
    update_book,
    delete_book,
    issue_book,
    return_book,
    show_admin_issued_books,
    admin_issue_book_search,
    track_book_history,
    track_using_date,
)

app_name = 'books'

urlpatterns = [

    # 📚 Book Management
    path('api/create/', create_books, name='create_books'),
    path('api/display/', display_all_books, name='display_all_books'),
    path('api/details/<int:book_structure_id>/', get_book_details, name='book_details'),
    path('api/update/<int:book_structure_id>/', update_book, name='update_book'),
    path('api/delete/<int:book_structure_id>/', delete_book, name='delete_book'),

    # 📦 Issue & Return Operations
    path('api/issue/<int:book_structure_id>/', issue_book, name='issue_book'),
    path('api/return/', return_book, name='return_book'),

    # 👤 User Operations
    path('api/admin_issued_books/', show_admin_issued_books, name='user_issued_books'),

    # 🛠️ Admin Tools
    path('api/admin_search/', admin_issue_book_search, name='admin_search'),

    # 📈 Tracking & History
    path('api/book_history/', track_book_history, name='book_history'),
    path('api/track_date/', track_using_date, name='track_date'),
]
