var TIP_TEXT = 'Add a book to your wishlist (enter book title or course name)';

$(function() {
    $('.remove-wish-button').click(function() {
        var book_id = getNumber(this.id);
        var answer = confirm("Are you sure to remove this book from your wishlist?");
    	if (answer) {
    	    $.post('/remove_wish_book/', {book_id:book_id}, function(data) {
    	        if (data.success) {
    	            window.location.reload();
    	        }
    	    });
    	}
    });
});

function onItemSelect(item) {
    $.post('/wish_book/', { book_id: item.data.id }, function(data) {
        if (data.success) {
            window.location.reload();
        }
    });
}
