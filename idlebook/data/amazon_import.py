from amazonproduct import *
import urllib2

from django.core.management import setup_environ
import settings
setup_environ(settings)

from django.db import connection, transaction
from book.models import Book


AWS_KEY = 'AKIAI6M6RNJTOTRN7M4Q'
SECRET_KEY = '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'
api = API(AWS_KEY, SECRET_KEY, 'us')

# paths
SLNBOOK_FILE = './data/spring/slnBook.txt'
BOOKINFO_FILE = './data/amazon_new_autumn.txt'
IMAGE_FOLDER = './data/tmp_images_aut/'


def __get(isbn):
    node = api.item_lookup('9780295952895', IdType='ISBN', SearchIndex='Books', ResponseGroup='ItemAttributes, Images, EditorialReview')
    book = node.Items.Item[0]
    attr = book.ItemAttributes
    return book


def getInfo(isbn, store_title=''):
    '''
    get a map of the infomation of the book isbn
    '''
    info = {}
    notfound = False
    
    try:
    #    node = api.item_lookup(isbn, IdType='ISBN', SearchIndex='Books', ResponseGroup='ItemAttributes, Images, EditorialReview')
        node = api.item_lookup(isbn, IdType='ISBN', SearchIndex='Books', ResponseGroup='ItemAttributes, Images')
        book = node.Items.Item[0]
        attr = book.ItemAttributes
        
        # title, edition, authors, publisher, publication_date, list_price, image, #description
    
        try:
            info['title'] = attr.Title
        except AttributeError, e:
            if store_title:
                info['title'] = store_title
            else:
                info['title'] = 'N/Title'
            
        try:
            info['edition'] = attr.Edition
        except AttributeError, e:
            info['edition'] = 'N/Edition'
        
        try:
            info['author'] = attr.Author
        except AttributeError, e:
            try:
                info['author'] = attr.Creator
            except AttributeError, e:
                info['author'] = 'N/Author'
        
        try:
            info['price'] = attr.ListPrice.Amount
        except AttributeError, e:
            info['price'] = 'N/Price'
    
        try:
            info['publisher']=attr.Publisher
        except AttributeError, e:
            info['publisher']='N/Publisher'
        
        try:
            info['pubdate']=attr.PublicationDate
        except AttributeError, e:
            info['pubdate']='N/Pubdate'
        
        try:
            info['format']=attr.Binding
        except AttributeError, e:
            info['format']='N/Format'
        
        try:
            imgLink=unicode(book.LargeImage.URL)
            img=urllib2.urlopen(imgLink).read()
            open(IMAGE_FOLDER+isbn+'.jpg','wb').write(img)
            info['image']=imgLink
        except AttributeError, e:
            info['image']='N/Image'
        
#        try:
#            info['description']=book.EditorialReviews.EditorialReview.Content
#        except AttributeError, e:
#            info['description']='N/Description'
        
        #utf-8 encoding
        for key, value in info.items():
            info[key] = unicode(value)
    
    except NoExactMatchesFound, e:
        print "not found"
        notfound = True
    except NoSimilarityForASIN, e:
        print "not similar found"
        notfound = True
    except Exception, e:
        print e, "what"
        notfound = True
    
    if notfound:
        info['title'] = store_title
        info['edition'] = 'N/Edition'
        info['author'] = 'N/Author'
        info['publisher'] = 'N/Publisher'
        info['pubdate'] = 'N/Pubdate'
        info['price'] = 'N/Price'
        info['image'] = 'N/Image'
#        info['description']='N/Description'
        
    return info


