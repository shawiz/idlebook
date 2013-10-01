$.namespace.nav_search_state = 0;

$(function() {
    /*
    // get all dept codes and turn it into array
    $.get('/static/texts/deptcodes.txt', function(data) {
        $.namespace.depts = data.split('\n');
    });
    */
    
    $('#nav-search-box').tipsy({trigger:'manual', gravity: 'nw', offset: 4, className: 'nav-search-tip', opacity: 1});
    
    $('#nav-search-box').hover(function() {
        if (!$('#nav-search-box').is(':focus')) {
            $(this).tipsy('show');
        }
    }, function() {
        $(this).tipsy('hide');
    });
    
    $('#nav-search-box').focus(function() {
        $(this).tipsy('hide');
        if ($.namespace.nav_search_state == 0) {
            $(this).val('');
            $(this).addClass('terms');
        }
        $.namespace.nav_search_state = 1;
    });
    
    $('#nav-search-box').blur(function() {
        $(this).val('Find a book...');
        $(this).removeClass('terms');
        $.namespace.nav_search_state = 0;
    });
    
    $('#nav-search-box').autocomplete({
        url: '/lookup/book/',
        minChars: 3,
        delay: 50,
        remoteDataType: 'json',
        maxItemsToShow: 5,
        selectOnly: true,
        resultWidth: 520,
        additionalResult: function(query) {
            return '<div class="result-row search-all">Search all: ' + query + '</div>';
        },
        showResult: function(value, data) {
            if ($.namespace.nav_search_state == 2) {
                return '<div class="result-row" id="book-' + data.id + '">' + value + '</div>';                
            } else {
                return '';
            }
        },
        onItemSelect: function(item) {
            if (item.data.id == -1) {
                window.location = '/search/?q=' + item.data.value;                
            } else {
                window.location = '/book/' + item.data.id;
            }
        },
        displayValue: function(value, data) {
            return value.replace(/ <span class="x-8q [\w ]+">.+<\/span>$/, "");
        }
        
    });
    
    $('#nav-search-box').keypress(function(event) {
        var code = event.keyCode ? event.keyCode : event.which;
        if (code != 13) {
            $(this).tipsy('hide');
            $.namespace.nav_search_state = 2;
        } else if (!$('.ac-results li').hasClass('ac-select')) {
            // if nothing selected, search the form
            $('#nav-search-form').submit();
        }
    });

    /*
    $('#nav-search-box').keyup(function() {
        var term = $('#nav-search-box').val();
        $(".ac-results").highlight(term);
    });
    */
    
    
    /* match a course name if start typing a dept code */
    /*
    $('#nav-search-box').keyup(function(event) {
        var code = $(this).val().match(/^[a-zA-Z&]{2,6}$/);
        if (code != null) {
            code = codes[code.length - 1].toUpperCase();
            if ($.namespace.depts.binarySearch(code) != null) {
                // do something here
                acSetParam('course');
            }
        }
    });
    */
    
    /*
    // match a person by entering @. need more work for search state and tipsy.
    $('#nav-search-box').keyup(function(event) {
        var name = $(this).val().match(/^@[A-Za-z\s\.\-]*$/);
        if (name != null) {
            name = name[0];
            $(this).attr('title', 'Find a person');
            if ($.namespace.nav_search_state == 2) {
                $(this).tipsy('show');
                $.namespace.nav_search_state = 3;
            }
            acSetParam('person');
        }
    });
    */
});

/*
// set extra params to the backend through autocompleter
function acSetParam(query_type) {
    var ac = $("#nav-search-box").data("autocompleter");
    ac.cacheFlush();
    ac.setExtraParam('type', query_type);
}
*/

/*
constraint binary search
Array are sorted and in all caps
find is in all caps
*/
/*
Array.prototype.binarySearch = function(find) {
    var low = 0, high = this.length - 1, i;
    while (low <= high) {
        i = Math.floor((low + high) / 2);
        if (this[i] < find) { low = i + 1; continue; };
        if (this[i] > find) { high = i - 1; continue; };
        return i;
    }
    return null;
};
*/


/*
jQuery.fn.extend({
    highlight: function(term) {
        var value = $(this);
//        value.find(".result-row").html(value.find(".result-row").html().replace(RegExp(term, "gi"), "<em>" + term + "</em>"));
    }
});
*/