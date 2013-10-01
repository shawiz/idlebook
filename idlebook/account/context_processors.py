from django.core.cache import cache
from cache import reset_unread_cache, reset_book_count_cache, reset_wallet_cache
from time import time

def unread_wallet(request):
    if request.user.is_authenticated():
        unread = cache.get('%s-unread_wallet' % request.user.id)
        if unread == None:
            unread = reset_wallet_cache(request)
    else:
        unread = False
    return {'unread_wallet': unread}


def unread_requests(request):
    if request.user.is_authenticated():
        count = cache.get('%s-unread_total' % request.user.id)
        if not count:
            tuple = reset_unread_cache(request.user)
            count = tuple[0]+tuple[1]
    else:
        count = None
    return {'unread_requests': count}


def unread_requests_received(request):
    if request.user.is_authenticated():
        count = cache.get('%s-unread_received' % request.user.id)
        if not count:
            tuple = reset_unread_cache(request.user)
            count = tuple[0]
    else:
        count = None
    return {'unread_requests_received': count}


def unread_requests_sent(request):
    if request.user.is_authenticated():
        count = cache.get('%s-unread_sent' % request.user.id)
        if not count:
            tuple = reset_unread_cache(request.user)
            count = tuple[1]
    else:
        count = None
    return {'unread_requests_sent': count}
    
    
def total_book_count(request):
    count = cache.get('book_count')
    if not count:
        count = reset_book_count_cache(request)
    return {'total_book_count': count}


def timestamp(request):
    return {'timestamp': time()}
