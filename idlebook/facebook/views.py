import urllib2
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.utils import simplejson

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import auth
from idlebook.account.forms import FacebookSignupForm
from idlebook.book.models import Book, BookCopy, Wishlist
from models import *
from django.contrib import auth

def signup(request):
    next = request.REQUEST.get('next', '/')
    if not request.facebook:
        return HttpResponseRedirect(next)
    errors = ""

    me = request.facebook.graph.get_object('me', fields='name, first_name, last_name, picture')
    friends = request.facebook.graph.get_connections('me', 'friends')
    
    facebook_data = {}
    facebook_data['name'] = me['name'] if me.get('name') else ''
    facebook_data['first_name'] = me['first_name'] if me.get('first_name') else ''
    facebook_data['last_name'] = me['last_name'] if me.get('last_name') else ''
    facebook_data['num_of_friends'] = len(friends.get('data'))
    facebook_data['thumb_url'] = me['picture'] if me.get('picture') else ''
    
    if request.method == 'POST':
        form = FacebookSignupForm(request.POST)
        if form.is_valid():
            user = form.save(facebook_data)
            # save facebook photos
            save_photos(user, request.facebook)
            facebook_user = FacebookUser.objects.create(
                user=user,
                facebook_id=request.facebook.uid,
                access_token=request.facebook.user['access_token']
            )
            facebook_user.save()
            user = auth.authenticate(fb_uid=request.facebook.uid, fb_graphtoken=request.facebook.user['access_token'])
            auth.login(request, user)
            save_temp_books(request, user)
            return HttpResponseRedirect('/profile/')
        else:
            errors = form.errors
    
    form = FacebookSignupForm()
    return render_to_response('signup_facebook.html', {'form': form, 'facebook_data': facebook_data, 'errors': errors}, context_instance=RequestContext(request))


def save_photos(user, facebook):
    # save image files
    thumb_graph = facebook.graph.get_object('me', fields='picture')
    photo_graph = facebook.graph.get_object('me', fields='picture', type='large')
    
    facebook_thumb_url = thumb_graph['picture'] if thumb_graph.get('picture') else ''
    facebook_photo_url = photo_graph['picture'] if photo_graph.get('picture') else ''
    
    photo_link = 'up' + str(user.id) + '.jpg'
    photo_temp = NamedTemporaryFile(delete=True)
    photo_temp.write(urllib2.urlopen(facebook_photo_url).read())
    photo_temp.flush()
    user.profile.photo.save(photo_link, File(photo_temp), save=True)
    
    thumb_link = 'ut' + str(user.id) + '.jpg'
    thumb_temp = NamedTemporaryFile(delete=True)
    thumb_temp.write(urllib2.urlopen(facebook_thumb_url).read())
    thumb_temp.flush()
    user.profile.thumb.save(thumb_link, File(thumb_temp), save=True)


def save_temp_books(request, user):
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


def authenticate(request):
    prev = request.META.get('HTTP_REFERER','/')
    next = request.REQUEST.get('next', prev)
    # if facebook is in
    if request.facebook:
        uid = request.facebook.uid
        access_token = request.facebook.user['access_token']
        # if user has been authenticated
        if request.user.is_authenticated():
            user = auth.authenticate(fb_uid=uid, fb_graphtoken=access_token)
            # if user is logged in
            if user:
                #save_photos(user, request.facebook)
                return HttpResponseRedirect(next)
            else:
                save_photos(request.user, request.facebook)
                facebook_user = FacebookUser.objects.create(
                    user=request.user,
                    facebook_id=request.facebook.uid,
                    access_token=request.facebook.user['access_token']
                )
                facebook_user.save()
                return HttpResponseRedirect(next)
                
        elif request.user.is_anonymous():
            user = auth.authenticate(fb_uid=uid, fb_graphtoken=access_token)
            if user:
                auth.login(request, user)
                save_temp_books(request, user)
                return HttpResponseRedirect(next)
            else:
                return HttpResponseRedirect('/facebook/signup_inviter/?next=%s' % next)    
    else:
        return HttpResponseRedirect(next)


def inviter(request):
    next = request.REQUEST.get('next', '/')
    if not request.facebook:
        return HttpResponseRedirect(next)
    errors = ""

    me = request.facebook.graph.get_object('me', fields='name, first_name, last_name, picture')
    friends = request.facebook.graph.get_connections('me', 'friends')
    
    facebook_data = {}
    facebook_data['name'] = me['name'] if me.get('name') else ''
    facebook_data['first_name'] = me['first_name'] if me.get('first_name') else ''
    facebook_data['last_name'] = me['last_name'] if me.get('last_name') else ''
    facebook_data['num_of_friends'] = len(friends.get('data'))
    facebook_data['thumb_url'] = me['picture'] if me.get('picture') else ''
    
#    friends_data = friends.get('data')
#    friends = [[friend['name'], friend['id']] for friend in friends_data]
#    friends = simplejson.dumps(friends)
    
    if request.method == 'POST':
        # test
        inviter_info = request.POST.copy()
        form = FacebookSignupForm(request.POST)
        if form.is_valid():
            user = form.save(facebook_data)
            # save facebook photos
            save_photos(user, request.facebook)
            facebook_user = FacebookUser.objects.create(
                user=user,
                facebook_id=request.facebook.uid,
                access_token=request.facebook.user['access_token'],
            )
            # save inviter info
        #    inviter_id = inviter_info.get('inviter_id', '')
            inviter_name = inviter_info.get('inviter_name', '')
        #    if inviter_id:
        #        facebook_user.inviter_id = inviter_id
            if inviter_name:
                facebook_user.inviter_name = inviter_name
            facebook_user.save()
            # auth and save temp books
            user = auth.authenticate(fb_uid=request.facebook.uid, fb_graphtoken=request.facebook.user['access_token'])
            auth.login(request, user)
            save_temp_books(request, user)
            return HttpResponseRedirect('/profile/')
        else:
            errors = form.errors
    
    form = FacebookSignupForm()
    return render_to_response('signup_facebook_inviter.html', {'form': form, 'facebook_data': facebook_data, 'errors': errors, 'friends':friends}, context_instance=RequestContext(request))
