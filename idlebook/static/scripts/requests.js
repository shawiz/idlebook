$(function() {
    $('.action:contains("-")').css('display', 'none');
    
    $('.copy-edit-button').click(function() {
        if ($(this).hasClass('lease')) {
            $('.sale-label').parent().hide();
            $('#lease-price').focus();
        } else if ($(this).hasClass('sale')) {
            $('.lease-label').parent().hide();
            $('#sale-price').focus();
        }
        if (this.id.indexOf("accept") != -1) {
            if ($(this).hasClass('wait')) {
                $('#modal-info').text("You need to wait for the buyer to confirm your price. You can also set a different price");                
            } else {
                $('#modal-info').text("You haven't set a price for your book. Please set a price first.");                
            }
        }
        return false;
    });
    
    /* Now you must confirm before you respond to a request */
    $("form input[type=submit]").click(function() {
        $("input[type=submit]", $(this).parents("form")).removeAttr("clicked");
        $(this).attr("clicked", "true");
    });
    
    $('form.respond-form').submit(function(event) {
        var action = $("input[type=submit][clicked=true]").attr('name');
        var answer = confirm("Are you sure to " + action + " this request?\n\nYou CAN'T undo this action.");
    	if (answer) {
            return true;
    	} else {
    	    event.preventDefault();
            return false;
    	}
    });
    
    $('.special-offer-button').click(function() {
        var button = $(this);
        var trade_id = getNumber(this.id);
        $('#special-offer-price').attr('autocomplete', 'off');        
        $('#special-offer-modal').modal({
            overlayClose: true,
            closeClass: "close",
            position: ["25%",],
            onShow: function() {
                $('#trade-id').val(trade_id);
                $('#current-price').text(button.prev().text());
                if ($(this).hasClass('lease')) {
                    $('#type').text('Lease');
                } else {
                    $('#type').text('Sale');
                }
            },
            onClose: function(dialog) {
                dialog.container.fadeOut('fast', function () {
                    $.modal.close();
                });
            }
        });
    });
    
    $('#special-offer-price').keyup(function(e) {
        if (e.which >= 37 && e.which <= 57 || e.which == 190) {
            var price = getNumber($(this).val()) * 100;
            $.get('/compute_price/',
                {
                    price: price,
                    type: $('#type').val().toLowerCase()
                },
                function(data) {
                    if (data.success) {
                        $('#actual-special-offer-price').text(formatMoney(data.price));
                    }
                }
            );
        }
    });
    
    $('#special-offer-form').submit(function(e) {
        var free = $('input[name=free]:checked', '#special-offer-form').val();
        var price = $.trim($('#special-offer-price').val());
        if (free === undefined) {
            $('#special-offer-error').text("Please set your special price for buyer");
            return false;
        } else if (free == 'no' && !price.match(/^\d+(\.\d{1,2})?$/)) {
            $('#special-offer-error').text("please enter a valid price");
            return false;
        }
        $('#special-offer-error').text('');
    });
    
});

function saveCopyEdit() {
    window.location.reload();
}
