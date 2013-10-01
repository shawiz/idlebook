from django.core.management import setup_environ
import settings
setup_environ(settings)

from django.db import connection, transaction

def load_departments():
    cursor = connection.cursor()
    logfile = open("./data/name2dep_normalized.txt", "r").readlines()
    counter = 1
    
    for line in logfile:
        words = line.split(';')
        name = words[0].strip()
        code = words[1].strip()
        
        cursor.execute("INSERT INTO network_department (network_id, name, code) VALUES (1, %s, %s)", [name, code])
        transaction.commit_unless_managed()
        counter += 1
        
        print "%d department: %s %s" % (counter, name, code)
        
    print "done"


def load_courses():
    cursor = connection.cursor()
    
    logfile = open("./data/autumn/bookData.txt", "r").read().split("\n")    

    counter = 1
    
    for line in logfile:
        if line == "":
            continue
        
        words = line.split('|')
        code = words[0].replace(' ', '')
        number = words[1]        
        name = "%s%s" % (code, number)
        
        cursor.execute("SELECT id FROM network_department WHERE code = %s", [code])
        dept_id = int(cursor.fetchone()[0])
        print "%s %s" % (dept_id, code)
        
        cursor.execute("INSERT IGNORE INTO network_course (name, number, department_id) VALUES (%s, %s, %s)", [name, number, dept_id])
        transaction.commit_unless_managed()
        
        counter += 1
        
        print "#%d course: %s %s" % (counter, name, dept_id)
    
    print "done"
    

# load for exist data
def load_books():
    cursor = connection.cursor()
        
    logfile = open("./data/amazon_new_autumn.txt", "r").read().split("\n")    

    counter = 1
    
    for line in logfile:
        if line == [] or line == "":
            continue
        
        words = line.split('|')
        
        isbn = words[0]
    
        title = words[1]
    
        edition = words[2]
        if edition == "N/Edition":
            edition = ""
    
        author = words[3]
        if author == "N/Author":
            author = ""
    
        list_price = words[4]
        if list_price == "N/Price":
            list_price = None

        publisher = words[5]
        if publisher == "N/Publisher":
            publisher = ""
    
        publication_date = words[6]
        if publication_date == "N/Pubdate":
            publication_date = ""
    
        image = words[7]
        if image == "N/Image":
            image = ""
        else:
            image = "books/%s.jpg" % isbn
    
        store_new_price = words[8]
        if store_new_price == "N/NewPrice":
            store_new_price = None
        else:
            store_new_price = int(float(store_new_price) * 100)
        
        store_used_price = words[9]
        if store_used_price == "N/UsedPrice":
            store_used_price = None
        else:
            store_used_price = int(float(store_used_price) * 100)
        
        cursor.execute("REPLACE INTO book_book (isbn, title, edition, author, list_price, publisher, publication_date, image) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", [isbn, title, edition, author, list_price, publisher, publication_date, image])
        transaction.commit_unless_managed()
        
        cursor.execute("SELECT id FROM book_book WHERE isbn = %s", [isbn])
        book_id = int(cursor.fetchone()[0])
        
        cursor.execute("REPLACE INTO book_bookprices (book_id, ubookstore_new, ubookstore_used) VALUES (%s, %s, %s)", [book_id, store_new_price, store_used_price])
        transaction.commit_unless_managed()
        
        counter += 1

        print "#%d book: %s %s" % (counter, isbn, title)

    print "done"
    


def load_books2courses():
    cursor = connection.cursor()

    logfile = open("./data/autumn/bookData.txt", "r").read().split("\n")

    counter = 1

    for line in logfile:
        if line == "":
            continue

        words = line.split('|')

        code = words[0].replace(' ', '')
        number = words[1]
        name = "%s%s" % (code, number)

        cursor.execute("SELECT id FROM network_course WHERE name = %s", [name])
        course_id = int(cursor.fetchone()[0])

        print "%s %s" % (name, course_id)

        books = words[3]
        isbns = books.split(';')
        
        for isbn in isbns:
            isbn = isbn.strip()
            
            cursor.execute("SELECT id FROM book_book WHERE isbn = %s", [isbn])
            book = cursor.fetchone()
            
            if book != None:
                book_id = int(book[0])

                cursor.execute("INSERT IGNORE INTO network_course_books (course_id, book_id) VALUES (%s, %s)", [course_id, book_id])
                transaction.commit_unless_managed()

                print "#%s %s %s" % (counter, course_id, book_id)

                counter += 1

    print "done"




if __name__ == "__main__":
#    load_departments()
#    load_courses()
#    load_books()
    load_books2courses()