from django.dispatch import receiver , Signal
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from .models import BookStructure , BookCopy

#custom signal
duplicate_book = Signal()
delete_dup_book = Signal()


@receiver(duplicate_book)
def duplicate_book_copy(sender , *args , **kwargs):
    book = kwargs.get("book")
    BookCopy.objects.create(
        book_instance=book,
        status = 'Available To issue',
    )

