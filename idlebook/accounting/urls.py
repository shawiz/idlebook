from django.conf.urls.defaults import *

urlpatterns = patterns('idlebook.accounting.views',
    url(r'^book/(?P<book_id>\d+)/$', 'book_trades', name='book_trades'),
    url(r'^pay/', 'pay', name='pay'),
    url(r'^deposit/', 'deposit', name='deposit'),
    url(r'^action/', 'action', name='action'),
)