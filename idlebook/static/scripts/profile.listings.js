var TIP_TEXT = 'Add a book to your listings (enter book title or course name)';

$(function() {
    $('.remove-button').click(function() {
        var book_id = getNumber(this.id);
        var answer = confirm("Are you sure to remove this book from your listings?");
    	if (answer) {
    	    $.post('/remove_book/', {book_id:book_id}, function(data) {
    	        if (data.success) {
    	            window.location.reload();
    	        }
    	    });
    	}
    });
});

function onItemSelect(item) {
    $.post('/own_book/', { book_id: item.data.id }, function(data) {
        if (data.success) {
            window.location.reload();
        }
    });
}

function saveCopyEdit() {
    window.location.reload();
//    $.modal.close();
}