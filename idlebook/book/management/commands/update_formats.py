from django.core.management.base import BaseCommand, CommandError
from idlebook.book.models import Book
from idlebook.book.amazon import get_by_isbn


class Command(BaseCommand):
    args = '<None>'
    help = 'Update book format'

    def handle(self, *args, **options):        
        books = Book.objects.filter(format=None)
        counter = 0
        for book in books:
            counter += 1
            book_info = get_by_isbn(book.isbn, ['format'])
            if book_info:
                book.format = book_info['format']
                book.save()
                print "#%s %s %s" % (counter, book.isbn, book.format)
            else:
                print "#%s %s" % (counter, book.isbn)