from django.contrib import admin
from django.urls import path
from .views import create_books , display_all_books , delete_book , get_book_details , update_book , issue_book , return_book , show_all_user_books , admin_search
#app urls
user_app = 'books'
urlpatterns = [
    path('api/create/' , create_books , name='create_books'),
    path('api/display/' , display_all_books , name='display_all_books'),
    path('api/details/<int:book_id>' , get_book_details , name='book-details'),
    path('api/update/<int:book_id>/' , update_book , name='update-book'),
    path('api/delete/<int:book_id>/' , delete_book , name='delete-book'),
    path('api/issue/<int:book_id>/' , issue_book , name='issue-book'),
    path('api/return/<int:book_id>/' , return_book , name='return-book'),
    path('user_books/<int:book_id>/' , show_all_user_books , name='user-books'),
    path('admin_search/' , admin_search , name='admin_search'),
]