#Model imports
from django.db import models
from user_app.models import CustomerCreate
from django.db.models import Max

from django.utils.timezone import now

# Create your models here.
#◥ ▬▬▬▬▬▬▬▬▬▬▬▬ ◆ ▬▬▬▬▬▬▬▬▬▬▬▬ ◤
class BookStructure(models.Model):
    '''
    Represents the core metadata for a unique book title in the library.

    Each time a new book (not a physical copy) is created by a user, it is stored in this model.
    This includes general information such as the title, author, publication details, and genre.
    Multiple physical copies of the same book reference this structure via the BookCopy model.

    '''
    title = models.CharField(max_length=120) #store the title of the book
    author = models.CharField(max_length=50) # store the author of the book
    price = models.FloatField() #store the price of the book
    publication_date = models.DateField(auto_now=False, auto_now_add=False)#store the publication date of the book
    subject = models.TextField(help_text='summary of the book')#store the subject of the book
    genre = models.CharField(max_length=120 , help_text='genre of the book')#store the genre of the book
    edition = models.DecimalField(decimal_places=5, max_digits=15)#store the edition of the book
    publisher = models.CharField(max_length=120)#store the punlisher of the book
    created_at = models.DateTimeField(auto_now_add=True) #store the date this book was created at
    updated_at = models.DateTimeField(auto_now=True)#store date this book was update at

    def __str__(self):
        '''
        Returns the string representation of the book, used in django admin and debugging.

        '''
        return self.title
#◥ ▬▬▬▬▬▬▬▬▬▬▬▬ ◆ ▬▬▬▬▬▬▬▬▬▬▬▬ ◤


#◥ ▬▬▬▬▬▬▬▬▬▬▬▬ ◆ ▬▬▬▬▬▬▬▬▬▬▬▬ ◤
class BookCopy(models.Model):
    '''
    Represents a physical copy of a book in the library.

    Each copy is linked to a BookStructure entry and has its own unique copy number and availability status.
    Useful for tracking individual inventory items, lending history, and condition.
    '''
    book_instance = models.ForeignKey(BookStructure, on_delete=models.CASCADE) #refers to the book from BookStructure as FK
    copy_number = models.PositiveIntegerField(default=0) #the number of copy a specific book has
    status_choices = (
        ('Issued' , 'Issued'), #one value of database , and one for user readiability
        ('Returned' , 'Returned'),
        ('Available To issue' , 'Available To Issue'),
        ('Unavailable', 'Unavailable'),
        ('Lost' , 'Lost'),
        ('Damaged' , 'Damaged'),
    )
    status = models.CharField(max_length=100 ,choices=status_choices) #we assign the choices
    created_at = models.DateTimeField(auto_now_add=True) #store the date this book was created at

    def save(self, *args, **kwargs):
        '''
        automatically assigns a new unique copy_number when the instance is saved
        '''
        if not self.copy_number:
            max_copies = BookCopy.objects.filter(book_instance=self.book_instance).aggregate(Max('copy_number'))['copy_number__max']
            self.copy_number = (max_copies or 0) + 1
        super().save(*args, **kwargs)

    def __str__(self):
        """
         Returns a readable string format for admin display and debugging.
         Example: 'Harry Potter - copy 2'
         """
        return f'{str(self.book_instance)} - copy {self.copy_number}'
#◥ ▬▬▬▬▬▬▬▬▬▬▬▬ ◆ ▬▬▬▬▬▬▬▬▬▬▬▬ ◤

#◥ ▬▬▬▬▬▬▬▬▬▬▬▬ ◆ ▬▬▬▬▬▬▬▬▬▬▬▬ ◤
class IssueBook(models.Model):
    '''
    This model keeps track of when a book was issued, its expected return date,
    when (or if) it was actually returned, and the user who borrowed it.
    '''
    book = models.ForeignKey(BookCopy, on_delete=models.CASCADE) #referes to the BookCopy because user can only issue if a copy of the book exists
    issue_date = models.DateField(auto_now=False, auto_now_add=False) #the date the book has been issued
    return_date = models.DateField(auto_now=False, auto_now_add=False) #the date the book is to be returned (can not be more than 7 days)
    returned_on = models.DateField(blank=True, null=True) #the date the book was returned
    issued_by = models.ForeignKey(CustomerCreate, on_delete=models.CASCADE) #which user issued the book

    def __str__(self):
        '''
            Returns a readable string for admin/debug views.
        Example: Harry Potter - copy 2 issued by Aryan
        '''
        return f'{self.book} issued by {self.issued_by}'
#◥ ▬▬▬▬▬▬▬▬▬▬▬▬ ◆ ▬▬▬▬▬▬▬▬▬▬▬▬ ◤