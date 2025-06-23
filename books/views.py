# 🧩 Django imports
import datetime
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.contrib.auth.decorators import login_required
from pyexpat.errors import messages

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
from sub_admins.permissions import *

#global imports
import logging


#-------------Logger---------------------------------
logger = logging.getLogger(__name__)
#------------------------------------------------


#-------------Create Book---------------------------------
@swagger_auto_schema(
    method='post',
    request_body=BookStructureSerializer,
    responses={
        201: openapi.Response('Book or duplicate book created successfully'),
        400: openapi.Response('Error while Creating Book'),
        500 : openapi.Response('Internal Server Error')
    },
    operation_description="Book Creation API"
)
@api_view(['POST'])
@permission_classes([IsAdminOrSubAdminUpdateBook])
def create_books(request , *args , **kwargs):
    """
    Handles the creation of a new book entry in the library system.

    This endpoint accepts a POST request with book details in the request body.
    If a book with the same title, author, and edition already exists, a duplicate book signal is triggered instead of creating a new entry.

    No query parameters are required. Input is expected as JSON in the request body.
    Returns a success message if the book is created or a duplicate is detected.
    """
    try:
        serializer = BookStructureSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        existing_book = BookStructure.objects.filter(
            title=serializer.validated_data['title'],
            author=serializer.validated_data['author'],
            edition=serializer.validated_data['edition'],
        ).first()
        if existing_book:
            duplicate_book_signal.send(sender=existing_book.__class__, book=existing_book)
            return Response({'message' : 'duplicate book detected and added'} , status=201)
        serializer.save()
        return Response({'message' : 'book created successfully'} , status=201)
    except Exception as e:
        logger.exception('unhandled exception in create_book_view')
        return Response(
            {
                'message' : 'Error while creating book',
            },
            status=500
        )
#----------------------------------------------

