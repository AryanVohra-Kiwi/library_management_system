from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view , permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
#Local imports
from user_app.models import CustomerCreate
from .DisplayForm import UpdateBookModelForm , IssueBookModelForm
from .serializer import *
from .models import BookStructure , BookCopy , IssueBook
from django.http import Http404
from .signals import duplicate_book_signal , issue_book_signal , return_book_signal
from user_auth.decorator import *
import datetime
# Create your views here.

#-------------Create Book---------------------------------
@swagger_auto_schema(
    method='post',
    request_body=BookStructureSerializer,
    responses={
        201: openapi.Response('Book created or duplicate detected'),
        400: 'Invalid input',
    },
    operation_description="Create a new book if it doesn't already exist. Duplicate books trigger a signal. signal is responsible for creating a duplicate copy instance of the book"
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_books(request , *args , **kwargs):
    '''
    This function will take the input made using our Model Form and will enter the value into the database.
    No parameters required
    '''
    serializer = BookStructureSerializer(data=request.data)
    if serializer.is_valid():
        existing_book = BookStructure.objects.filter(
            Title=serializer.validated_data['Title'],
            Author=serializer.validated_data['Author'],
            Price=serializer.validated_data['Price'],
            Publication_date=serializer.validated_data['Publication_date'],
            Subject=serializer.validated_data['Subject'],
            keyword=serializer.validated_data['keyword'],
            Edition=serializer.validated_data['Edition'],
            Publisher=serializer.validated_data['Publisher'],
        ).first()

        if existing_book:
            duplicate_book_signal.send(sender=existing_book.__class__, book=existing_book)
            return Response({'message' : 'duplicate book detected and added'} , status=201)
        new_book = serializer.save()
        return Response({'message' : 'book created successfully'} , status=201)
    return Response(serializer.errors, status=400)
#----------------------------------------------

#-----------Display books----------------------
@swagger_auto_schema(
    method='get',
    responses={
        200:openapi.Response('All books Displayed'),
        404: openapi.Response('No Book Found'),
    },
    operation_description="Get all books displayed"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def display_all_books(request , *args , **kwargs):
    '''
    This function will display all the books in the database.
    No parameters required
    '''
    books = BookStructure.objects.all()
    if not books.exists():
        return Response({'message' : 'No books found'}, status=404)
    serializer = BookStructureSerializer(books , many=True)
    return Response(serializer.data)
#----------------------------------------------

#--------------------Get Book Details--------------------------
@swagger_auto_schema(
    method='get',
    responses={
        200:openapi.Response('Book details'),
        404: openapi.Response('No Book Found'),
    },
    operation_description="Get one single book detail , and based on your role , you will have the option to change / edit the book"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_book_details(request , book_id , *args , **kwargs ):
    book = get_object_or_404(BookStructure , id=book_id)
    #count copies
    book_copy_count = BookCopy.objects.filter(
        book_instance=book,
        status='Available To issue'
    ).count()
    all_books = BookCopy.objects.filter(book_instance=book)
    book_copy_data = [
        {
            'copy_number' : single_copy.copy_number ,
            'status' : single_copy.status,
            'id' : single_copy.id
        } for single_copy in all_books
    ]

    serializer_data = BookStructureSerializer(book).data
    serializer_data['available_copies'] = book_copy_count
    serializer_data['all_copies'] = book_copy_data
    return Response(serializer_data , status=200)
#----------------------------------------------


#---------------Delete Book----------------
@swagger_auto_schema(
    method = 'post',
    request_body=None,
    responses={
        200 : openapi.Response('Book deleted successfully'),
        404 : openapi.Response('Error Deleting Book'),
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_book(request , book_id , *args , **kwargs):
    '''
    This function will delete the book.
    parameters : book_id -> id in the database
    '''
    book = get_object_or_404(BookStructure , id=book_id)
    book_copy_count = BookCopy.objects.filter(book_instance=book).count()

    if book_copy_count > 0:
        book_to_delete = BookCopy.objects.filter(book_instance=book).order_by('-copy_number').first()
        book_to_delete.delete()
        return Response({'message' : 'Book copy deleted successfully'}, status=200)
    else:
        book.delete()
        return Response({'message' : 'Main Book deleted successfully'}, status=200)
#---------------------------------------------------

#------------Update Book--------------
@swagger_auto_schema(
    method='patch',
    request_body=BookStructureSerializer,
    responses={
        200 : openapi.Response('Book updated successfully'),
        404 : openapi.Response('Error updating Book'),
    },
    operation_description='This api is responsible for updating a book'

)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_book(request , book_id , *args , **kwargs ):
    '''
    This function will update the book.
    parameters : book_id -> id in the database
    '''
    book = get_object_or_404(BookStructure , id=book_id)
    serializer = BookStructureSerializer(book , data=request.data , partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'message' : 'Book updated successfully' , 'data' : serializer.data}, status=200)
    return Response(serializer.errors, status=400)
#-----------------------------------


#REST TO BE DONE AFTER UPDATING USER LOGIN
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

