from django.contrib import admin
from django.urls import path
from .views import create_books , display_all_books , delete_book , get_book_details , update_book , issue_book , return_book , show_user_issued_books , admin_issue_book_search , track_book_history, track_using_date
#app urls
user_app = 'books'
urlpatterns = [
    path('api/create/' , create_books , name='create_books'),
    path('api/display/' , display_all_books , name='display_all_books'),
    path('api/details/<int:book_structure_id>' , get_book_details , name='book-details'),
    path('api/update/<int:book_structure_id>/' , update_book , name='update-book'),
    path('api/delete/<int:book_structure_id>/' , delete_book , name='delete-book'),
    path('api/issue/<int:book_structure_id>/' , issue_book , name='issue-book'),
    path('api/return/<int:book_structure_id>/' , return_book , name='return-book'),
    path('api/user_issued_books/' , show_user_issued_books , name='user-books'),
    path('api/admin_search/' , admin_issue_book_search , name='admin_search'),
    path('api/book_history' , track_book_history , name='book-history'),
    path('api/track_date' , track_using_date , name='track-date'),
]