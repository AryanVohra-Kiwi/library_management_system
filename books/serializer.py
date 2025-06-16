from rest_framework import serializers
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
        fields = '__all__'

