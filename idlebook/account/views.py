import re
import datetime
from operator import itemgetter

from django.utils import simplejson
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required #, user_passes_test
from django.contrib import messages as flash
from django.contrib.auth.forms import PasswordChangeForm

from models import *
from forms import *
from cache import reset_unread_cache, reset_wallet_cache
from decorators import *
from account import notifications
from accounting.models import Transaction
from book.models import *
from book.utils import get_buyer_price, _to_int, duration
from network.models import Department
from facebook.models import *



def index(request):
#    errors = ""
#    if request.method == 'POST':
#        form = StartForm(request.POST)
#        if form.is_valid():
#            email = form.cleaned_data['email']
#            request.session['email'] = email[:email.find('@')]
#            return HttpResponseRedirect('/signup/')
#        else:
#            errors = form.errors
#    
#    form = StartForm()
    
#    args = {
#        'form': form,
#        'errors': errors,
#    }
    if request.user.is_authenticated():
        return HttpResponseRedirect('/profile/')
    return render_to_response('index.html', {}, context_instance=RequestContext(request))


def server_error(request):
    """
    500 error handler.

    Templates: `500.html`
    """
    return render_to_response('500.html', {}, context_instance=RequestContext(request))


def debug_signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            user = auth.authenticate(username=form.cleaned_data['email'], password=form.cleaned_data['password'])
            auth.login(request, user)
            
            # save some data for the user
            if 'own_books' in request.session and request.session['own_books']:
                own_books = request.session['own_books']
                for book_id in own_books:
                    book = Book.objects.get(id=book_id)
                    copy, created = BookCopy.objects.get_or_create(book=book, owner=user)
            if 'wish_books' in request.session and request.session['wish_books']:
                wish_books = request.session['wish_books']
                for book_id in wish_books:
                    book = Book.objects.get(id=book_id)
                    wish, created = Wishlist.objects.get_or_create(book=book, user=user)
                    
            return HttpResponseRedirect('/profile/')
    else:        
        init_data = {}
        if 'email' in request.session:
            init_data = { 'email': request.session['email'] }
            del request.session['email']
        form = SignupForm(init_data)
    return render_to_response('signup.html', {'form': form}, context_instance=RequestContext(request))



def debug_login(request):
    next = request.REQUEST.get('next', '/')
    errors = ""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = auth.authenticate(username=email, password=password)
            if user is not None:
                if user.is_active:
                    if not request.POST.get('remember_me', None):
                        request.session.set_expiry(0)
                    auth.login(request, user)
                    return HttpResponseRedirect('/')
                else:
                    errors = "Your account is disabled."
            else:
                errors = "Your email and password doesn't match. Please try again."
    else:
        form = LoginForm()
    return render_to_response('login.old.html', {'form': form, 'next':next }, context_instance=RequestContext(request))



def login(request):
    prev = request.META.get('HTTP_REFERER','/')
    next = request.REQUEST.get('next', '/')
    return render_to_response('login.html', {'next':next, 'prev':prev }, context_instance=RequestContext(request))


def logout(request):
    if request.method == 'POST' and 'logout' in request.POST:
        auth.logout(request)
        return HttpResponseRedirect('/')


@ajax_login_required
def send_confirmation(request):
    result = {'success': False}
    if request.is_ajax() and request.method == 'POST':
        EmailConfirmation.objects.send_confirmation(request.user.email, request.user.profile)
        result = {'success': True}
    content = simplejson.dumps(result)
    return HttpResponse(content, content_type='application/json')


def confirm_email(request, confirmation_key):
    """
    Used when confirming a email open from email
    
    """
    confirmation_key = confirmation_key.lower()
    profile = EmailConfirmation.objects.confirm_email(confirmation_key)
    
    return render_to_response('small/email_confirmed.html', {'profile': profile, 'prev':request.META.get('HTTP_REFERER','/')}, context_instance=RequestContext(request))


@login_required
def verify_email(request):
    return render_to_response('small/email_verify.html', {'prev':request.META.get('HTTP_REFERER','/')}, context_instance=RequestContext(request))


@login_required
def notification(request):
    """
    Redirect to notification settings
    """
    return HttpResponseRedirect('/settings/notifications/')
    

