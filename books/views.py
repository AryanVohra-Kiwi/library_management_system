# 🧩 Django imports
import datetime
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.contrib.auth.decorators import login_required

# 🌐 DRF imports
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

# 📘 Swagger / OpenAPI (drf-yasg)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# 🗂️ Local imports
from .models import BookStructure, BookCopy, IssueBook
from .serializer import *
from .signals import duplicate_book_signal, issue_book_signal, return_book_signal


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
    method = 'delete',
    request_body=None,
    responses={
        200 : openapi.Response('Book deleted successfully'),
        404 : openapi.Response('Error Deleting Book'),
    }
)
@api_view(['DELETE'])
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
#---------------------------------------------------

#------------------Isuue Book------------------------
@swagger_auto_schema(
    method='post',
    request_body=IssueBookSerializer,
    responses={
        200 : openapi.Response('Book created successfully'),
        400 : openapi.Response('Book not issued'),
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def issue_book(request , book_id , *args , **kwargs):
    customer = CustomerCreate.objects.get(user=request.user)
    book = get_object_or_404(BookStructure , id=book_id)
    issued_book_serializer = IssueBookSerializer(data=request.data)
    if issued_book_serializer.is_valid():
        already_issued = IssueBook.objects.filter(
            issued_by=customer,
            book__book_instance=book,
            # Go from IssueBook to its book field (which is a BookCopy), Then go from that BookCopy to its book_instance (which is a BookStructure)
        ).exists()
        if already_issued:
            return Response({'messages' : 'This book is already issued'},400 )
        copy_book = BookCopy.objects.filter(
            book_instance=book,
            status='Available To issue'
        ).order_by('copy_number').first()
        if not copy_book:
            return Response({'messages' : 'No book avaliable to issue'},400 )
        else:
            book_issued = issued_book_serializer.save(
                issued_by=customer,
                book=copy_book,
            )
            issue_book_signal.send(sender=issued_book_serializer.__class__, book_copy_id=copy_book.id)
            return Response({'messages' : 'Book issued successfully'},200 )
    return Response(issued_book_serializer.errors, status=400)
#-----------------------------------------------------------------

#--------------------Return Book ----------------------
@swagger_auto_schema(
    method='post',
    request_body=ReturnBookSerializer,
    responses={
        200 : openapi.Response('Book created successfully'),
        400 : openapi.Response('Book not issued'),
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def return_book(request, book_id):
    serializer = ReturnBookSerializer(data={'book_id': book_id}, context={'request': request})
    if serializer.is_valid():
        issue = serializer.save()
        return Response({
            "message": "Book returned successfully",
            "book": issue.book.book_instance.title,
            "returned_on": issue.returned_on
        }, status=200)
    return Response(serializer.errors, status=400)

#----------------------------------------------------------------------

#------------------------Show user issued books------------------------
@swagger_auto_schema(
    method='get',
    responses={
        200 : openapi.Response('Show all Books Iussed By user'),
        400 : openapi.Response('Error while showing books'),
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def show_user_issued_books(request, *args , **kwargs):
    customer = CustomerCreate.objects.get(user=request.user)
    book_issued_by_user = IssueBook.objects.filter(
        issued_by=customer,
    )
    serializer = ViewIssueBookSerializer(book_issued_by_user, many=True)
    return Response(
        {
            'Issued_Book' : serializer.data,
        }
    )
#--------------------------------------------------------------------


#-------------------Admin Only Search-------------------
@swagger_auto_schema(
    method='post',
    request_body=AminSearchSearlizer,
    responses={
        200 : openapi.Response('Show all Books Iussed By user'),
        400 : openapi.Response('Error while showing books'),
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_issue_book_search(request , *args , **kwargs):
    search_seralizer = AminSearchSearlizer(data=request.data)
    if not search_seralizer.is_valid():
        return Response(search_seralizer.errors, status=400)

    title = search_seralizer.validated_data.get('Title')
    target_days = search_seralizer.validated_data.get('number_of_days_issued')
    filter = search_seralizer.validated_data.get('filter_over_8_days')
    today = datetime.date.today()

    issued_books = IssueBook.objects.all()

    if title:
        issued_books = issued_books.filter(
            book__book_instance__Title = title,
        )
    if target_days is not None:
        filtered_books = list(filter(
            lambda book : (today - book.Issue_date).days == target_days,
            issued_books
        ))
    elif filter:
        filtered_books = list(filter(
            lambda book : (today - book.Issue_date).days > 8,
            issued_books
        ))
    else:
        filtered_books = list(issued_books)
    #remove later
    seralizer = ViewIssueBookSerializer(filtered_books, many=True)
    return Response({
        'matched books' : seralizer.data,
    })
#-----------------------------------------------------------------------

#----------------------------------Track Book History----------------------
@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
        'book_id',
        openapi.IN_QUERY,
        description='Book ID',
        type=openapi.TYPE_INTEGER,
        required=False,
        ),
    ],
    responses={
        200 : openapi.Response('Show Book Hisotry (filtered and non filtered)'),
        400 : openapi.Response('Error while showing book history'),
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def track_book_history(request, *args, **kwargs):
    book_id_serialized = BookHistoryFilterSeralizer(data=request.query_params)
    if not book_id_serialized.is_valid():
        return Response(book_id_serialized.errors, status=400)

    book_id = book_id_serialized.validated_data.get('book_id')
    paginator = PageNumberPagination()
    paginator.page_size = 10

    if book_id:
        filtered_history = IssueBook.objects.filter(book__book_instance__id=book_id)
        results = paginator.paginate_queryset(filtered_history, request)
        serializer = BookHistorySerializer(results, many=True)
        return paginator.get_paginated_response(serializer.data)
    else:
        all_books = IssueBook.objects.all()
        results = paginator.paginate_queryset(all_books, request)
        serializer = BookHistorySerializer(results, many=True)
        return paginator.get_paginated_response(serializer.data)
#---------------------------------------------------------------------


#-------------------------------------Get user issued Books using a specific date ------------------
@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'date',
            openapi.IN_QUERY,
            description='Date',
            type=openapi.TYPE_STRING,
            required=False,
        ),
    ],
    responses={
        200 : openapi.Response('Show all Books Issued on a particuar date'),
        400 : openapi.Response('Error while showing books'),
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
#NOTE ADD PAGINATION
def track_using_date(request , *args , **kwargs):
    date_seralizer = HistoryUsingDateInputSeralizer(data=request.query_params)
    if not date_seralizer.is_valid():
        return Response(date_seralizer.errors, status=400)
    date = date_seralizer.validated_data.get('date')
    if date:
        issued_book = IssueBook.objects.filter(
            Issue_date=date,
        )
        result_seralizer = BookHistorySerializer(issued_book , many=True)
        return Response(
            {
                'Issued book for specific date' : result_seralizer.data,
            }
        )
    else:
        today = datetime.date.today()
        eight_days_ago = today - datetime.timedelta(days=8)
        filtered_issue = IssueBook.objects.filter(Issue_date__lte=eight_days_ago)
        result_seralizer = BookHistorySerializer(filtered_issue, many=True)
        return Response(
            {
                'Issued book after filter (greater than 8 days)' : result_seralizer.data,
            }
        )
#---------------------------------------------------------------------------------