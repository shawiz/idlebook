from django.core.management.base import BaseCommand, CommandError
from idlebook.book.models import Book
from idlebook.book.amazon import get_by_isbn

from django.db import connection, transaction

class Command(BaseCommand):
    args = '<None>'
    help = 'Update book format'

    def handle(self, *args, **options):        
        books = Book.objects.all()
        counter = 0
        cursor = connection.cursor()
        
        for book in books:
            counter += 1
            # Data retrieval operation - no commit required
            cursor.execute("SELECT image FROM book_book WHERE id = %s", [book.id])
            image = cursor.fetchone()[0]
            
            if image and not image.startswith('books/'):
                new_image = 'books/' + image
                cursor.execute("UPDATE book_book SET image = %s WHERE id = %s", [new_image, book.id])
                transaction.commit_unless_managed()
            #    print new_image