@login_required
def profile(request):
    return HttpResponseRedirect('/person/' + request.user.profile.username)


def person(request, username):
    person = get_object_or_404(UserProfile, username=username).user

    # show requests of other to current user
#    requests = Trade.objects.filter(borrower=person, lender=request.user)
#    book_request = None
#    if requests:
#        book_request = requests[0]
#    else:
#        requests = Trade.objects.filter(lender=person, borrower=request.user)
#        if requests:
#            book_request = requests[0]

    args = fetch_profile(request, person)
    listings = []
    for copy in person.own_books.all().order_by('-add_time'):
        item = {}
        item['book'] = copy.book
        item['courses'] = [course for course in copy.book.courses.all()]
        item['copy'] = copy
        item['condition'] = copy.get_condition_display()
        listings.append(item)
    args['listings'] = listings
    args['own_tab_class'] = ' class=active'
    
    return render_to_response('profile/profile_own.html', args, context_instance=RequestContext(request))


def person_list(request, username, list):
    person = get_object_or_404(UserProfile, username=username).user
    args = fetch_profile(request, person)
    active_class = ' class=active'
    
    if list == 'wishlist':
        wish_books = []
        for book in person.wish_books.all():
            item = {
                'book': book,
                'courses': [course for course in book.courses.all()]
            }
            wish_books.append(item)
        args['wish_books'] = wish_books
        args['wish_tab_class'] = active_class
        
    elif list == 'reviews':
        args['reviews_as_buyer'] = person.received_reviews.filter(role=0).order_by('-update_time')
        args['reviews_as_seller'] = person.received_reviews.filter(role=1).order_by('-update_time')
        args['reviews_tab_class'] = active_class
    
    return render_to_response('profile/profile_%s.html'%list, args, context_instance=RequestContext(request))
    

def public_list(request, username, list):
    """
    A list of books a user owns and wishes. Everyone can see, including non-users.
    """
    if request.user.is_authenticated:
        return HttpResponseRedirect('/person/%s/%s/' % (username, list))
    else:
        person = get_object_or_404(UserProfile, username=username).user
        args = fetch_profile(request, person)

        if list == 'listings':
            listings = []
            for copy in person.own_books.all().order_by('-add_time'):
                item = {}
                item['book'] = copy.book
                item['courses'] = [course for course in copy.book.courses.all()]
                item['copy'] = copy
                listings.append(item)
            args['listings'] = listings

        elif list == 'wishlist':
            wish_books = []
            for book in person.wish_books.all():
                item = {}
                item['book'] = book
                item['courses'] = [course for course in book.courses.all()]
                wish_books.append(item)

            args['wish_books'] = wish_books

        return render_to_response('profile/public_profile_%s.html'%list, args, context_instance=RequestContext(request))


def fetch_profile(request, person):
    facebook_id = None
    if request.user.is_authenticated() and person.profile.has_permission(request.user):
        try:
            fb_user = FacebookUser.objects.get(user=person)
            facebook_id = fb_user.facebook_id
        except FacebookUser.DoesNotExist:
            pass
    
    return {
        'person': person,
        'profile': person.profile,
        'own_count': person.own_books.count(),
        'wish_count': person.wish_books.count(),
        'lending_count': Lease.objects.filter(seller=person, request_status=1).count(),
        'borrowing_count': Lease.objects.filter(buyer=person, request_status=1).count(),
        'departments': person.departments.all(),
        'response_rate': person.profile.get_response_rate(),
        'is_myself': person.id == request.user.id,
        'borrowed_count': Lease.objects.filter(buyer=person, request_status__gte=1).count(),
        'lent_count': Lease.objects.filter(seller=person, request_status__gte=1).count(),
        'facebook_id': facebook_id
    }



@login_required
def settings(request):
    return HttpResponseRedirect('/settings/account/')


