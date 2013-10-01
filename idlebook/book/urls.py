from django.conf.urls.defaults import *

urlpatterns = patterns('idlebook.book.views',
    # book
    url(r'^book/(?P<book_id>\d+)/$', 'book', name='book'),
    
    # library
    url(r'^library/$', 'library', name='library'),
    url(r'^library/(?P<network_slug>\w+)/depts/$', 'departments', name='departments'),
    url(r'^library/(?P<network_slug>\w+)/depts/(?P<dept_id>\d+)/$', 'dept', name='dept'),
    
    # search
    url(r'^search/', 'search', name='search'),

    # ajax lookup
    url(r'^lookup/(?P<lookup_type>(book|department))/$', 'lookup', name='lookup'),
    url(r'^own_book/$', 'own_book', name='own_book'),
    url(r'^wish_book/$', 'wish_book', name='wish_book'),
    url(r'^remove_book/$', 'remove_book', name='remove_book'),
    url(r'^remove_wish_book/$', 'remove_wish_book', name='remove_wish_book'),
    url(r'^load_copy/$', 'load_copy', name='load_copy'),
    url(r'^edit_copy/$', 'edit_copy', name='edit_copy'),
    url(r'^compute_price/$', 'compute_price', name='compute_price'),
    
)