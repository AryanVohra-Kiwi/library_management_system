from drf_yasg.openapi import Response
from rest_framework import serializers, status
import datetime
from user_app.models import CustomerCreate
from .models import BookStructure , BookCopy , IssueBook

class BookStructureSerializer(serializers.ModelSerializer):
    available_copies = serializers.SerializerMethodField() # is used when you want to include custom, calculated, or dynamic data in your API response — data that isn't directly stored as a field in your model.
    #SerializerMethodField will help me get the number of copies a book has , since it is not stored in BookStructure model but my BookCopy Model

    class Meta:
        model = BookStructure
        fields = '__all__'
    #get us the available copies for displaying
    def get_available_copies(self , obj):
        return BookCopy.objects.filter(
         book_instance = obj,
    ).count()

class BookCopySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookCopy
        fields = '__all__'

class IssueBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueBook
        fields = ['Issue_date' , 'Return_date']


from rest_framework import serializers, status
from rest_framework.response import Response
from django.utils import timezone
from .models import CustomerCreate, IssueBook


class ReturnBookSerializer(serializers.Serializer):
    book_id = serializers.IntegerField()
    def validate(self, data):
        user = self.context['request'].user
        book_id = data['book_id']
        try:
            customer = CustomerCreate.objects.get(user=user)
        except CustomerCreate.DoesNotExist:
            raise serializers.ValidationError('Customer does not exist')
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
        today = timezone.now()
        issue.returned_on = today
        issue.save()

        book = issue.book
        book.status = 'Available To issue'
        book.save()

        return {
            'message': 'Book returned successfully',
            'returned_on': today,
            'book_id': book.id,
            'book_title': book.book_instance.title if hasattr(book, 'book_instance') else 'Unknown'
        }

    def to_representation(self, instance):
        return {
            'success': True,
            'message': instance['message'],
            'data': {
                'returned_on': instance['returned_on'],
                'book_id': instance['book_id'],
                'book_title': instance['book_title']
            }
        }


class ViewIssueBookSerializer(serializers.ModelSerializer):
    Title = serializers.CharField(
        source='book.book_instance.Title',
        read_only=True
    )
    Issue_date = serializers.DateField(read_only=True)
    Return_date = serializers.DateField(read_only=True)
    issued_by = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = IssueBook
        fields = ['Title','Issue_date','Return_date' , 'issued_by']


class AminSearchSearlizer(serializers.Serializer):
    title = serializers.CharField()
    number_of_days_isssued = serializers.IntegerField()
    filter_over_8_days = serializers.BooleanField()

    def validate(self, data):
        if data['title'] == None:
            raise serializers.ValidationError('Title is required')
        elif data['number_of_days_issued'] == None:
            raise serializers.ValidationError('number_of_days_issued is required')
        return data

    def validate_number_of_days_issued(self, value):
        if value < 0:
            raise serializers.ValidationError('number_of_days_issued can not be negative')
        return value

class BookHistoryFilterSeralizer(serializers.Serializer):
    book_id = serializers.IntegerField(
        required=False,
    )

class HistoryUsingDateInputSeralizer(serializers.Serializer):
    date = serializers.DateField(
        required=False,
    )

class BookHistorySerializer(serializers.ModelSerializer):
    Title = serializers.CharField(
        source='book.book_instance.Title',
        read_only=True
    )
    book_id = serializers.IntegerField(
        source='book.book_instance.book_instance_id',
        read_only=True
    )
    issued_copy = serializers.IntegerField(
        source='book.copy_number',
        read_only=True
    )
    class Meta:
        model = IssueBook
        fields = ['Title', 'Issue_date','Return_date' , 'returned_on', 'issued_by' , 'issued_copy' , 'book_id']



