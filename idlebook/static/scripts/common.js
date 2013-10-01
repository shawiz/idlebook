if (typeof $.namespace === 'undefined') {
    $.namespace = {};
}

$(function() {
    $('.flash').show();
    setTimeout(fadeFlash, 2500);
    
    $('a[rel=tipsy]').tipsy();
    $('span[rel=tipsy]').tipsy();
    
    $('#logout-form').submit(function(event) {
        FB.logout();
    });
    
    $('.facebook-login-button').click(function() {
        FB.login(function(response) {
            if (response.session) {
                window.location = '/facebook/authenticate/' + $(location).attr('search');
            }
        }, {perms: 'user_education_history, publish_stream'});
    });
    
    $('.facebook-signup-button').click(function(e) {
        var mouse_x = e.pageX - 200;
        var mouse_y = e.pageY - 180;
        $('#facebook-signup-modal').modal({
            overlayClose: true,
            closeClass: "close",
            position: [mouse_y, mouse_x],
        });
    });
    
    $('#send-confirmation').click(function() {
        var element = $(this);
        $.post('/send_confirmation/', function(data) {
            if (data.success) {
                element.text('confirmation email sent');
                element.css('color', '#666');                
            }
        });
    });
});

function fadeFlash() {
    $('.flash').fadeOut(1000);
}

/*
utility function that parse the first integer in a given string
*/
function getNumber(s) {
    return parseInt(s.match(/\d+/));
}

function getIntMoney(s) {
    // append a '0' before a number between 0 and 1 without the preceding 0 (.XX)
    if (s.match(/^\.\d{1,2}/)) {
        s = '0' + s;
    }
    return Math.round(parseFloat(s.match(/\d+(\.\d{1,2})?/)) * 100);
}

function formatMoney(num) {
    return '$' + (Math.round(num) / 100);
}

function formatMoneyN(num) {
    return Math.round(num) / 100;
}

function formatDate(date) {
	return (date.getMonth() + 1) + '/' + date.getDate() + '/' + date.getFullYear();
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
            // Only send the token to relative URLs i.e. locally. 
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    },
    complete: function(xhr, settings) {
        var json = $.parseJSON(xhr.responseText);
        if (json.not_authenticated) {
            var next = window.location.pathname + window.location.hash;
            window.location = json.login_url + '?next=' + next;
        } else if (json.not_verified) {
            window.location = json.login_url;
        }
    },
});

$.expr[':'].focus = function(elem) {
    return elem === document.activeElement && (elem.type || elem.href);
};
