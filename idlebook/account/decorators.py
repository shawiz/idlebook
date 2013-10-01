from functools import wraps

#from django import http
from django.utils import simplejson
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import available_attrs


def verify_required(view_func):
    """Handle non-verfied users."""
    
    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated():
            if request.user.profile.email_verified:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('/verify_email/')
        else:
            return view_func(request, *args, **kwargs)
#            return login_required(view_func)(request, *args, **kwargs)
    return _wrapped_view


def ajax_login_required(view_func):
    """Handle non-authenticated users differently if it is an AJAX request."""

    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view(request, *args, **kwargs):
        if request.is_ajax():
            if request.user.is_authenticated():
                return view_func(request, *args, **kwargs)
            else:
                content = simplejson.dumps({'not_authenticated': True, 'login_url': settings.LOGIN_URL})
                return HttpResponse(content, content_type='application/json')
        else:
            return login_required(view_func)(request, *args, **kwargs)
    return _wrapped_view


def ajax_verify_required(view_func):
    """Handle non-verfied users differently if it is an AJAX request."""
    
    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view(request, *args, **kwargs):
        if request.is_ajax():
            if request.user.profile.email_verified:
                return view_func(request, *args, **kwargs)
            else:
                content = simplejson.dumps({'not_verified': True, 'login_url': '/verify_email/'})
                return HttpResponse(content, content_type='application/json')    
        else:
            return verify_required(view_func)(request, *args, **kwargs)
    return _wrapped_view

