if (typeof $.namespace === 'undefined') {
    $.namespace = {};
}

// 0: init, 1: focus, 2: typed
$.namespace.search_tip_status = 0;

$(function() {
    $('#search-box').autocomplete({
        url: '/lookup/book/',
        minChars: 3,
        delay: 50,
        remoteDataType: 'json',
        maxItemsToShow: 5,
        selectFirst: true,
        selectOnly: true,
        showResult: function(value, data) {
            return '<div class="result-row" id="' + data.id + '">' + value + '</div>';
        },
        onItemSelect: function(item) {
            onItemSelect(item);
            $('#search-box').focus();
        },
        displayValue: function(value, data) {
            return value.replace(/ <span class="x-8q [\w ]+">.+<\/span>$/, "");
        }
    });
    
    var timer;
    
    $('#search-box').click(function() {
        setSearchTipStatus(1);
    });
    
    $('#search-box').focus(function() {
        clearTimeout(timer);
        setSearchTipStatus(1);
    });
    
    $('#search-box').blur(function() {
        timer = setTimeout(resetSearchTip, 10);
    });
    
    $('#search-box').keypress(function(event) {
        if (event.which != 13 && $.namespace.search_tip_status != 2) {
            setSearchTipStatus(2);
        }
    });
    
    /*
    $('#search-box').keydown(function() {
        var term = $('#search-box').val();
    //    $(".ac-results").highlight(term, 1);
    });
    */
});

function resetSearchTip() {
    setSearchTipStatus(0);
}

function setSearchTipStatus(status) {
    if ($.namespace.search_tip_status != 0 && status == 0) {
        $('#search-box').removeClass('tip-half');
        $('#search-box').removeClass('tip-off');
        $('#search-box').val(TIP_TEXT);
        $.namespace.search_tip_status = 0;
    } else if (status == 1) {
        $('#search-box').removeClass('tip-off');
        $('#search-box').addClass('tip-half');
        $('#search-box').val(TIP_TEXT);
        $('#search-box').selectRange(0, 0);
        $.namespace.search_tip_status = 1;
    } else if ($.namespace.search_tip_status != 2 && status == 2) {
        $('#search-box').removeClass('tip-half');
        $('#search-box').addClass('tip-off');
        $('#search-box').val('');
        $.namespace.search_tip_status = 2;
    }
}

$.fn.selectRange = function(start, end) {
    return this.each(function() {
        if (this.setSelectionRange) {
            this.focus();
            this.setSelectionRange(start, end);
        } else if (this.createTextRange) {
            var range = this.createTextRange();
            range.collapse(true);
            range.moveEnd('character', end);
            range.moveStart('character', start);
            range.select();
        }
    });
};