def isbn2Info_slnBook():
    '''
    get all course book data in batch mode
    '''
    lines = open(SLNBOOK_FILE).read()
    lines = lines.split('\n')
    infoMap = {}
    counter = 1
    
    out = open(BOOKINFO_FILE, 'w')

    for line in lines:
        if line.strip() == '':
            continue
        items = line.split('|')
        isbn = items[4].strip()
        store_title = items[5].strip()
        store_new_price = items[6].strip()
        store_used_price = items[7].strip()
        
        if not isbn in infoMap:
            info = {}
            try:
                info = getInfo(isbn, store_title)
            except InvalidParameterValue, e:
                print 'Book Not Found.'
                
                info['title'] = store_title
                info['edition'] = 'N/Edition'
                info['author'] = 'N/Author'
                info['publisher'] = 'N/Publisher'
                info['pubdate'] = 'N/Pubdate'
                info['price'] = 'N/Price'
                info['image'] = 'N/Image'
#                info['description']='N/Description'
            
            infoLs = [info['title'], info['edition'], info['author'], info['price'], info['publisher'], info['pubdate'], info['image'], store_new_price, store_used_price]
            
            infoMap[isbn] = '|'.join(infoLs)
            
            # write files
            out.write(isbn + '|' + infoMap[isbn] + '\n')
            
            print "#%s %s" % (counter, infoMap[isbn])
            counter += 1


def load_new_books():
    '''
    get book info that are not in database
    '''
    lines = open(SLNBOOK_FILE).read()
    lines = lines.split('\n')
    infoMap = {}
    counter = 1

    out = open(BOOKINFO_FILE, 'w')
    
    for line in lines:
        if line.strip() == '':
            continue
        items = line.split('|')
        isbn = items[4].strip()
        store_title = items[5].strip()
        store_new_price = items[6].strip()
        store_used_price = items[7].strip()

        try:
            book = Book.objects.get(isbn=isbn)
        except Book.DoesNotExist:        
            if not isbn in infoMap:
                info = {}
                try:
                    info = getInfo(isbn, store_title)
                except InvalidParameterValue, e:
                    print 'Book Not Found.'

                    info['title'] = store_title
                    info['edition'] = 'N/Edition'
                    info['author'] = 'N/Author'
                    info['publisher'] = 'N/Publisher'
                    info['pubdate'] = 'N/Pubdate'
                    info['price'] = 'N/Price'
                    info['image'] = 'N/Image'
    #                info['description']='N/Description'

                infoLs = [info['title'], info['edition'], info['author'], info['price'], info['publisher'], info['pubdate'], info['image'], store_new_price, store_used_price]

                infoMap[isbn] = '|'.join(infoLs)

                # write files
                out.write(isbn + '|' + infoMap[isbn] + '\n')

                print "#%s %s" % (counter, infoMap[isbn])
                counter += 1



def update_prices():
    '''
    update prices for books
    
    '''
    lines = open(SLNBOOK_FILE).read()
    lines = lines.split('\n')
    counter = 1
        
    for line in lines:
        if line.strip() == '':
            continue
        items = line.split('|')
        isbn = items[4].strip()
        store_title = items[5].strip()
        store_new_price = items[6].strip()
        store_used_price = items[7].strip()
        
        try:
            book = Book.objects.get(isbn=isbn)
            if store_new_price != 'N/NewPrice':
                new_price = int(float(store_new_price) * 100)
                if not book.prices.ubookstore_new or book.prices.ubookstore_new != new_price:
                    book.prices.ubookstore_new = new_price
                    book.prices.save()
                    print "#%s %s" % (counter, book.prices.ubookstore_new)
                    counter += 1
            if store_used_price != 'N/UsedPrice':
                used_price = int(float(store_used_price) * 100)
                if not book.prices.ubookstore_used or book.prices.ubookstore_used != used_price:
                    book.prices.ubookstore_used = used_price
                    book.prices.save()
                    print "#%s %s" % (counter, book.prices.ubookstore_used)
                    counter += 1
                
        except Book.DoesNotExist:
            pass




if __name__ == "__main__":
#    print getInfo('9781891389221')    
#    isbn2Info_slnBook()
#    load_new_books()
#    update_prices()