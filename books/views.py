from urllib import request

from django.shortcuts import render, redirect , get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
#Local imports
from .DisplayForm import CreateBookModelForm, UpdateBookModelForm
from .models import BookStructure
from django.http import Http404
from user_auth.decorator import allowed_users
# Create your views here.
@login_required(login_url='login_user')
@allowed_users(allowed_users=['admin' , 'sub-admin'] , allowed_permissions=['books.add_bookstructure'])
def create_books(request , *args , **kwargs):
    '''
    This function will take the input made using our Model Form and will enter the value into the database.
    No parameters required
    '''
    user = request.user
    if request.method == 'POST':
        new_book = CreateBookModelForm(request.POST)
        if new_book.is_valid():
            existing_book = BookStructure.objects.filter(
                Title = new_book.cleaned_data['Title'],
                Author = new_book.cleaned_data['Author'],
            ).first() #get existing book from the database
            if existing_book:
                existing_book.count += new_book.cleaned_data['count']
                existing_book.save() #save the book in the database
                messages.success(request, 'duplicate book added successfully')
                return redirect('display_all_books')
            else:
                new_book.save() #save the book in the database
                messages.success(request, 'Book created successfully')
                return redirect('create_books') #returns to the same homepage after creating , if the user wants to create another book
        else:
            messages.error(request , 'Failed to add a new book')
    else:
        new_book = CreateBookModelForm()

    context = {'new_book' : new_book} #new book as object
    return render(request , 'book_pages/book_create.html' , context)

@login_required(login_url='login_user')
@allowed_users(allowed_users=['admin' , 'sub-admin' , 'Customer'])
def display_all_books(request , *args , **kwargs):
    '''
    This function will display all the books in the database.
    No parameters required
    '''
    querry_set = BookStructure.objects.all() #queryset to print all books
    context = {'List_all_books' : querry_set}
    return render(request , 'book_pages/all_books.html' , context)

@login_required(login_url='login_user')
@allowed_users(allowed_users=['admin' , 'sub-admin' , 'Customer'])
def get_book_details(request , book_id , *args , **kwargs ):
    '''
    This function will display the details of the book.
    we require a book id to display the details of a specific book.
    parameters : book_id -> id in the database
    '''
    user = request.user
    user_group = list(user.groups.values_list('name', flat=True))
    can_update = bool(
        'admin' in user_group or
        ('sub-admin' in user_group and user.has_perm('books.change_bookstructure'))
    )
    can_add = bool(
        'admin' in user_group or
        ('sub-admin' in user_group and user.has_perm('books.add_bookstructure'))
    )
    can_delete = bool(
        'admin' in user_group or
        ('sub-admin' in user_group and user.has_perm('books.delete_bookstructure'))
    )


    try:
        book = get_object_or_404(BookStructure , id=book_id)
    except Http404 as http404_error:
        raise Http404
    except Exception as exception:
        raise exception
    context = {
        'book_details' : book,
        'user_group' : user_group,
        'can_update' : can_update,
        'can_add' : can_add,
        'can_delete' : can_delete,

    }
    return render(request , 'book_pages/book_details.html' ,context)

@login_required(login_url='login_user')
@allowed_users(allowed_users=['admin' , 'sub-admin'] , allowed_permissions=['books.delete_bookstructure'])
def delete_book(request , book_id , *args , **kwargs):
    '''
    This function will delete the book.
    parameters : book_id -> id in the database
    '''
    try:
        del_book = get_object_or_404(BookStructure , id=book_id) #get objects or gives 404
        book = get_object_or_404(BookStructure , id=book_id)
    except Http404 as http404_error:
        return redirect('display_all_books')
    except Exception as exception:
        messages.error(request, 'Failed to delete book')
    if request.method == 'POST':
        del_book.delete()
        messages.success(request, 'Book deleted successfully')
    context = {
        'delete_book' : del_book,
        'book' : book,
    }
    return render (request, 'book_pages/book_delete.html' , context)

@login_required(login_url='login_user')
@allowed_users(allowed_users=['admin' , 'sub-admin'] , allowed_permissions=['books.change_bookstructure'])
def update_book(request , book_id , *args , **kwargs ):
    '''
    This function will update the book.
    parameters : book_id -> id in the database
    '''
    try:
        book = get_object_or_404(BookStructure , id=book_id)
    except HTTP404 as http404_error:
        raise Http404
    except Exception as exception:
        raise exception
    if request.method == 'POST':
        updated_book = UpdateBookModelForm(request.POST , instance=book)
        if updated_book.is_valid():
            updated_book.save()
            messages.success(request, 'Book updated successfully')
            return redirect('book-details' , book_id=book_id)
        else:
            messages.error(request , 'Failed to update book')
    else:
        updated_book = UpdateBookModelForm(instance=book)

    context = {
        'updated_book' : updated_book,
        'current_book' : book,
    }
    return render(request , 'book_pages/book_update.html' , context)