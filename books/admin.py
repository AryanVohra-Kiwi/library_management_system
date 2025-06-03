from django.contrib import admin
from .models import BookStructure , BookCopy , IssueBook
# Register your models here.
admin.site.register(BookStructure)
admin.site.register(BookCopy)
admin.site.register(IssueBook)