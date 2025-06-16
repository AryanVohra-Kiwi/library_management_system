from urllib import request

from django.dispatch import Signal
from django.shortcuts import render, redirect , get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
#Local imports
from user_app.models import CustomerCreate
from .DisplayForm import CreateBookModelForm, UpdateBookModelForm , IssueBookModelForm
from .models import BookStructure , BookCopy , IssueBook
from django.http import Http404
from .signals import duplicate_book_signal , issue_book_signal , return_book_signal
from user_auth.decorator import *
import datetime
from django.db.models import Max
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
                Title=new_book.cleaned_data['Title'],
                Author=new_book.cleaned_data['Author'],
                Price=new_book.cleaned_data['Price'],
                Publication_date=new_book.cleaned_data['Publication_date'],
                Subject=new_book.cleaned_data['Subject'],
                keyword=new_book.cleaned_data['keyword'],
                Edition=new_book.cleaned_data['Edition'],
                Publisher=new_book.cleaned_data['Publisher'],
            ).first()

            if existing_book:
                duplicate_book_signal.send(sender=existing_book.__class__, book=existing_book)
            else:
                new_book = new_book.save() #save the book in the database
                book_copy = BookCopy()
                book_copy.book_instance = new_book
                book_copy.save()
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
    for books in querry_set:
        avail_copies = BookCopy.objects.filter(
            book_instance = books,
            status='Available To issue'

        ).count()
        books.available_copies = avail_copies
    context = {
        'List_all_books' : querry_set,
    }
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
    max_copies = BookCopy.objects.filter(
        book_instance=book,
        status='Available To issue'
    ).count()
    copies = BookCopy.objects.filter(book_instance_id=book_id)
    print(copies)
    for details in copies:
        print(details)
        print(details.copy_number)
    context = {
        'book_details' : book,
        'user_group' : user_group,
        'can_update' : can_update,
        'can_add' : can_add,
        'can_delete' : can_delete,
        'max_copies': max_copies,
        'dup_books' : copies,

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
        book_copy_count = BookCopy.objects.filter(book_instance=book).count()
    except Http404 as http404_error:
        return redirect('display_all_books')
    except Exception as exception:
        messages.error(request, 'Failed to delete book')
    if request.method == 'POST':
        if book_copy_count > 0:
            book_to_delete = BookCopy.objects.filter(book_instance=book).order_by('-copy_number').first()
            book_to_delete.delete()
            messages.success(request, 'Book copy deleted successfully')
            return redirect('display_all_books')
        else:
            del_book.delete()
            messages.success(request, 'Book deleted successfully')
            return redirect('display_all_books')
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

def issue_book(request , book_id , *args , **kwargs):
    customer = CustomerCreate.objects.get(user=request.user)
    book = get_object_or_404(BookStructure , id=book_id)


    if request.method == 'POST':
        issued_book  = IssueBookModelForm(request.POST)
        if issued_book.is_valid():
            already_issued = IssueBook.objects.filter(
                issued_by=customer,
                book__book_instance=book,
                # Go from IssueBook to its book field (which is a BookCopy), Then go from that BookCopy to its book_instance (which is a BookStructure)
            ).exists()
            if already_issued:
                messages.error(request, 'Book already issued')
                return redirect('book-details', book_id=book_id)


            copy_book = BookCopy.objects.filter(
                book_instance=book,
                status='Available To issue'
            ).order_by('copy_number').first()
            if not copy_book:
                messages.error(request, 'No available copy of this book to issue.')
                return redirect('book-details', book_id=book_id)
            else:
                book_issued = issued_book.save(commit=False)
                book_issued.issued_by = customer
                book_issued.book = copy_book
                book_issued.save()
                issue_book_signal.send(sender=issued_book.__class__, book_copy_id=copy_book.id)
                messages.success(request, 'Book issued successfully')
                return redirect('book-details' , book_id=book_id)
    else:
        issued_book = IssueBookModelForm()
    context = {
        'book' : book,
        'issued_book' : issued_book,
    }
    return render(request , 'book_pages/issue_book.html' , context)

def return_book(request , book_id , *args , **kwargs):
    book = get_object_or_404(BookStructure , id=book_id)
    customer = CustomerCreate.objects.get(user=request.user)
    book_copy = BookCopy.objects.filter(book_instance=book)
    issued_book = IssueBook.objects.filter(
        issued_by=customer,
    )
    return_date = issued_book.values_list('Return_date' , flat=True)
    today = datetime.date.today()

    for issue in issued_book:
        days_left = (issue.Return_date - today).days
        issue.days_left = days_left
    if request.method == 'POST':
        issued_book_instance = issued_book.first()
        book_copy = issued_book_instance.book
        return_book_signal.send(sender=return_book, book_copy_id=book_copy.id)
        return redirect('user_orders' , id=book_id)
    context = {
        'issued_book' : issued_book,
    }
    return render(request , 'book_pages/return_book.html' , context)

@login_required(login_url='login_user')
@admin_only(allowed_users=['admin' , 'sub-admin'])
def show_all_user_books(request , book_id , *args , **kwargs):
    customer = CustomerCreate.objects.get(user=request.user)
    issued_book = IssueBook.objects.all()
    if request.method == 'POST':
        user_book_title = request.POST.get('Book Title')
        try:
            book_title = issued_book.first().book.book_instance.Title
        except AttributeError:
            book_title = None
        print(user_book_title)
        print(book_title)
        print(issued_book)

    return render(request , 'book_pages/all_user_books.html' , {})

def admin_search(request , *args , **kwargs):
    matched_books = []
    show =  False
    if request.method == 'POST':
        show = True
        user_book = request.POST.get('book_title')
        user_days = int(request.POST.get('number_of_days'))
        today = datetime.date.today()
        requested_book = IssueBook.objects.filter(book__book_instance__Title=user_book)  #return a query set
        for book in requested_book:
            days = (today - book.Issue_date).days
            if days == user_days:
                matched_books.append(book)
                print(matched_books)
    context = {
        'matched_issues' : matched_books,
        'show' : show,
    }
    return render(request , 'book_pages/admin_book_search.html' , context)

