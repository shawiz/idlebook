from django.core.management import setup_environ
import settings
import re
setup_environ(settings)

from idlebook.book.models import Book

def remove_useless_books():    
    logfile = open("./data/remove_junk.txt", "r").read().split("\n")
    counter = 1
    for line in logfile:
        line = line.strip()
        if line == '':
            continue
        words = line.split('|')
        isbn = words[0].strip()
        
        try:
            book = Book.objects.get(isbn=isbn)
        #    print book.isbn, book.title
            book.delete()
            print "#%s %s deleted" % (counter, isbn)
            counter += 1
            
        except Book.DoesNotExist:
            pass
        
        

def cleanup_book_names():
    unknown_books = Book.objects.filter(author='')
    counter = 1
    for book in unknown_books:
        title = book.title
        m = re.search(r'[a-z0-9,][A-Z(][a-z,]', title)
        
        if m:
            print "#" + str(counter) + " " + book.title
            new_title = title[:m.start()+1] + ' ' + title[m.end()-2:]
            print '\t' + new_title
            book.title = new_title
            book.save()
            counter += 1

if __name__ == "__main__":
#    remove_useless_books()
#    cleanup_book_names()