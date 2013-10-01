from django.conf.urls.defaults import *

urlpatterns = patterns('idlebook.facebook.views',
    url(r'^facebook/signup/$', 'signup', name='signup'),
    url(r'^facebook/authenticate/$', 'authenticate', name='authenticate'),
    url(r'^facebook/signup_inviter/$', 'inviter', name='inviter')
)