@ajax_login_required
def check_username(request):
    result = {'success': False}
    if request.is_ajax() and request.method == 'POST':
        username = request.POST.get('username').strip()
        number_match = re.match(r'^\d+$', username)
        if number_match:
            result['error'] = 'Your username cannot just contain numbers'
        else:
            match = re.match(r'^[\w]{3,}$', username)
            if not match:
                result['error'] = "The username can only contain the alphabet, numbers and underscores, three characters or longer"
            else:
                try:
                    UserProfile.objects.get(username=username)
                    result['error'] = "The username has already exist. Please try a different one"
                except UserProfile.DoesNotExist:
                    reserved_words = ['about', 'aboutus', 'account', 'admin', 'administer', 'administor', 'administrater', 
                                    'administrator', 'anonymous', 'author', 'book', 'blog', 'contact', 'contactus',
                                    'data', 'delete', 'edit', 'editer', 'editor', 'email', 'emailus', 'faq', 'ftp', 
                                    'guest', 'help', 'hello', 'info', 'library', 'login', 'logout', 'login', 'logout', 
                                    'master', 'media', 'moderater', 'moderator', 'money', 'mail', 'mysql', 'news', 'nobody', 
                                    'operater', 'operator', 'oracle', 'owner', 'password', 'person', 'people', 'postmaster', 
                                    'president', 'profile', 'public', 'registar', 'register', 'registrar', 'request', 'requests', 
                                    'root', 'r00t', 'sales', 'setting', 'settings', 'signup', 'signin', 'signout', 'student', 
                                    'support', 'system', 'test', 'test1', 'testing', 'user', 'upload', 'vicepresident', 'wallet', 
                                    'web', 'webadmin', 'webmaster', 'www', 'wwwrun', 
                                    '123', '1234', '12345', '123456', '1234567',
                                    'facebook', 'google', 'amazon', 'microsoft', 'apple', 'twitter', 'idle', 'idlebook', 
                                    'washington', 'harvard', 'stanford', 'mit', 'yale', 'princeton']
                    if username in reserved_words:
                        result['error'] = "The username you entered is reserved. Please try a different one"
                    else:
                        result = {'success': True}
    content = simplejson.dumps(result)
    return HttpResponse(content, content_type='application/json')


@ajax_login_required
@ajax_verify_required
def set_username(request):
    result = { 'success': False }
    if request.is_ajax() and request.method == 'POST':
        username = request.POST.get('username').strip()
        try:
            UserProfile.objects.get(username=username)
            result['error'] = "The username has already exist"
        except UserProfile.DoesNotExist:
            profile = request.user.profile
            profile.username = username
            profile.has_username = True
            profile.save()
            result = { 'success': True }
    content = simplejson.dumps(result)
    return HttpResponse(content, content_type='application/json')


@login_required
def settings_tab(request, tab):
    if tab == 'account':
        profile = get_object_or_404(UserProfile, user=request.user)
        facebook_linked = True
        try:
            fb_user = FacebookUser.objects.get(user=request.user)        
        except FacebookUser.DoesNotExist:
            facebook_linked = False
        
        return render_to_response('settings/settings_account.html', {'facebook_linked': facebook_linked}, context_instance=RequestContext(request))

#    elif tab == 'password':
#        if request.method == 'POST':
#            form = PasswordChangeForm(user=request.user, data=request.POST)
#            if form.is_valid():
#                form.save()
#                flash.success(request, "Your password is updated")
#                return HttpResponseRedirect('/settings/password/')
#        else:
#            profile = get_object_or_404(UserProfile, user=request.user)
#            form = PasswordChangeForm(user=request.user)
#        return render_to_response('settings_password.html', {'form': form}, context_instance=RequestContext(request))
        
    elif tab == 'profile':
        if request.method == 'POST':
            form = ProfileForm(request.POST)
            if form.is_valid():
                form.save(request.user)
                return HttpResponseRedirect('/settings/profile/')
        else:
            init_data = {
                'about': request.user.profile.about,
                'rules': request.user.profile.rules,
            }
            form = ProfileForm(init_data)
        return render_to_response('settings/settings_profile.html', {'form': form}, context_instance=RequestContext(request))

    elif tab == 'network':
        network = request.user.profile.network
        departments = request.user.departments.all()
        args = {
            'user': request.user,
            'network': network,
            'departments': departments
        }
        return render_to_response('settings/settings_network.html', args, context_instance=RequestContext(request))
    
    elif tab == 'notifications':
        notification_instance = NotificationSettings.objects.get(user=request.user)
        logger.error("entering notification:")
        if request.method == 'POST':
            form = NotificationForm(request.POST, instance=notification_instance)
            logger.error(str(form.errors))
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/settings/notifications/')
        else:
            form = NotificationForm(instance=notification_instance)
        return render_to_response('settings/settings_notifications.html', {'form': form}, context_instance=RequestContext(request))
        

