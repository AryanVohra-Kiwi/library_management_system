from django.dispatch import receiver , Signal
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.contrib import messages
import logging
from .models import BookStructure , BookCopy , IssueBook

logger = logging.getLogger(__name__)

#custom signal
duplicate_book_signal = Signal()
issue_book_signal = Signal()
return_book_signal = Signal()

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
        logger.error("No copy book id given")
        return
    try:
        book_copy = BookCopy.objects.get(id=book_id)
    except BookCopy.DoesNotExist:
        logger.error("no id avaliable")
        return

    if book_copy.copy_number > 0:
        book_copy.status = 'Issued'
    else:
        book_copy.status = 'Unavailable'

    book_copy.save()

@receiver(return_book_signal)
def return_book(sender, *args, **kwargs):
    book_copy_id = kwargs.get("book_copy_id")
    if not book_copy_id:
        logger.error("No copy book id given")
        return
    try:
        book_copy = BookCopy.objects.get(id=book_copy_id)
    except BookCopy.DoesNotExist:
        logger.error("no id avaliable")
        return

    if book_copy.status == 'Issued':
        print('the status also works')
        book_copy.status = 'Available To issue'
        book_copy.save()
        IssueBook.objects.filter(book=book_copy).delete()
        logger.info(f"{book_copy} has been returnrd")
    else:
        print('if this is print you fucked up ')
        logger.error(f"{book_copy} could not be returned")

