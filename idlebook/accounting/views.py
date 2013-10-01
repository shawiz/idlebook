from operator import itemgetter
import datetime
from django.conf import settings
from django.utils import simplejson
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages as flash

from models import *
from idlebook.account.models import *
from idlebook.book.models import *
from idlebook.book.utils import *

from idlebook.book.utils import _to_int

@login_required
def book_trades(request, book_id):
    if not request.user.is_staff:
        flash.warning(request, "You don't have permissions to do this operation. Redirected to book.")
        return HttpResponseRedirect('/book/%s' % book_id)

    book = get_object_or_404(Book, id=book_id)
    copies = book.copies.all()
    trades_info = []

    for copy in copies:
        trades = copy.trades.filter(request_status__gte=1).order_by('-update_time')
        for t in trades:
            type = t.get_type()
            price, price_type = t.get_price()
            dropoff_time = ''
            return_time = ''
            if type == 'lease':
                dropoff_time = t.lease.dropoff_time
                return_time = t.lease.return_time
            
            role = t.get_responder()
            
            if not price:
                price = 0
            
            if t.payment_status == 1:
                balance_needed = 0
                deposit_needed = 0
                total_needed = 0
            else:
                balance_needed = max(0, price - t.buyer.wallet.regular_balance)
                deposit_needed = 0
                if type == 'lease':
                    deposit_needed = t.lease.deposit
                total_needed = max(0, (price + deposit_needed) - t.buyer.wallet.regular_balance)
            
            trade = {
                'id': t.id,
                'time': t.update_time,
                'seller': t.seller,
                'buyer': t.buyer,
                'role': role,
                'type': type,
                'price': price,
                'price_type': price_type,
                'balance_needed': balance_needed,
                'deposit': deposit_needed,
                'total_needed': total_needed,
                'state': t.current_state,
                'payment_status': t.payment_status,
                'add_time': t.add_time,
                'deposit_time': t.deposit_time,
                'pickup_time': t.pickup_time,
                'dropoff_time': dropoff_time,
                'return_time': return_time,
                'sequence': t.sequence,
            }
            trades_info.append(trade)
    
    args = {
        'book': book,
        'trades': trades_info
    }
    return render_to_response('trades.html', args, context_instance=RequestContext(request))


@login_required
def deposit(request):
    if not request.user.is_staff:
        flash.warning(request, "You don't have permissions to do this operation. Redirected to home.")
        return HttpResponseRedirect('/')
    
    if request.method == 'POST':
        trade_id = request.POST.get('trade_id').strip()
        amount = _to_int(request.POST.get('amount').strip())
        trade = get_object_or_404(Trade, id=trade_id)
        person = trade.buyer
        book_id = trade.book_copy.book.id
        Transaction.objects.deposit(person, trade, amount)
        
        return HttpResponseRedirect('/manage/book/%s' % book_id)


@login_required
def pay(request):
    if not request.user.is_staff:
        flash.warning(request, "You don't have permissions to do this operation. Redirected to home.")
        return HttpResponseRedirect('/')
    if request.method == 'POST':
        trade_id = request.POST.get('trade_id').strip()
        trade = get_object_or_404(Trade, id=trade_id)
        book_id = trade.book_copy.book.id
        
        price, price_type = trade.get_price()
        trade_type = trade.get_type()
        commission = get_commission(price, trade_type)
        earning = price - commission
        deposit = trade.lease.deposit if trade_type == 'lease' else 0
        
        Transaction.objects.transfer(trade.buyer, trade.seller, trade, price, earning, deposit)
        trade.payment_status = 1
        trade.save()
        
        return HttpResponseRedirect('/manage/book/%s' % book_id)


@login_required
def action(request):
    if not request.user.is_staff:
        flash.warning(request, "You don't have permissions to do this operation. Redirected to home.")
        return HttpResponseRedirect('/')
    if request.method == 'POST':
        trade_id = request.POST.get('trade_id').strip()
        trade = get_object_or_404(Trade, id=trade_id)
        book_id = trade.book_copy.book.id
        role = trade.get_responder()
        post = request.POST.copy()
        action_code = 0
        action_name = ''
        if 'accept' in post:
            action_code = 1
        elif 'reject' in post:
            action_code = 2
                
        if trade.current_state == 20 and action_code == 1 and trade.payment_status == 0:
            flash.warning(request, "Buyer hasn't paid yet!")
            return HttpResponseRedirect('/manage/book/%s' % book_id)
        else:
            try:
                trade.move_state(role, action_code)
                if trade.current_state == 40:
                    Transaction.objects.return_deposit(trade.buyer, trade)                
            #    if role == 'seller':
            #        t.unread('buyer')
            #    else:
            #        t.unread('seller')
            #    t.save()

            except Exception:
                pass
        
            return HttpResponseRedirect('/manage/book/%s' % book_id)    
    
