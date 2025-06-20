from django.db import models
from django.db.models import Model
from django.urls import reverse
from user_app.models import CustomerCreate
from django.db.models import Max

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

    def get_absolute_url(self):
        return reverse('books:book-details' , kwargs={'id':self.id})

    def __str__(self):
        return self.Title

class BookCopy(models.Model):
    book_instance = models.ForeignKey(BookStructure, on_delete=models.CASCADE)
    copy_number = models.PositiveIntegerField(default=0)
    status_choices = (
        ('Issued' , 'Issued'), #one value of database , and one for user readiability
        ('Returned' , 'Returned'),
        ('Available To issue' , 'Available To Issue'),
        ('Unavailable', 'Unavailable'),
        ('Lost' , 'Lost'),
        ('Damaged' , 'Damaged'),
    )
    status = models.CharField(max_length=100 ,choices=status_choices)

    def save(self, *args, **kwargs):
        if not self.copy_number:
            max_copies = BookCopy.objects.filter(book_instance=self.book_instance).aggregate(Max('copy_number'))['copy_number__max']
            self.copy_number = (max_copies or 0) + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{str(self.book_instance)} - copy {self.copy_number}'


class IssueBook(models.Model):
    book = models.ForeignKey(BookCopy, on_delete=models.CASCADE)
    Issue_date = models.DateField(auto_now=False, auto_now_add=False)
    Return_date = models.DateField(auto_now=False, auto_now_add=False)
    returned_on = models.DateField(blank=True, null=True)
    issued_by = models.ForeignKey(CustomerCreate, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.book} issued by {self.issued_by}'

