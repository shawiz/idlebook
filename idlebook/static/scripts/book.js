Date.firstDayOfWeek = 0;
Date.format = 'mm/dd/yyyy';

$(function() {
	$('.rent-button').click(rent);
	$('.buy-button').click(buy);

    // switch off the native auto complete
    $('.date-picker').attr('autocomplete', 'off');
    
    $('#request-sale-form').submit(function(event) {
        var form = $(event.target);
        $.ajax({
            url: form.attr('action'),
            type: form.attr('method'),
            data: {
                message: $('#sale-message').val(),
                copy_id: $('#sale-copy-id').val(),
                request_type: 'sale',
            },
            dataType: 'json',
            success: function(response){
                if (response.success) {
                    $('#request-sale-form').hide();
                    $('.request-sent').show();
                    disableButtons($('#sale-copy-id').val());
                    setTimeout(function() {
                        $.modal.close();
                    }, 3000);
                }
            }
        });
        return false;
    });
    
    $('#request-lease-form').submit(function(event) {
        var form = $(event.target);
        $.ajax({
            url: form.attr('action'),
            type: form.attr('method'),
            data: {
                message: $('#lease-message').val(),
                copy_id: $('#lease-copy-id').val(),
                start_date: $('#lease-start-date').val(),
                due_date: $('#lease-end-date').val(),
                request_type: 'lease',
            },
            dataType: 'json',
            success: function(response){
                if (response.success) {
                    $('#request-lease-form').hide();
                    $('#lease-start-date').val('');
                    $('#lease-end-date').val('');
                    $('.request-sent').show();
                    disableButtons($('#lease-copy-id').val());
                    setTimeout(function() {
                        $.modal.close();
                    }, 3000);
                }
            }
        });
        return false;
    });
});

function disableButtons(copy_id) {
    var buy_button = $('#sale-copy-' + copy_id);
    buy_button.removeClass('buy-button');
    buy_button.addClass('disabled');
    buy_button.attr('title', 'Book requested');
    buy_button.parent().prev().text('Requested');
    var rent_button = $('#lease-copy-' + copy_id);
    rent_button.removeClass('rent-button');
    rent_button.addClass('disabled');
    rent_button.attr('title', 'Book requested');
}

function buy() {
    var copy_id = getNumber(this.id);
    var title = $(this).attr('title');
    var price = $(this).text();
    $('#sale-modal').modal({
        overlayClose: true,
        closeClass: "close",
        position: ["25%",],
        onShow: function() {
            $('#sale-title').text(title);
            $('#request-sale-price').text(price);
            $('#sale-copy-id').val(copy_id);
        },
        onClose: function(dialog) {
            dialog.container.fadeOut('fast', function () {
                $.modal.close();
            });
        }
    });
    return false;
}

function rent() {
    var copy_id = getNumber(this.id);
    var title = $(this).attr('title');
    var price = $(this).text();
    $('#lease-modal').modal({
        overlayClose: true,
        closeClass: "close",
        position: ["25%",],
        onShow: function() {
            $.get('/load_copy/', {copy_id:copy_id}, function(data) {
                if (data.success) {
                    $('#request-deposit').text(formatMoney(data.deposit));
                    $('#request-lease-total').text(formatMoney(parseInt(data.deposit) + parseInt(data.lease_price)))
                    if (data.notes) {
                        $('#lease-rules').html('<span class="request-price-notes">also:</span> <span class="lease-rules">' + data.notes + '</span>');
                    }
                }
            });
            $('.date-picker').datePicker({clickInput:true}).val(new Date().asString()).trigger('change');
        	$('#lease-start-date').dpSetDisabled(true);
            
            $('#lease-title').text(title);
            $('#request-lease-price').text(price);
            $('#lease-copy-id').val(copy_id);
        },
        onClose: function(dialog) {
            $('#lease-rules').text('');
            dialog.container.fadeOut('fast', function() {
                $.modal.close();  
            });
        }
    });
    return false;
}

function saveOwnWish(button, copy_id) {
    if (copy_id != null && copy_id != -1) {
        openModal(copy_id);
    } else {
        window.location.reload();
    }
}

function saveCopyEdit() {
    window.location.reload();
}