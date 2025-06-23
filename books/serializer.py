# Standard Library Importd
import datetime

#Django imports
from django.utils import timezone

#Third-party imports
from rest_framework import serializers, status
from rest_framework.response import Response
from drf_yasg.openapi import Response as SwaggerResponse

#local impoers
from .models import BookStructure, BookCopy, IssueBook
from user_app.models import CustomerCreate

#seralizers defined below
# ══════════════════════════ Book Structure Serializer ══════════════════════════════════════════════════════
class BookStructureSerializer(serializers.ModelSerializer):
    # Dynamically calculate available copies from BookCopy model
    available_copies = serializers.SerializerMethodField()
    class Meta:
        model = BookStructure
        fields = '__all__'
    #get us the available copies for displaying
    def get_available_copies(self , obj):
        return BookCopy.objects.filter(
         book_instance = obj,
    ).count()
# ════════════════════════════════════════════════════════════════════════════════

# ════════════════════════════ Book Copy Serializer ════════════════════════════════════════════════════
class BookCopySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookCopy
        fields = '__all__'
# ════════════════════════════════════════════════════════════════════════════════

# ═════════════════════════════ Issue Book Serializer ═══════════════════════════════════════════════════
class IssueBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueBook
        fields = ['issue_date' , 'return_date']
# ════════════════════════════════════════════════════════════════════════════════

# ══════════════════════════════ Retuen Book Serializer ══════════════════════════════════════════════════
class ReturnBookSerializer(serializers.Serializer):
    book_id = serializers.IntegerField()

    def validate(self, data):
        user = self.context['request'].user
        book_id = data['book_id']

        #user validation
        if not user and not user.is_authenticated:
            raise serializers.ValidationError('Authentication required')

        #get the customer
        try:
            customer = CustomerCreate.objects.get(user=user)
        except CustomerCreate.DoesNotExist:
            raise serializers.ValidationError('Customer does not exist')
        #get the issued book
        try:
            issue_book = IssueBook.objects.select_related('book').get(
                issued_by=customer,
                book__book_instance__id=book_id,
                returned_on__isnull=True
            )
        except IssueBook.DoesNotExist:
            raise serializers.ValidationError('No active issue found for this book')
        if issue_book.returned_on:
            raise serializers.ValidationError('This book has already been returned')

        data['issue_book'] = issue_book
        data['customer'] = customer
        return data

    def save(self, **kwargs):
        issue = self.validated_data['issue_book']
        book = issue.book

        #update return date
        today = timezone.now()
        issue.returned_on = today
        issue.save()

        #update book status
        book.status = 'Available To issue'
        book.save()

        return {
            'message': 'Book returned successfully',
            'returned_on': today,
            'book_id': book.id,
            'book_title': book.book_instance.title if hasattr(book, 'book_instance') else 'Unknown'
        }

    def to_representation(self, instance):
        '''
        function for output formating
        '''
        return {
            'success': True,
            'message': instance['message'],
            'data': {
                'returned_on': instance['returned_on'],
                'book_id': instance['book_id'],
                'book_title': instance['book_title']
            }
        }
# ════════════════════════════════════════════════════════════════════════════════

# ═════════════════════════════════════ View Issued Book Seralizer ═══════════════════════════════════════════
class ViewIssueBookSerializer(serializers.ModelSerializer):
    title = serializers.CharField(
        source='book.book_instance.title', # IssueBook -> BookCopy → BookStructure → title
        read_only=True
    )
    issue_date = serializers.DateField(read_only=True)
    return_date = serializers.DateField(read_only=True)
    issued_by = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = IssueBook
        fields = ['title','issue_date','return_date' , 'issued_by']
# ════════════════════════════════════════════════════════════════════════════════

# ════════════════════════════════ Admin Search Serializer ════════════════════════════════════════════════
class AdminSearchSerializer(serializers.Serializer):
    title = serializers.CharField()
    number_of_days_issued = serializers.IntegerField()
    filter_over_8_days = serializers.BooleanField()

    def validate(self, data):
        if not data.get('title') or not data['title'].strip():
            raise serializers.ValidationError('Title is required')
        elif data.get('number_of_days_issued') is None:
            raise serializers.ValidationError('number_of_days_issued is required')
        return data

    def validate_number_of_days_issued(self, value):
        if value < 0:
            raise serializers.ValidationError('number_of_days_issued cannot be negative')
        return value
# ════════════════════════════════════════════════════════════════════════════════

# ════════════════════════════════ Serializers for tracking  ════════════════════════════════════════════════
class BookHistoryFilterSerializer(serializers.Serializer):
    book_structure_id = serializers.IntegerField(
        required=False,
    )

class HistoryUsingDateInputSerializer(serializers.Serializer):
    date = serializers.DateField(
        required=False,
    )

class BookHistorySerializer(serializers.ModelSerializer):
    title = serializers.CharField(
        source='book.book_instance.title',
        read_only=True
    )
    book_structure_id = serializers.IntegerField(
        source='book.book_instance.id',
        read_only=True
    )
    issued_copy = serializers.IntegerField(
        source='book.copy_number',
        read_only=True
    )
    class Meta:
        model = IssueBook
        fields = ['title', 'issue_date','return_date' , 'returned_on', 'issued_by' , 'issued_copy' , 'book_structure_id']
# ════════════════════════════════════════════════════════════════════════════════

