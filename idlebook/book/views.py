import urllib2
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

from django.utils import simplejson
from django.shortcuts import render_to_response, get_object_or_404
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from models import *
from utils import _to_int, _is_isbn, _is_course_name, get_buyer_price, get_price_range
from lookup import BookLookup, DepartmentLookup
#from ubookstore.search import fetchBooks, removeBookDuplicates
from account.cache import reset_book_count_cache
from account.decorators import ajax_login_required, ajax_verify_required
from network.models import Network, Department
from amazon import search_by_keywords, get_by_isbn

from facebook import facebook
from facebook.models import FacebookUser

import logging
logger = logging.getLogger(__name__)

NUM_PER_PAGE = 10


def book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    other_editions = book.other_editions.all()
    
    # get copies for all editions
    all_copies = book.copies.all()
    copies = []
    requested_copies = []
    for copy in all_copies:
        if copy.status == 2:
            copies.append(copy)
            if request.user.is_authenticated() and copy.trades.filter(buyer=request.user, request_status=0):
                requested_copies.append(copy)
    
    for each_edition in other_editions:
        other_copies = each_edition.copies.all()
        for copy in other_copies:
            if copy.status == 2:
                copies.append(copy)
                if request.user.is_authenticated() and copy.trades.filter(buyer=request.user, request_status=0):
                    requested_copies.append(copy)
    
    # find number of copies
    copy_count = len(copies)
    
    wishlists = Wishlist.objects.filter(book=book).order_by('-add_time')[:3]
    wishers = [wishlist.user for wishlist in wishlists]
    wisher_count = book.wish_users.count()
    
    courses = book.courses.all()
    
    prices = book.prices
    
    # if is my own or my wish
    my_copy = None
    my_wish = None
    
#    related_books = book.get_related_books()
    
    if request.user.is_authenticated():
        try:
            my_copy = BookCopy.objects.get(owner=request.user, book=book)
        except BookCopy.DoesNotExist:
            try:
                my_wish = Wishlist.objects.get(user=request.user, book=book)
            except Wishlist.DoesNotExist:
                pass
    else:
        if 'own_books' in request.session and unicode(book.id) in request.session['own_books']:
            my_copy = book.id
        elif 'wish_books' in request.session and unicode(book.id) in request.session['wish_books']:
            my_wish = book.id
    
    args = {
        'book': book,
        'other_editions': other_editions,
        'copies': copies,
        'copy_count': copy_count,
        'wishers': wishers,
        'wisher_count': wisher_count,
        'courses': courses,
        'requested_copies': requested_copies,
        'my_copy': my_copy,
        'my_wish': my_wish,
        'prices': prices,
    }
    return render_to_response('book.html', args , context_instance=RequestContext(request))



def library(request):
    book_count = BookCopy.objects.count()
    new_copies = BookCopy.objects.order_by('-add_time')[0:5]
    new_books = set([copy.book for copy in new_copies])

    books_in_dept = {}
    if request.user.is_authenticated():
        departments = request.user.departments.all()
        for dept in departments:
            books_in_dept[dept.id] = []
            courses = dept.courses.all()
            for course in courses:
                books_in_dept[dept.id] += [book for book in course.books.all()]    
            books_in_dept[dept.id] = list(set(books_in_dept[dept.id]))
            if len(books_in_dept[dept.id]) > 5:
                books_in_dept[dept.id] = books_in_dept[dept.id][0:5]
            books_in_dept[dept.id] = {'name':dept.name, 'books': books_in_dept[dept.id]}
            
    most_wanted = Book.objects.most_wanted()
    wanted = [book for book in most_wanted]

    args = {
        'new_books': new_books,
        'books_in_dept': books_in_dept,
#        'network_slug': request.user.profile.network.name_slug,
        'book_count': book_count,
        'wanted': wanted
    }
    return render_to_response('library/library_home.html', args, context_instance=RequestContext(request))


def departments(request, network_slug):
    network = get_object_or_404(Network, name_slug=network_slug)
    departments = network.departments.order_by('name')
    args = {
        'network_slug': network.name_slug,
        'departments': departments,
    }
    return render_to_response('library/library_departments.html', args, context_instance=RequestContext(request))    


def dept(request, network_slug, dept_id):
    dept = get_object_or_404(Department, id=dept_id)
    courses = dept.courses.order_by('name')
    books = {}
    for course in courses:
        books[course.name] = [book for book in course.books.all()]
        
    args = {
        'dept': dept,
        'dept_books': books,
        'network_slug': network_slug,
    }
    return render_to_response('library/library_dept.html', args, context_instance=RequestContext(request))    
    


def lookup(request, lookup_type):
    if lookup_type == 'book':
        lookup = BookLookup()
        return lookup.results(request)
    elif lookup_type == 'department':
        lookup = DepartmentLookup()
        return lookup.results(request)