@ajax_login_required
def add_department(request):
    result = { 'success': False }
    if request.is_ajax() and request.method == 'POST':
        dept_id = request.POST.get('dept_id').strip()
        dept = get_object_or_404(Department, id=dept_id)
        if request.user.is_authenticated():
            request.user.departments.add(dept)
        else:
            if 'depts' not in request.session or not request.session['depts']:
                request.session['depts'] = []
            depts = request.session['depts']
            depts.append(dept_id)
            request.session['depts'] = depts
        result = { 'success': True }
    content = simplejson.dumps(result)
    return HttpResponse(content, content_type='application/json')


@ajax_login_required
def remove_department(request):
    result = { 'success': False }
    if request.is_ajax() and request.method == 'POST':
        dept_id = request.POST.get('dept_id').strip()
        dept = get_object_or_404(Department, id=dept_id)
        if request.user.is_authenticated():
            request.user.departments.remove(dept)
        elif 'depts' in request.session and dept_id in request.session['depts']:
            request.session['depts'].remove(dept_id)
        result = { 'success': True }
    content = simplejson.dumps(result)
    return HttpResponse(content, content_type='application/json')



@login_required
def wallet(request):
    wallet = request.user.wallet
    incomes = request.user.incomes.order_by('-add_time')
    transactions = request.user.transactions.order_by('-add_time')
    
    results = []
    for income in incomes:
        t = {
            'add_time': income.add_time,
            'title': income.trade.book_copy.book.title,
            'trade_id': income.trade.id,
            'from': income.buyer.profile,
            'to': 'Account',
            'amount': '+%s' % income.earning,
            'balance': income.seller_balance,
            'type': income.trade.get_type(),
            'trans_type': 4
        }
        results.append(t)
    
    for transaction in transactions:
        trans_type = transaction.type
        t = {
            'add_time': transaction.add_time,
            'balance': transaction.buyer_balance,
            'deposit': transaction.buyer_deposit,
            'trans_type': trans_type,
        }
        if trans_type == 1: # deposit
            t['title'] = 'Card Swipe'
            t['trade_id'] = None
            t['from'] = 'Card'
            t['to'] = 'Account'
            t['amount'] = "+%s" % transaction.earning
        elif trans_type == 2: # withdraw (aka cash out)
            t['title'] = 'Cash Out'
            t['trade_id'] = None
            t['from'] = 'Account'
            t['to'] = 'Check'
            t['amount'] = "-%s" % transaction.payment
        elif trans_type == 3: # deposit return to balance
            t['title_text'] = 'Deposit return for: '
            t['title'] = transaction.trade.book_copy.book.title
            t['trade_id'] = transaction.trade.id
            t['from'] = 'Deposit'
            t['to'] = 'Account'
            t['amount'] = '+%s' % -transaction.deposit
        elif trans_type == 0: # transfer
            t['title'] = transaction.trade.book_copy.book.title
            t['trade_id'] = transaction.trade.id
            if transaction.trade.get_type() == 'sale':
                t['type'] = 'sale'
                t['from'] = 'Account'
                t['to'] = transaction.seller.profile
                t['amount'] = '-%s' % transaction.payment
            else:
                t['type'] = 'lease'
                t['from_top'] = 'Account'
                t['to_top'] = transaction.seller.profile
                t['from_bot'] = 'Account'
                t['to_bot'] = 'Deposit'
                t['amount_top'] = '-%s' % transaction.payment
                t['amount_bot'] = '-%s' % transaction.deposit
        results.append(t)
    
    results = sorted(results, key=itemgetter('add_time'))
    results.reverse()
    
    request.user.wallet.unread = False
    request.user.wallet.save()
    reset_wallet_cache(request)
    
    args = {'wallet': request.user.wallet, 'results': results}
    return render_to_response('wallet/wallet_credits.html', args, context_instance=RequestContext(request))


