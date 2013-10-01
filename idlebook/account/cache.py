from django.core.cache import cache
from book.models import BookCopy

def reset_wallet_cache(request):
    unread = request.user.wallet.unread
    cache.set('%s-unread_wallet' % request.user.id, unread, 10000)
    return unread


def reset_unread_cache(user):
    trades = user.sells.filter(request_status__lt=4)
    received_count = 0
    for trade in trades:
        if trade.action_required('seller'):
            received_count +=1

    cache.set('%s-unread_received' % user.id, received_count, 10000)

    trades = user.buys.filter(request_status__lt=4)
    sent_count = 0
    for trade in trades:
        if trade.action_required('buyer'):
            sent_count +=1
    cache.set('%s-unread_sent' % user.id, sent_count, 10000)
    
    cache.set('%s-unread_total' % user.id, received_count + sent_count, 10000)
    
    return received_count, sent_count

    
def reset_book_count_cache(request):
    count = BookCopy.objects.count()
    cache.set('book_count', count, 10000)
    return count