def own_book(request):
    result = { 'success': False }
    if request.is_ajax() and request.method == 'POST':
        copy_id = -1
        book_id = request.POST.get('book_id').strip()
        if request.user.is_authenticated():
            book = Book.objects.get(id=book_id)
            copy, created = BookCopy.objects.get_or_create(book=book, owner=request.user)
            copy_id = copy.id
            reset_book_count_cache(request)
        else:
            if 'own_books' not in request.session or not request.session['own_books']:
                request.session['own_books'] = []
            if unicode(book_id) not in request.session['own_books']:
                books = request.session['own_books']
                books.append(book_id)
                request.session['own_books'] = books
        result = {'success': True, 'copy_id': copy_id}
    content = simplejson.dumps(result)
    return HttpResponse(content, content_type='application/json')


def remove_book(request):
    result = { 'success': False }
    if request.is_ajax() and request.method == 'POST':
        book_id = request.POST.get('book_id').strip()
        if request.user.is_authenticated():
            book = Book.objects.get(id=book_id)
            try:
                copy = BookCopy.objects.get(book=book, owner=request.user)
                copy.delete()
                reset_book_count_cache(request)
            except BookCopy.DoesNotExist:
                pass
        elif 'own_books' in request.session and unicode(book_id) in request.session['own_books']:
            own_books = request.session['own_books']
            own_books.remove(book_id)
            request.session['own_books'] = own_books
        result = { 'success': True }
    content = simplejson.dumps(result)
    return HttpResponse(content, content_type='application/json')


def wish_book(request):
    result = { 'success': False }
    if request.is_ajax() and request.method == 'POST':
        book_id = request.POST.get('book_id').strip()
        if request.user.is_authenticated():
            book = Book.objects.get(id=book_id)
            wish_book, created = Wishlist.objects.get_or_create(book=book, user=request.user)
            
        #    graph = facebook.GraphAPI(FacebookUser.objects.filter(user=request.user))
        #    graph.put_wall_post("I wish to have this book: %s" % book.title)
        else:
            if 'wish_books' not in request.session or not request.session['wish_books']:
                request.session['wish_books'] = []
            if unicode(book_id) not in request.session['wish_books']:
                books = request.session['wish_books']
                books.append(book_id)
                request.session['wish_books'] = books
        result = { 'success': True }
    content = simplejson.dumps(result)
    return HttpResponse(content, content_type='application/json')


def remove_wish_book(request):
    result = { 'success': False }
    if request.is_ajax() and request.method == 'POST':
        book_id = request.POST.get('book_id').strip()
        if request.user.is_authenticated():
            book = Book.objects.get(id=book_id)
            try:
                wish = Wishlist.objects.get(book=book, user=request.user)
                wish.delete()
            except Wishlist.DoesNotExist:
                pass
        elif 'wish_books' in request.session and unicode(book_id) in request.session['wish_books']:
            wish_books = request.session['wish_books']
            wish_books.remove(book_id)
            request.session['wish_books'] = wish_books
        result = { 'success': True }
    content = simplejson.dumps(result)
    return HttpResponse(content, content_type='application/json')



def load_copy(request):
    result = { 'success': False }
    if request.is_ajax() and request.method == 'GET':
        copy_id = request.GET.get('copy_id').strip()
        copy = BookCopy.objects.get(id=copy_id)
        list_price = copy.book.list_price
        if not list_price:
            list_price = 0
        result = {
            'success': True,
            'condition': copy.condition,
            'notes': copy.notes,
            'list_price': copy.book.list_price,
            'lease_price': copy.lease_price,
            'sale_price': copy.sale_price,
            'lease_range': get_price_range(list_price, 'lease'),
            'sale_range': get_price_range(list_price, 'sale'),
            'deposit': copy.get_deposit(),
        }
    content = simplejson.dumps(result)
    return HttpResponse(content, content_type='application/json')
    

def compute_price(request):
    result = { 'success': False }
    if request.is_ajax() and request.method == 'GET':
        price = request.GET.get('price').strip()
        type = request.GET.get('type').strip()
        try:
            price = int(price)
        except Exception:
            price = 0
        buyer_price = get_buyer_price(price, type)
        result = {
            'success': True,
            'price': buyer_price
        }
    content = simplejson.dumps(result)
    return HttpResponse(content, content_type='application/json')
    