@login_required
def get_balance(request):
    result = { 'success': False }
    if request.is_ajax() and request.method == 'GET':    
        result = {
            'success': True,
            'regular_balance': request.user.wallet.regular_balance,
            'reserved_balance': request.user.wallet.reserved_balance
        }
    content = simplejson.dumps(result)
    return HttpResponse(content, content_type='application/json')


@login_required
@verify_required
def order_check(request):
    if request.method == 'POST':
        realname = request.POST.get('realname').strip()
        amount = _to_int(request.POST.get('amount').strip())
        address = request.POST.get('address').strip()
        city = request.POST.get('city').strip()
        state = request.POST.get('state').strip()
        zipcode = request.POST.get('zipcode').strip()
        wallet = request.user.wallet
        
        # make sure the amount is ok
        if amount > wallet.regular_balance:
            flash.warning(request, "You cannot withdraw more than your current balance")
            return HttpResponseRedirect('/wallet/')
        
        request.user.checks.create(
            amount=amount,
            realname=realname,
            address=address,
            city=city,
            state=state,
            zipcode=zipcode,
        )
        Transaction.objects.withdraw(request.user, amount)
        
        flash.success(request, "You checked is ordered. You should be receiving the check in a few days.")
        return HttpResponseRedirect('/wallet/')



@login_required
def requests(request):
    trades = request.user.sells.filter(request_status__lt=4).order_by('-add_time')
    requests = get_requests(trades, 'seller')
    args = {'requests': requests}
    return render_to_response('requests/requests_received_open.html', args, context_instance=RequestContext(request))


@login_required
def requests_past(request):
    trades = request.user.sells.filter(request_status=4).order_by('-add_time')
    requests = get_requests(trades, 'seller')
    args = {'requests': requests}
    return render_to_response('requests/requests_received_past.html', args, context_instance=RequestContext(request))


@login_required
def requests_sent(request):
    trades = request.user.buys.filter(request_status__lt=4).order_by('-add_time')
    requests = get_requests(trades, 'buyer')
    args = {'requests': requests}
    return render_to_response('requests/requests_sent_open.html', args, context_instance=RequestContext(request))


@login_required
def requests_sent_past(request):
    trades = request.user.buys.filter(request_status=4).order_by('-add_time')
    requests = get_requests(trades, 'buyer')
    args = {'requests': requests}
    return render_to_response('requests/requests_sent_past.html', args, context_instance=RequestContext(request))


@login_required
@verify_required
def view_request(request, trade_id):
    t = get_object_or_404(Trade, id=trade_id)
    if t.buyer.id == request.user.id:
        role = 'buyer'
    elif t.seller.id == request.user.id:
        role = 'seller'
    else:
        flash.warning(request, "You don't have permissions to view this request. Redirected to your requests.")
        return HttpResponseRedirect('/requests/')

    if request.method == 'POST':
        content = request.POST.get('content')
        message = t.messages.create(
            sender = request.user,
            content = content
        )
#        if role == 'seller':
#            t.unread('buyer')
#        else:
#            t.unread('seller')
#        reset_unread_cache(request)
        return HttpResponseRedirect('/requests/%s/' % trade_id)

    else:
        messages_info = []
        messages = t.messages.all().order_by('add_time')
        for m in messages:
            messages_info.append({
                'id': m.id,
                'sender': m.sender,
                'content': m.content,
                'add_time': m.add_time
            })

#        if role == 'seller':
#            t.read('seller')
#        else:
#            t.read('buyer')
#        reset_unread_cache(request)
        
        args = {}
        args['request'] = fetch_trade(t)
        args['book_id'] = t.book_copy.book.id
        args['role'] = role
        args['trade_messages'] = messages_info

        return render_to_response('requests/requests_detail.html', args, context_instance=RequestContext(request))


