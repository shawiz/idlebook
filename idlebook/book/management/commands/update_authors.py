from django.core.management.base import BaseCommand, CommandError
from book.models import Book
from book.amazon import get_by_isbn
from book.utils import smart_truncate_lists


class Command(BaseCommand):
    args = '<None>'
    help = 'Update book format'

    def handle(self, *args, **options):
        books = Book.objects.all()
        counter = 0
        for book in books:
            counter += 1
            book_info = get_by_isbn(book.isbn, ['title', 'edition', 'authors', 'publisher', 'format'])
            if book_info:
                book.title = book_info['title']
                book.edition = book_info['edition']
                book.authors = smart_truncate_lists(book_info['authors'])
                book.publisher = book_info['publisher']
                book.format = book_info['format']
                book.save()
                print "#%s %s %s" % (counter, book.isbn, book.authors)
            else:
                print "#%s %s" % (counter, book.isbn)
