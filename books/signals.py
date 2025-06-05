from django.dispatch import receiver , Signal
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.contrib import messages

from .models import BookStructure , BookCopy , IssueBook

#custom signal
duplicate_book_signal = Signal()
issue_book_signal = Signal()


@receiver(duplicate_book_signal)
def duplicate_book_copy(sender , *args , **kwargs):
    book = kwargs.get("book")
    BookCopy.objects.create(
        book_instance=book,
        status = 'Available To issue',
    )


@receiver(issue_book_signal)
def issue_book(sender, *args, **kwargs):
    book_id = kwargs.get("book_copy_id")
    if not book_id:
        return messages.error('no book id')
    try:
        book_copy = BookCopy.objects.get(id=book_id)
    except BookCopy.DoesNotExist:
        return messages.error('id doesnt exist')

    if book_copy.copy_number > 0:
        book_copy.status = 'Issued'
    else:
        book_copy.status = 'Unavailable'

    book_copy.save()



