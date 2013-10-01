from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.contrib import admin

from idlebook.account import *
from idlebook.book import *
from idlebook.network import *
from idlebook.accounting import *

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
#   url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    
    # for development static solution. finally > <
    (r'^static/(.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    (r'^media/(.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    
    url(r'^$', 'idlebook.account.views.index'),
    url(r'^', include('idlebook.account.urls')),
    url(r'^', include('idlebook.book.urls')),
    url(r'^', include('idlebook.facebook.urls')),
    url(r'^manage/', include('idlebook.accounting.urls')),
    url(r'^notification/', include('notification.urls')),
)
urlpatterns += staticfiles_urlpatterns()

handler500 = 'account.views.server_error'
