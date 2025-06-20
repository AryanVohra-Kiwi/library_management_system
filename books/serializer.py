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
            'book_title': book.title if hasattr(book, 'title') else 'Unknown'
        }

    def to_representation(self, instance):
        return {
            'success': True,
            'message': 'Book returned successfully',
            'data': instance
        }
