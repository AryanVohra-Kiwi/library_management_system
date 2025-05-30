from django.db import models
from django.urls import reverse
# Create your models here.
class BookStructure(models.Model):
    Title = models.CharField(max_length=120)
    Author = models.CharField(max_length=50)
    Price = models.FloatField()
    Publication_date = models.DateField(auto_now=False, auto_now_add=False)
    Subject = models.TextField() #summery of the book
    keyword = models.CharField() #gerne for the book
    Edition = models.DecimalField(decimal_places=5, max_digits=15)
    Publisher = models.CharField()

    def get_absolute_url(self):
        return reverse('books:book-details' , kwargs={id:self.id})