#-----------Display books----------------------
@swagger_auto_schema(
    method='get',
    responses={
        200:openapi.Response('All books Displayed'),
        404: openapi.Response('No Book Found'),
        500: openapi.Response('Internal Server Error')
    },
    operation_description="API to display all available books in the library"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def display_all_books(request , *args , **kwargs):
    '''
    Retrieves and returns a list of all books stored in the library system.

    This endpoint requires no parameters and is accessible to authenticated users.
    Returns a 200 response with serialized book data or 404 if no books are found.
    '''
    try:
        books = BookStructure.objects.all()
        if not books.exists():
            return Response({'message' : 'No books found'}, status=404)
        serializer = BookStructureSerializer(books , many=True)
        return Response(
            {
                'all_books' : serializer.data
            },
            status=200
        )
    except Exception as e:
        logger.exception('unhandled exception in display_all_books view')
        return Response(
            {
                'message' : 'Error while retrieving all books',
            },
            status=500
        )
#----------------------------------------------

#--------------------Get Book Details--------------------------
@swagger_auto_schema(
    method='get',
    responses={
        200:openapi.Response('Book details'),
        404: openapi.Response('No Book Found'),
        500: openapi.Response('Internal Server Error')
    },
    operation_description="API to get single book details"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_book_details(request , book_structure_id , *args , **kwargs ):
    """
    Retrieves detailed information about a specific book, including its metadata and all physical copies.

    This endpoint accepts a `book_structure_id` (corresponding to a BookStructure entry) and returns:
    - General metadata of the book (title, author, genre, etc.).
    - The number of available copies (with status = 'Available To issue').
    - A list of all physical copies with their copy number, status, and ID.

    Authentication is required. Access may be limited based on user roles (e.g., editing/updating rights for admins/sub-admins).

    Returns:
    - 200 OK with serialized book details if the book exists.
    - 404 Not Found if the book ID is invalid or not found.
    """
    #get book
    try:
        book = get_object_or_404(BookStructure , id=book_structure_id)

        #count copies
        book_copy_count = BookCopy.objects.filter(
            book_instance=book,
            status='Available To issue'
        ).count()

        #get all books
        all_copies = BookCopy.objects.filter(book_instance=book)
        book_copy_data = [
            {
                'copy_number' : single_copy.copy_number ,
                'status' : single_copy.status,
                'id' : single_copy.id
            } for single_copy in all_copies
        ]

        serializer_data = BookStructureSerializer(book).data
        serializer_data['available_copies'] = book_copy_count
        serializer_data['all_copies'] = book_copy_data
        return Response(serializer_data , status=200)
    except Http404:
        return Response({'message': 'No book found'}, status=404)
    except Exception as e:
        logger.exception('unhandled exception in get_book_details view')
        return Response(
            {
                'message' : 'Error while retrieving book details',
            },
            status=500
        )
#----------------------------------------------


#---------------Delete Book----------------
@swagger_auto_schema(
    method = 'delete',
    request_body=None,
    responses={
        200 : openapi.Response('Book deleted successfully'),
        404 : openapi.Response('Book Not Found'),
        500: openapi.Response('Internal Server Error')
    },
    operation_description="API to delete a single book or a book copy"
)
@api_view(['DELETE'])
@permission_classes([IsAdminOrSubAdminDeleteBook])
def delete_book(request , book_structure_id , *args , **kwargs):
    """
    Deletes a book copy or the main book from the library.

    Logic:
    - If any BookCopy exists for the given BookStructure:
        - Deletes the most recent BookCopy (highest copy_number).
    - If no copies are left:
        - Deletes the BookStructure itself.

    Parameters:
    - `book_structure_id`: ID of the BookStructure model (not BookCopy or IssueBook).

    Returns:
    - 200 OK: If deletion is successful.
    - 404 Not Found: If the book doesn't exist.
    - 500 Internal Server Error: For unexpected issues.
    """
    try:
        book = get_object_or_404(BookStructure , id=book_structure_id)
        book_copy_querry_set = BookCopy.objects.filter(book_instance=book)

        if book_copy_querry_set.exists():
            latest_copy = book_copy_querry_set.order_by('-copy_number').first()
            latest_copy.delete()
            return Response({'message' : 'Book copy deleted successfully'}, status=200)
        else:
            book.delete()
            return Response({'message' : 'Main Book deleted successfully'}, status=200)
    except Http404:
        return Response({'message': 'No book found'}, status=404)
    except Exception as e:
        logger.exception('unhandled exception in delete_book view')
        return Response(
            {
                'message' : 'Error while deleting book and book copies',
            },
            status=500
        )
#---------------------------------------------------

#------------Update Book--------------
@swagger_auto_schema(
    method='patch',
    request_body=BookStructureSerializer,
    responses={
        200 : openapi.Response('Book updated successfully'),
        404 : openapi.Response('Bad Request'),
        500: openapi.Response('Internal Server Error')
    },
    operation_description='API to update book details'

)
@api_view(['PATCH'])
@permission_classes([IsAdminOrSubAdminUpdateBook])
def update_book(request , book_structure_id , *args , **kwargs ):
    """
    Updates metadata for a specific book (BookStructure entry).

    Parameters:
    - `book_structure_id`: ID of the book (BookStructure).

    Accepts:
    - Partial fields of the BookStructure model.

    Returns:
    - 200 OK: If the book was successfully updated.
    - 400 Bad Request: If the submitted data is invalid.
    - 404 Not Found: If the book does not exist.
    - 500 Internal Server Error: On unexpected failure.
    """
    try:
        book = get_object_or_404(BookStructure , id=book_structure_id)
        serializer = BookStructureSerializer(book , data=request.data , partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        serializer.save()
        return Response({'message' : 'Book updated successfully' , 'data' : serializer.data}, status=200)
    except Http404:
        return Response({'message': 'No book found'}, status=404)
    except Exception as e:
        logger.exception('unhandled exception in update_book view')
        return Response(
            {
                'message' : 'Error while updating book details',
            },
            status=500
        )

#---------------------------------------------------

#------------------Isuue Book------------------------
@swagger_auto_schema(
    method='post',
    request_body=IssueBookSerializer,
    responses={
        200: openapi.Response('Book issued successfully'),
        400: openapi.Response('Book not issued'),
        404:openapi.Response('Book not found'),
        500: openapi.Response('Internal Server Error'),
    },
    operation_description='API to issue book'
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def issue_book(request , book_structure_id , *args , **kwargs):
    """
    Issues a book to the currently authenticated user.

    Logic:
    - Retrieves the authenticated user's customer profile.
    - Validates the request data using `IssueBookSerializer`.
    - Ensures the user hasn't already issued the same book.
    - Fetches the first available book copy (based on `copy_number`).
    - If found, creates an `IssueBook` entry and marks the copy as issued.

    Parameters:
    - `book_structure_id`: ID of the BookStructure (not BookCopy or IssueBook).

    Returns:
    - 200 OK: Book issued successfully.
    - 400 Bad Request: Validation error, book already issued, or no available copies.
    - 500 Internal Server Error: Unexpected errors.
    """
    try:
        customer = CustomerCreate.objects.get(user=request.user)
        book = get_object_or_404(BookStructure , id=book_structure_id)

        issued_book_serializer = IssueBookSerializer(data=request.data)
        if not issued_book_serializer.is_valid():
            return Response(issued_book_serializer.errors, status=400)

        already_issued = IssueBook.objects.filter(
            issued_by=customer,
            book__book_instance=book,
            # Go from IssueBook to its book field (which is a BookCopy), Then go from that BookCopy to its book_instance (which is a BookStructure)
         ).exists()
        if already_issued:
            return Response({'message' : 'This book is already issued'},status=400 )

        copy_book = BookCopy.objects.filter(
            book_instance=book,
            status='Available To issue'
        ).order_by('copy_number').first()
        if not copy_book:
            return Response({'message' : 'No book availiable to issue'},status=400 )

        book_issued = issued_book_serializer.save(
            issued_by=customer,
            book=copy_book,
        )
        issue_book_signal.send(sender=issued_book_serializer.__class__, book_copy_id=copy_book.id)
        return Response({'message' : 'Book issued successfully'},status=200 )

    except CustomerCreate.DoesNotExist:
        return Response({'message' : 'Customer does not exist'},status=400)

    except Http404:
        return Response({'message' : 'No book found'},status=404)

    except Exception as e:
        logger.exception('unhandled exception in issue_book view')
        return Response(
            {
                'message' : 'Error while issuing book ',
            },
            status=500
        )

#-----------------------------------------------------------------

#--------------------Return Book ----------------------
#run tests before updating
@swagger_auto_schema(
    method='post',
    request_body=ReturnBookSerializer,
    responses={
        200 : openapi.Response('Book returned successfully'),
        400 : openapi.Response('Book not issued'),
        500 : openapi.Response('Internal Server Error'),
    },
    operation_description='API to return book'
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def return_book(request, book_structure_id , *args , **kwargs):
    '''
    Handles the return of a previously issued book by an authenticated user.

    This endpoint:
    - Accepts a `book_structure_id` representing the BookStructure (not BookCopy or IssueBook).
    - Verifies that the authenticated user has an active issue record for this book.
    - Updates the `IssueBook` record with a return timestamp.
    - Updates the `BookCopy` status to 'Available To issue'.

    Requirements:
    - The user must be authenticated.
    - The book must be currently issued and not already returned.

    Returns:
    - 200 OK: If the book is successfully returned.
    - 400 Bad Request: If validation fails (e.g., book not issued or already returned).
    - 500 Internal Server Error: For unexpected failures.

    Note:
    This endpoint uses the `ReturnBookSerializer` to validate input and perform the return logic.
    '''
    try:
        serializer = ReturnBookSerializer(data={'book_id': book_structure_id} , context={'request': request} )
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        data = serializer.save()
        return Response({
            "message": data['message'],
            "book": data['book_title'],
            "returned_on": data['returned_on'],
        }, status=200)
    except Exception as e:
        logger.exception('unhandled exception in return book view')
        return Response(
            {
                'message' : 'Error while returning book ',
            },
            status=500
        )

#----------------------------------------------------------------------

#------------------------Show user issued books------------------------
@swagger_auto_schema(
    method='get',
    responses={
        200 : openapi.Response('Show all Books Iussed By user'),
        400 : openapi.Response('Error while showing books issued by user'),
        404: openapi.Response('Book not found'),
        500: openapi.Response('Internal Server Error'),
    },
    operation_description='API to show all books issued by user'
)
@api_view(['GET'])
@permission_classes([IsAdminOrSubAdminDeleteBook])
def show_user_issued_books(request, *args , **kwargs):
    """
    Retrieves all books currently issued by the authenticated user.

    Logic:
    - Identifies the currently authenticated user.
    - Fetches the corresponding Customer instance.
    - Queries the IssueBook model for all books issued by that customer.
    - Serializes and returns the issued book data.

    Returns:
    - 200 OK: A list of books issued by the user.
    - 404 Not Found: If the user does not have a corresponding customer profile.
    - 500 Internal Server Error: If any unexpected error occurs during processing.

    Permissions:
    - Only users with `IsAdminOrSubAdminDeleteBook` permission are allowed to access this endpoint.
    """
    try:
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
    except CustomerCreate.DoesNotExist:
        return Response({'message' : 'Customer does not exist'},status=404)
    except Exception as e:
        logger.exception('unhandled exception in show_user_issued_books view')
        return Response(
            {
                'message' : 'Error while showing books issued by user ',
            },
            status=500
        )
#--------------------------------------------------------------------


#-------------------Admin Only Search-------------------
@swagger_auto_schema(
    method='post',
    request_body=AdminSearchSerializer,
    responses={
        200 : openapi.Response('Show all Books Iussed By user'),
        400 : openapi.Response('Error while showing books'),
        500: openapi.Response('Internal Server Error'),
    },
    operation_description='API to show all books based on target days and filter'
)
@api_view(['POST'])
@permission_classes([IsAdminOrSubAdminReadBook])
def admin_issue_book_search(request , *args , **kwargs):
    """
    Admin API to search for issued books based on title and issuance duration.

    This endpoint allows admin or sub-admin users to filter issued books using the following criteria:

    - `Title` (optional): Partial or full book title match (case-insensitive).
    - `number_of_days_issued` (optional): Filters books issued exactly `N` days ago.
    - `filter_over_8_days` (optional): Filters books issued more than 8 days ago.

    Logic:
    - Performs case-insensitive search by book title using `icontains`.
    - If both title and days are given, applies both filters.
    - If no filters match, returns all issued books.
    - Uses `select_related` to optimize database queries by prefetching `book` and `book_instance`.

    Permissions:
    - Only accessible by users with `IsAdminOrSubAdminReadBook` permission.

    Returns:
    - `200 OK`: List of issued books matching the filter.
    - `400 Bad Request`: If validation fails on input.
    - `500 Internal Server Error`: If an unexpected error occurs during execution.
    """
    try:
        search_serializer  = AdminSearchSerializer(data=request.data)
        if not search_serializer.is_valid():
            return Response(search_serializer.errors, status=400)

        title = search_serializer.validated_data.get('Title')
        target_days = search_serializer.validated_data.get('number_of_days_issued')
        filter_over_8_days = search_serializer.validated_data.get('filter_over_8_days')
        today = datetime.date.today()
        issued_books = IssueBook.objects.select_related('book__book_instance').all()

        if title:
            issued_books = issued_books.filter(
                book__book_instance__title__icontains = title,
            )
        if target_days is not None:
            date_n_days_ago = today - datetime.timedelta(days=target_days)
            issued_books = issued_books.filter(Issue_date__date=date_n_days_ago)

        elif filter_over_8_days:
            date_8_days_ago = today - datetime.timedelta(days=8)
            issued_books = issued_books.filter(Issue_date__lt=date_8_days_ago)

        serializer = ViewIssueBookSerializer(issued_books, many=True)
        return Response(
            {
            'matched_books' : serializer.data,
            },
            status=200
        )
    except Exception as e:
        logger.exception('unhandled exception in admin_issue_book_search view')
        return Response(
            {
                'message' : 'Error while searching ',
            },
            status=500
        )
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
        500: openapi.Response('Internal Server Error'),
    },
    operation_id='API to track book history with filter',
)
@api_view(['GET'])
@permission_classes([IsAdminOrSubAdminReadBook])
def track_book_history(request, *args, **kwargs):
    """
    track_book_history(request)

    API endpoint to retrieve the issue/return history of books.

    This view supports optional filtering based on a specific `book_structure_id`. If provided, it returns the history of all copies (BookCopy) associated with that particular BookStructure. If no filter is applied, it returns the complete issue history across all books.

    The results are paginated (10 records per page) and serialized using `BookHistorySerializer`.

    Query Parameters:
    - book_structure_id (optional): Integer — ID of the BookStructure to filter history by.

    Returns:
    - 200 OK: Paginated list of issue/return records.
    - 400 Bad Request: If query parameter validation fails.
    - 500 Internal Server Error: For unexpected server-side exceptions.
    """

    try:
        book_id_serialized = BookHistoryFilterSerializer(data=request.query_params)
        if not book_id_serialized.is_valid():
            return Response(book_id_serialized.errors, status=400)

        book_structure_id = book_id_serialized.validated_data.get('book_structure_id')
        paginator = PageNumberPagination()
        paginator.page_size = 10

        if book_structure_id:
            querry_set = IssueBook.objects.filter(book__book_instance__id=book_structure_id)
        else:
            querry_set = IssueBook.objects.all()

        paginator_querry_set=paginator.paginate_queryset(querry_set, request)
        serializer = BookHistorySerializer(paginator_querry_set, many=True)
        return paginator.get_paginated_response(serializer.data)
    except Exception as e:
        logger.exception('unhandled exception in track_book_history view')
        return Response(
            {
                'message': 'Error while searching ',
            },
            status=500
        )
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
        500: openapi.Response('Internal Server Error'),
    },
    operation_description='API to get all the books on a particuar date or filter it'
)
@api_view(['GET'])
@permission_classes([IsAdminOrSubAdminReadBook])
def track_using_date(request , *args , **kwargs):
    """
    Tracks issued books based on a specific date or books issued more than 8 days ago.

    Functionality:
    - Accepts an optional `date` as a query parameter in `YYYY-MM-DD` format.
    - If a date is provided, it fetches all books issued on that specific date.
    - If no date is provided, it fetches all books that were issued more than 8 days ago from today.
    - Results are paginated with 10 records per page.

    Query Parameters:
    - `date` (optional): A date string (e.g., "2025-06-01") to filter issued books.

    Returns:
    - 200 OK: Paginated list of issued books with a message.
    - 400 Bad Request: If the date input is invalid.
    - 500 Internal Server Error: For unexpected exceptions.

    Permissions:
    - Requires admin or sub-admin role with ReadBook permission.
    """
    try:
        date_seralizer = HistoryUsingDateInputSerializer(data=request.query_params)
        if not date_seralizer.is_valid():
            return Response(date_seralizer.errors, status=400)
        date = date_seralizer.validated_data.get('date')
        paginator = PageNumberPagination()
        paginator.page_size = 10
        if date:
            querry_set = IssueBook.objects.filter(
                Issue_date=date,
            )
            message = "Issued Book for specific date"
        else:
            today = datetime.date.today()
            eight_days_ago = today - datetime.timedelta(days=8)
            querry_set = IssueBook.objects.filter(Issue_date__lte=eight_days_ago)
            message = "Issued Book after filter (greater than 8 days ago)"

        paginated = paginator.paginate_queryset(querry_set, request)
        serializer = BookHistorySerializer(paginated, many=True)
        return paginator.get_paginated_response({
            'message': message,
            'data': serializer.data
        })

    except Exception as e:
        logger.exception('unhandled exception in track_using_date view')
        return Response(
            {
                'message': 'Error while searching ',
            },
            status=500
        )
#---------------------------------------------------------------------------------