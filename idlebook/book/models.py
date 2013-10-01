from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class BookManager(models.Manager):
    
    def most_wanted(self):
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("""
            SELECT book_book.id, book_book.title, book_book.edition, count(book_wishlist.user_id) AS wish_count
            FROM book_wishlist, book_book
            WHERE book_wishlist.book_id = book_book.id
            GROUP BY book_wishlist.book_id
            ORDER BY wish_count DESC
            LIMIT 5""")
        result_list = []
        for row in cursor.fetchall():
            p = self.model(id=row[0], title=row[1], edition=row[2])
            p.wish_count = row[3]
            result_list.append(p)
        return result_list


class Book(models.Model):
    # fields
    title               = models.CharField(max_length=200)
    isbn                = models.CharField(max_length=20, unique=True)
    edition             = models.CharField(max_length=60, null=True, blank=True)
    authors             = models.CharField(max_length=200, null=True, blank=True)
    publisher           = models.CharField(max_length=100, null=True, blank=True)
    publication_date    = models.CharField(max_length=40, null=True, blank=True)
    list_price          = models.IntegerField(null=True, blank=True)
    format              = models.CharField(max_length=100, null=True, blank=True)
    description         = models.TextField(blank=True, null=True)
    is_textbook         = models.BooleanField(default=True)
    image               = models.ImageField(upload_to='books/', null=True)
    
    # many to many
    wish_users          = models.ManyToManyField(User, null=True, related_name='wish_books', through='Wishlist')
    other_editions      = models.ManyToManyField('self', blank=True)

    objects             = BookManager()

    def __unicode__(self):
        return self.title
    
    def has_owner(self, owner):
        users = Book.objects.raw('SELECT * FROM book_bookcopy WHERE book_bookcopy.book_id = %s AND book_bookcopy.owner_id = %s', [self.id, owner.id])
        
        for user in users:
            if user:
                return True
        return False

    def has_wisher(self, wisher):
        users = Book.objects.raw('SELECT * FROM book_wishlist WHERE book_wishlist.book_id = %s AND book_wishlist.user_id = %s', [self.id, wisher.id])
        
        for user in users:
            if user:
                return True
        return False
    
    def get_related_books(self, num=5):
        """ Possible use of SQL
        'SELECT p.* FROM posts_tags pt, posts p, tags t WHERE pt.tag_id = t.id AND (t.name IN ('tag1', 'tag2', 'tag3')) AND p.id=pt.post_id GROUP BY p.id HAVING COUNT(p.id) = 3;'
        """
        books = Book.objects.filter(courses__books__id=self.id).exclude(id=self.id).distinct()[0:5]
    #    if len(books) < 5:
    #        pass
        return books
        
    
    class Admin:
        list_display    = ('title', 'author', 'publisher')
        ordering        = ('author', 'title')
        search_fields   = ('title', 'author', 'publisher')


class BookPrices(models.Model):
    
    book            = models.OneToOneField(Book, related_name='prices')
    ubookstore_new  = models.IntegerField(null=True, blank=True)
    ubookstore_used = models.IntegerField(null=True, blank=True)
    amazon_new      = models.IntegerField(null=True, blank=True)
    amazon_used     = models.IntegerField(null=True, blank=True)


class BookCopy(models.Model):
        
    CONDITION_CHOICES = (
        (0, ''),
        (1, 'New'),
        (2, 'Used - Like New'),
        (3, 'Used - Very Good'),
        (4, 'Used - Good'),
        (5, 'Used - Acceptable'),
    )
    
    # many to one
    book            = models.ForeignKey(Book, related_name='copies')
    owner           = models.ForeignKey(User, related_name='own_books')
    
    # fields
    add_time        = models.DateTimeField(auto_now_add=True)
    condition       = models.SmallIntegerField(null=True, choices=CONDITION_CHOICES)
    notes           = models.TextField(blank=True)
    # books's status. not available 0, renting 1, available 2
    status          = models.SmallIntegerField(default=0)
    lease_price     = models.IntegerField(default=None, null=True)
    sale_price      = models.IntegerField(default=None, null=True)
    # penalty per day for people didn't return the book at due date
    penalty         = models.IntegerField(default=0)
    # deposit amount
    reserved_amount = models.IntegerField(default=None, null=True)
    
    def __unicode__(self):
        return self.book.title + ' ' + self.owner.last_name
    
    class Admin:
        pass
    
    
    def get_deposit(self):
        book = self.book
        list_price = book.list_price
        lease_price = self.lease_price
        sale_price = self.sale_price
        
        if not lease_price: # sales don't need deposit
            return 0
            
        if not list_price:
            list_price = book.prices.ubookstore_new
            if not list_price:
                list_price = book.prices.amazon_new
                
        if list_price:
            if list_price < settings.DEPOSIT_LIST_PRICE_MIN_LIMIT:
                return 0
            else:
                depo_return = int(round(list_price * settings.DEPOSIT_LIST_PRICE_PERCENT))
                if sale_price:
                    return max(min(depo_return, sale_price - lease_price), 0)
                else:
                    return max(min(depo_return, list_price - lease_price), 0)
        else:
            if lease_price < settings.DEPOSIT_MIN_LIMIT:
                return 0
            else:
                depo_return = int(round(lease_price * settings.DEPOSIT_MIN_LIMIT_PERCENT))
                if sale_price:
                    return max(min(depo_return, sale_price - lease_price), 0)
                else:
                    return depo_return

class Wishlist(models.Model):
    # many to one
    book        = models.ForeignKey(Book)
    user        = models.ForeignKey(User)

    # fields
    add_time    = models.DateTimeField(auto_now_add=True)
    max_price   = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return '%s %s' % (self.book.title, self.user.first_name)

    @staticmethod
    def most_wanted():
        books = Wishlist.objects.raw('''SELECT book_book.id, book_book.title, book_book.edition, count(book_wishlist.user_id) AS wish_count
                                        FROM book_wishlist, book_book
                                        WHERE book_wishlist.book_id = book_book.id
                                        GROUP BY book_wishlist.book_id
                                        ORDER BY wish_count DESC
                                        LIMIT 5''')
        return books
    
    class Meta:
        unique_together = [('book', 'user')]

    class Admin:
        pass

