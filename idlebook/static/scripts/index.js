$.namespace.saved_count = 0;
$.namespace.how_on = false;
var TIP_TEXT = 'Enter book title or course name (i.e. math124)';

$(function() {
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
    
    $('.own-button').live('click', function() {
        var button = $(this);
    	var book_id = getNumber(this.id);
        $.post('/own_book/', { book_id: book_id }, function(data) {
            if (data.success) {
                button.addClass('used');
                $.namespace.saved_count++;
                if ($.namespace.saved_count >= 2) {
                    $('#book-info-notice').css('visibility', 'visible');
                };
            }
        });
    });
    
    $('.wish-button').live('click', function() {
        var button = $(this);
    	var book_id = getNumber(this.id);
        $.post('/wish_book/', { book_id: book_id }, function(data) {
            if (data.success) {
                button.addClass('used');
                $.namespace.saved_count++;
                if ($.namespace.saved_count >= 2) {
                    $('#book-info-notice').css('visibility', 'visible');
                };
            }
        });
    });
    
    $('.remove').live('click', function() {
        $(this).parent().remove();
    });
    
});

function onItemSelect(item) {
    $('#book-list').append('<li id="book-' + item.data.id + '"><span class="remove" id="remove-book-' + item.data.id + '">×</span><a target="_blank" href="/book/' + item.data.id + '/">' + item.value + '</a><p><button class="own-button" id="own-' + item.data.id + '">I own it</button><button class="wish-button" id="wish-' + item.data.id + '">Add to wish list</button></p></li>');
}
