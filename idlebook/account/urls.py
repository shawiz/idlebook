from django.conf.urls.defaults import *

urlpatterns = patterns('idlebook.account.views',

    # debug
    url(r'^debug_login/$', 'debug_login', name='debug_login'),  # login for debug site
#    url(r'^debug_signup/$', 'debug_signup', name='debug_signup'),  # sign up for debug site

    # account operations
    url(r'^login/$', 'login', name='login'),
    url(r'^signup/$', 'login', name='signup'),  # now sign up is the same as login
    url(r'^logout/$', 'logout', name='logout'),
    url(r'^send_confirmation/$', 'send_confirmation', name='send_confirmation'),
    url(r'^confirm_email/(?P<confirmation_key>\w+)/$', 'confirm_email', name='confirm_email'),
    url(r'^verify_email/$', 'verify_email', name='verify_email'),    
    
    # profiles
    url(r'^profile/$', 'profile', name='profile'),
    url(r'^person/(?P<username>\w+)/$', 'person', name='person'),
    url(r'^person/(?P<username>\w+)/(?P<list>(wishlist|reviews))/$', 'person_list', name='person_list'),
#    url(r'^person/(?P<username>\w+)/(?P<list>(listings|wishlist))/public/$', 'public_list', name='public_list'),
    
    # settings
    url(r'^settings/$', 'settings', name='settings'),
    url(r'^settings/(?P<tab>(account|profile|network|notifications))/$', 'settings_tab', name='settings_tab'),
#    url(r'^settings/photo_edit/$', 'settings_photo_edit'),
    url(r'^check_username/$', 'check_username', name='check_username'),
    url(r'^set_username/$', 'set_username', name='set_username'),
    url(r'^add_dept/$', 'add_department', name='add_department'),
    url(r'^remove_dept/$', 'remove_department', name='remove_department'),
    
    # wallet
    url(r'^wallet/$', 'wallet', name='wallet'),
    url(r'^get_balance/$', 'get_balance', name='get_balance'),
    url(r'^order_check/$', 'order_check', name='order_check'),
    
    # requsts
    url(r'^request_book/$', 'request_book', name='request_book'),
    url(r'^requests/$', 'requests', name='requests'),
    url(r'^requests/past/$', 'requests_past', name='requests_past'),
    url(r'^requests/sent/$', 'requests_sent', name='requests_sent'),
    url(r'^requests/sent/past/$', 'requests_sent_past', name='requests_sent_past'),
    url(r'^requests/(?P<trade_id>\d+)/$', 'view_request', name='view_request'),
    url(r'^requests/(?P<trade_id>\d+)/review/$', 'write_review', name='write_review'),
    url(r'^respond/$', 'respond_request', name='respond_request'),
    url(r'^special_offer/$', 'special_offer', name='special_offer'),
    
    # notification
    url(r'^notification/$', 'notification', name='notification'),
    
#    url(r'^offers/$', 'offers'),
#    url(r'^offers/sent/$', 'offers_sent'),
#    url(r'^inbox/$', 'inbox', name='inbox'),
#    url(r'^mail/(?P<mail_id>\d+)/$', 'mail', name='mail'),
    
)