def get_requests(trades, role):
    requests = []
    for t in trades:
        last_message = None
        try:
            if role == 'seller':
                last_message = t.messages.order_by('-add_time')[0:1].get()
                if last_message.sender.id != t.buyer.id:
                    last_message = None
            elif role == 'buyer':
                last_message = t.messages.order_by('-add_time')[0:1].get()
                if last_message.sender.id != t.seller.id:
                    last_message = None
        except TradeMessage.DoesNotExist:
            pass
        
        request_info = fetch_trade(t)
        request_info['last_message'] = last_message
        requests.append(request_info)
    return requests


def fetch_trade(t):
    trade_type = t.get_type()
    
    phase = t.get_phase()
    
    seller_notice = t.notice_available('seller')
    buyer_notice = t.notice_available('buyer')
    
    seller_action = t.action_required('seller')
    buyer_action = t.action_required('buyer')
    
    seller_response_class = 'action' if seller_action else 'notice'
    buyer_response_class = 'action' if buyer_action else 'notice'
        
    trade_info = {
        'id': t.id,
        'type': trade_type,
        'add_time': t.add_time,

        'copy_id': t.book_copy.id,        
        'image': t.book_copy.book.image,
        'title': t.book_copy.book.title,

        'price': t.original_price,
        'special_offer': t.special_offer,
        'paid': t.payment_status > 0,

        'buyer_username': t.buyer.profile.username,
        'buyer': t.buyer,
        'buyer_fullname': t.buyer.get_full_name(),
        'seller_username': t.seller.profile.username,
        'seller': t.seller,
        'seller_fullname': t.seller.get_full_name(),
        
        'state': t.current_state,
        'prev_state': t.previous_state,
        'phase': phase,

        'seller_notice': seller_notice,
        'buyer_notice': buyer_notice,
        'seller_required_action': seller_action,
        'buyer_required_action': buyer_action,
        'seller_response_class': seller_response_class,
        'buyer_response_class': buyer_response_class,

        'review_writable': t.request_status >= 2
    }
    if trade_type == 'lease':
        trade_info['start_date'] = t.lease.start_date
        trade_info['due_date'] = t.lease.due_date
        trade_info['duration'] = duration(t.lease.start_date, t.lease.due_date)
    
    return trade_info


@ajax_login_required
@ajax_verify_required
def request_book(request):
    """
    Send a request
    """
    result = {'success': False}
    if request.is_ajax() and request.method == 'POST':
        copy_id = request.POST.get('copy_id').strip()
        content = request.POST.get('message').strip()
        request_type = request.POST.get('request_type')
        book_copy = BookCopy.objects.get(id=copy_id)
        trade = None
        if request_type == 'sale':
            trade = Sale.objects.create(
                buyer=request.user,
                seller=book_copy.owner,
                book_copy=book_copy,
                original_price=book_copy.sale_price,
            )
            state_change_signal.send(
                sender=trade,
                role='buyer',
                action=1,
                previous_state=-1,
            )
        else:
            # start date should be today
            start_date = datetime.datetime.now()
            due_date = datetime.datetime.strptime(request.POST.get('due_date').strip(), '%m/%d/%Y')
            trade = Lease.objects.create(
                buyer=request.user,
                seller=book_copy.owner,
                book_copy=book_copy,
                start_date=start_date,
                due_date=due_date,
                original_price=book_copy.lease_price,
                deposit=book_copy.get_deposit()
            )
            state_change_signal.send(
                sender=trade,
                role='buyer',
                action=1,
                previous_state=-1,
            )
        if content:
            message = trade.messages.create(
                sender = request.user,
                content = content
            )
        
        # set buyer as read, seller defaults to unread
#        trade.read('buyer')
    #    reset_unread_cache(request)
        result = {'success': True}
    json = simplejson.dumps(result)
    return HttpResponse(json, mimetype='application/json')


