$(function() {
	$('.wish-button').click(wish);
	$('.remove-wish-button').click(unwish);
	$('.own-button').click(own);
	$('.remove-own-button').click(unown);
});

function wish() {
    if ($(this).hasClass('active')) {
        var button = $(this);
    	var book_id = getNumber(this.id);
        $.post('/wish_book/', { book_id: book_id }, function(data) {
            if (data.success) {
                saveOwnWish(button, -1);
            }
        });
    }
}

function own() {
    if ($(this).hasClass('active')) {
        var button = $(this);
        var book_id = getNumber(this.id);
        $.post('/own_book/', { book_id: book_id }, function(data) {
    		if (data.success) {
                saveOwnWish(button, data.copy_id);
            }
    	});
	}
}

function unwish() {
    var button = $(this);
    var book_id = getNumber(this.id);
    $.post('/remove_wish_book/', { book_id: book_id }, function(data) {
	    if (data.success) {
            saveOwnWish(button, -1);
        }
	});
}

function unown() {
    var button = $(this);
    var book_id = getNumber(this.id);
    $.post('/remove_book/', { book_id: book_id }, function(data) {
		if (data.success) {
            saveOwnWish(button, -1);
        }
	});
}