@ajax_login_required
def edit_copy(request):
    result = {'success': False}
    if request.is_ajax() and request.method == 'POST':
        copy_id = request.POST.get('copy_id').strip()
        condition = request.POST.get('condition').strip()
        notes = request.POST.get('notes').strip()
        lease_price = request.POST.get('lease_price').strip()
        sale_price = request.POST.get('sale_price').strip()
        copy = BookCopy.objects.get(id=copy_id)
        
        # make sure it's the owner changing the copy
        if copy.owner.id == request.user.id:
            copy.condition = condition
            copy.notes = notes
            # make book available
            if copy.status == 0 and (lease_price or sale_price):
                copy.status = 2
            if lease_price:
                copy.lease_price = get_buyer_price(_to_int(lease_price), 'lease')
            if sale_price:
                copy.sale_price = get_buyer_price(_to_int(sale_price), 'sale')
            copy.save()
            result = {'success': True}
    content = simplejson.dumps(result)
    return HttpResponse(content, content_type='application/json')



def search(request):
    term = request.GET.get('q', '').strip()
    amazon_info = []
#    bookstore_info = []
    book_results = []
    if term != '':
        saved_term = request.session.get('term', '')
        saved_results = request.session.get('books', [])
        if saved_term == term and saved_results:
            book_results = saved_results
        else:
            if _is_isbn(term):
                book_results = Book.objects.filter(isbn__contains=term)
                if not book_results:
                    logger.error('not result found for isbn')
                    amazon_info = get_by_isbn(term)
            elif _is_course_name(term):
                book_results = Book.objects.filter(courses__keywords__icontains=term).distinct()
    #            if not book_results:
    #                bookstore_info = bookstore_info+(fetchBooks(quarter='Summer', course=term))
    #                bookstore_info = bookstore_info+(fetchBooks(quarter='Autumn', course=term))
    #                bookstore_info = removeBookDuplicates(bookstore_info)
            else:
                book_results = Book.objects.filter(title__icontains=term)
            #    if not book_results:
            #        book_results = Book.objects.filter(courses__name__icontains=term).distinct()
                if not book_results:
                    pass
                    #amazon_info = search_by_keywords(term, settings.AMAZON_QUERY_COUNT)
                        
        #    if bookstore_info:
        #        logger.info('query through bookstore')
        #        
        #        book_results = []
        #        for info in bookstore_info:
        #            book, created = Book.objects.get_or_create(
        #                isbn=info['isbn'],
        #            )
        #            # make book price object
        #            if created:
        #                book.title=info['title']
        #                book.list_price=info['new_price']
        #                book.save()
        #                BookPrices.objects.create(book=book, ubookstore_new=info['new_price'], ubookstore_used=info['used_price'])
        #            book_results.append(book)
                
            if amazon_info:
                logger.info('query through amazon')
                
                book_results = []
                for info in amazon_info:
                    try_book = Book.objects.filter(isbn__contains=info['isbn'])
                    if try_book:
                        book_results.extend(try_book)
                    else:
                        book = Book.objects.create(
                            isbn=info['isbn'],
                            title=info['title'],
                            edition=info['edition'],
                            authors=info['authors'],
                            format=info['format'],
                            publisher=info['publisher'],
                            publication_date=info['publication_date'],
                            list_price=info['list_price']
                        )
                        book.save()
                        # todo: move it to task queue
                        try:
                            # save book image to file
                            image_temp = NamedTemporaryFile(delete=True)
                            image_temp.write(urllib2.urlopen(info['image_url']).read())
                            image_temp.flush()
                            book.image.save(info['image'], File(image_temp), save=True)
                        except Exception:
                            logger.error('unknown exception when saving book image from Amazon')
            
                        # make book price object
                        BookPrices.objects.create(book=book)
                        book_results.append(book)   
            request.session['term'] = term
            request.session['books'] = book_results
    
    paginator = Paginator(book_results, NUM_PER_PAGE)
    
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    
    try:
        page_results = paginator.page(page)
    except (EmptyPage, InvalidPage):
        page_results = paginator.page(paginator.num_pages)
        
    args = {
        'term': term,
        'books': page_results,
        'total': paginator.count,
    }

    return render_to_response('search_results.html', args, context_instance=RequestContext(request))


def search_amazon(term):
    results = []
    if term:
        amazon_results = None
        
        if _is_isbn(term):
            amazon_results = get_by_isbn(term)
        else:
            amazon_results = search_by_keywords(term, settings.AMAZON_QUERY_COUNT)
        
        if amazon_results:
            for info in amazon_results:
                book = Book.objects.create(
                    isbn=info['isbn'],
                    title=info['title'],
                    edition=info['edition'],
                    authors=info['authors'],
                    format=info['format'],
                    publisher=info['publisher'],
                    publication_date=info['publication_date'],
                    list_price=info['list_price']
                )
                book.save()
                # todo: move it to task queue
                try:
                    # save book image to file
                    image_temp = NamedTemporaryFile(delete=True)
                    image_temp.write(urllib2.urlopen(info['image_url']).read())
                    image_temp.flush()
                    book.image.save(info['image'], File(image_temp), save=True)
                except Exception:
                    logger.error('unknown exception when saving book image from Amazon')

                # make book price object
                BookPrices.objects.create(book=book)
                results.append(book)
    
    return results
    