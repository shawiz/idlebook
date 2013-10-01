$.namespace.own_price = 0;
$.namespace.own_rent = 0;
$.namespace.wish_price = 0;
$.namespace.wish_rent = 0;
$.namespace.own_search = true;
$.namespace.how_on = false;

var BUYBACK_MULTIPLYER = 0.55
var RENTAL_MULTIPLYER = 0.3
var TIP_TEXT = 'Enter book title or course name (i.e. math124)';

$(function() {
    $('#search-box').tipsy({trigger:'manual', gravity:'s', offset: -12, className: 'search-tip', opacity: 1});
    $('#search-box').hover(function() {
        if ($.namespace.search_tip_status == 0) {
            $(this).tipsy('show');
        }
    }, function() {
        $(this).tipsy('hide');
    });
    $('#search-box').focus(function() {
        $(this).tipsy('hide');
    });
    
    $('#own-selector').click(function(event) {
        $('#search-box').focus();
        $(this).addClass('active');
        $('#wish-selector').removeClass('active');
        $.namespace.own_search = true;
    });
    
    $('#wish-selector').click(function() {
        $('#search-box').focus();
        $(this).addClass('active');
        $('#own-selector').removeClass('active');
        $.namespace.own_search = false;
    });
    
    $('.how').click(function() {
        if ($.namespace.how_on) {
            $('#how-nav').css('color', '#444444');
        } else {
            $('#how-nav').css('color', '#1a8f5b');
        }
        $('#howitworks').slideToggle();
        $.namespace.how_on = !$.namespace.how_on;
    });
    
    /*
    if (location.hash && location.hash == '#howitworks') {
        $('#howitworks').show();
        $.namespace.how_on = true;
    }
    */
    
    $('.how-tab').click(function() {
        if (!$(this).hasClass('active')) {
            $(this).addClass('active');
            $(this).siblings().removeClass('active');
            var hidden_graphs = $('#graphs').find('.hidden');
            hidden_graphs.siblings().addClass('hidden');
            hidden_graphs.removeClass('hidden');
        }
    });
    
    $('.remove-book').live('click', function() {
        var book_id = getNumber(this.id);
        var block = $(this).parent();
        $.post('/remove_book/', {book_id:book_id}, function(data) {
            if (data.success) {
                block.remove();                
            }
        });
    });
    
    $('.remove-wish-book').live('click', function() {
        var book_id = getNumber(this.id);
        var block = $(this).parent();
        $.post('/remove_wish_book/', {book_id:book_id}, function(data) {
            if (data.success) {
                block.remove();                
            }
        });
    });
    
});

function onItemSelect(item) {
    if ($.namespace.own_search) {
        $('#own-list ul').append('<li id="book-' + item.data.id + '"><span class="remove-book remove" id="remove-book-' + item.data.id + '">×</span><a target=_blank href="/book/' + item.data.id + '/">' + item.value + '</a></li>');
        
        $.namespace.own_price += item.data.price * BUYBACK_MULTIPLYER;
        $.namespace.own_rent += item.data.price * RENTAL_MULTIPLYER;
        
        $('#own-price').text(formatMoneyN($.namespace.own_price));
        $('#own-rent').text(formatMoneyN($.namespace.own_rent));
        $('#own-price-count').fadeIn('fast');
        $('#book-info-notice').fadeIn('slow');
        
        $.post('/own_book/', { book_id: item.data.id });
    } else {
        $('#wish-list ul').append('<li><span class="remove-book remove" id="remove-book-' + item.data.id + '">×</span><a target=_blank href="/book/' + item.data.id + '/">' + item.value + '</li>');
        
        $.namespace.wish_price += item.data.price;
        $.namespace.wish_rent += item.data.price * RENTAL_MULTIPLYER;
        $('#wish-price').text(formatMoneyN($.namespace.wish_price));
        $('#wish-rent').text(formatMoneyN($.namespace.wish_rent));
        $('#wish-price-count').fadeIn('fast');
        $('#book-info-notice').fadeIn('slow');
        
        $.post('/wish_book/', { book_id: item.data.id });
    }
}