@login_required
@verify_required
def special_offer(request):
    if request.method == 'POST':
        trade_id = request.POST.get('trade_id').strip()
        price = request.POST.get('special_offer_price').strip()
        trade_message = request.POST.get('so_message').strip()
        free = request.POST.get('free')
        trade = get_object_or_404(Trade, id=trade_id)
        
        # check permissions
        if trade.buyer.id != request.user.id and trade.seller.id != request.user.id:
            flash.warning(request, "You don't have permissions to view this request. Redirected to your requests.")
            return HttpResponseRedirect('/requests/')
        
        if free == 'yes':
            trade.special_offer = 0
        else:
            if trade.get_type() == 'lease':
                trade.special_offer = get_buyer_price(_to_int(price), 'lease')
            else:
                trade.special_offer = get_buyer_price(_to_int(price), 'sale')
        
        trade.save()
        if trade.current_state in [1, 2]:
            trade.move_state('seller', 7)
#            trade.unread('buyer')
#            trade.read('seller')
        
        if trade_message:
            trade.messages.create(
                sender = request.user,
                content = trade_message
            )
#            trade.unread('buyer')
    #    reset_unread_cache(request)
        flash.success(request, "You just made a new special offer")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))


@login_required
@verify_required
def respond_request(request):
    if request.method == 'POST':
        trade_id = request.POST.get('trade_id').strip()        
        t = get_object_or_404(Trade, id=trade_id)
        if t.seller.id == request.user.id:
            role = 'seller'
        elif t.buyer.id == request.user.id:
            role = 'buyer'
        else:
            flash.warning(request, "You don't have permissions to do this operation. Redirected to your requests.")
            return HttpResponseRedirect('/requests/')
        
        post = request.POST.copy()
        action_code = 0
        action_name = ''
        if 'accept' in post:
            action_code = 1
            action_name = 'accepted'
        elif 'reject' in post:
            action_code = 2
            action_name = 'declined'
        elif 'cancel' in post:
            action_code = 3
            action_name = 'canceled'
        elif 'ignore' in post:
            action_code = 4
            action_name = 'ignored'
        else:
            action_code = 0
            action_name = 'no action'
            
        try:
            t.move_state(role, action_code)
        #    if role == 'seller':
        #        t.read('seller')
        #        if action_code != 4:
        #            t.unread('buyer')                    
         #   else:
         #       t.read('buyer')
         #       if action_code != 4:
         #           t.unread('seller')                    
        except Exception:
            pass
        
#        reset_unread_cache(request)
        flash.success(request, "You just %s the request." % action_name)
#        next = request.META.get('HTTP_REFERER','/')
        if role == 'buyer':
            return HttpResponseRedirect('/requests/sent/')
        else:
            return HttpResponseRedirect('/requests/')


@login_required
@verify_required
def write_review(request, trade_id):
    t = get_object_or_404(Trade, id=trade_id)
    if t.buyer.id == request.user.id:
        role = 'buyer'
    elif t.seller.id == request.user.id:
        role = 'seller'
    else:
        flash.warning(request, "You don't have permissions to view this request. Redirected to your requests.")
        return HttpResponseRedirect('/requests/')
    
    if request.method == 'POST':
        review_content = request.POST.get('content')
        message = t.messages.create(
            sender=request.user,
            content='New review is written for you'
        )
        if role == 'seller':
            t.buyer.received_reviews.create(
                sender=t.seller,
                trade=t,
                role=0, # as buyer
                content=review_content
            )
        #    t.unread('buyer')
            
        else:
            t.seller.received_reviews.create(
                sender=t.buyer,
                trade=t,
                role=1, # as seller
                content=review_content
            )
        #    t.unread('seller')
    #    reset_unread_cache(request)
        flash.success(request, "You just post a review")    
        return HttpResponseRedirect('/requests/%s/review/' % trade_id)
    
    else:
        buyer_review = None
        seller_review = None
        for review in t.reviews.all():
            if review.role == 0:
                seller_review = review.content
                seller_review_time = review.update_time
            elif review.role == 1:
                buyer_review = review.content
                buyer_review_time = review.update_time
        
        args = {
            'role': role,
            'buyer_fullname': t.buyer.get_full_name(),
            'buyer_username': t.buyer.profile.username,
            'buyer_review': buyer_review,
            'seller_fullname': t.seller.get_full_name(),
            'seller_username': t.seller.profile.username,
            'seller_review': seller_review,
            'trade_id': trade_id,
            'writable': t.request_status >= 2
        }
        return render_to_response('requests/requests_review.html', args, context_instance=RequestContext(request))

    