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
    book_copy_id = serializers.IntegerField()

    def validate(self, data):
        user = self.context['request'].user
        book_copy_id = data.get('book_copy_id')

        if not user or not user.is_authenticated:
            raise serializers.ValidationError('Authentication required.')

        # Get the customer
        try:
            customer = CustomerCreate.objects.get(user=user)
        except CustomerCreate.DoesNotExist:
            raise serializers.ValidationError('Customer does not exist.')

        # Get the BookCopy
        try:
            book_copy = BookCopy.objects.get(id=book_copy_id)
        except BookCopy.DoesNotExist:
            raise serializers.ValidationError('Book copy not found.')

        # Get the active IssueBook entry
        try:
            issue_book = IssueBook.objects.select_related('book__book_instance').get(
                issued_by=customer,
                book=book_copy,
                returned_on__isnull=True
            )
        except IssueBook.DoesNotExist:
            raise serializers.ValidationError('No active issue found for this book copy.')

        # Save references in validated_data
        data['issue_book'] = issue_book
        data['book_copy'] = book_copy
        data['customer'] = customer
        return data

    def save(self, **kwargs):
        """
        Marks the book as returned and updates the status.
        """
        issue = self.validated_data['issue_book']
        book_copy = self.validated_data['book_copy']
        today = timezone.now()

        # Update issue record
        issue.returned_on = today
        issue.save()

        # Update book copy status
        book_copy.status = 'Available To issue'
        book_copy.save()

        return {
            'message': 'Book returned successfully',
            'returned_on': today,
            'book_id': book_copy.id,
            'book_title': getattr(book_copy.book_instance, 'title', 'Unknown')
        }

    def to_representation(self, instance):
        """
        Format output for the API response.
        """
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

