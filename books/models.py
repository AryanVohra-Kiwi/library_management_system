from django.db import models
from django.db.models import Model
from django.urls import reverse
from user_app.models import CustomerCreate

# Create your models here.
class BookStructure(models.Model):
    Title = models.CharField(max_length=120)
    Author = models.CharField(max_length=50)
    Price = models.FloatField()
    Publication_date = models.DateField(auto_now=False, auto_now_add=False)
    Subject = models.TextField() #summery of the book
    keyword = models.CharField(max_length=120) #gerne for the book
    Edition = models.DecimalField(decimal_places=5, max_digits=15)
    Publisher = models.CharField(max_length=120)
    count = models.IntegerField(default = 1)

    def get_absolute_url(self):
        return reverse('books:book-details' , kwargs={'id':self.id})

class IssueBook(models.Model):
    Title = models.CharField(max_length=120)
    Price = models.FloatField()
    Issue_date = models.DateField(auto_now=False, auto_now_add=False)
    Return_date = models.DateField(auto_now=False, auto_now_add=False)
    issued_by = models.ForeignKey(CustomerCreate, on_delete=models.CASCADE)


