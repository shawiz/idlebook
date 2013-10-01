
$(function() {
    $('#deposit').click(function() {
        if ($('#deposit').is(':checked')) {
            $.namespace.total_amount += $.namespace.reserved_balance;
        } else {
            $.namespace.total_amount -= $.namespace.reserved_balance;            
        }
        $('#amount').val(formatMoneyN($.namespace.total_amount));
    });
    
    $('.address-input').focus(function() {
        if ($(this).val() == 'Street Address' || $(this).val() == 'City' || $(this).val() == 'Zip code') {
            $(this).val('');
            $(this).removeClass('tip');
        }
        $('#invalid-input-error').hide();
    });
    
    $('#amount').focus(function() {
        $('#none-withdraw-error').hide();
        $('#over-withdraw-error').hide();
    });
    
    $('#edit-name').click(setName);
    
    $('#order-check-form').submit(function() {
        if ($('#amount').val() == '0') {
            $('#none-withdraw-error').show();   
            return false;
        }
        if (getIntMoney($('#amount').val()) > $.namespace.total_amount) {
            $('#over-withdraw-error').show();
            return false;
        }
        if ($('#amount').val() == '' ||
            $('#address').val() == '' || $('#address').val() == 'Street Address' ||
            $('#city').val() == '' || $('#city').val() == 'City' ||
            $('#zip').val() == '' || $('#zip').val() == 'Zip code' || !$('#zip').val().match(/\d{5}/)) {
            $('#invalid-input-error').show();
            return false;
        }
    });


/*
    // todo: check if a field is touched, and reset to tip if not
    
    $('#address').blur(function() {
        $(this).val('Stree Address');
        $(this).addClass('tip');
    });
    
    $('#city').blur(function() {
        $(this).val('City');
        $(this).addClass('tip');
    });
    
    $('#zipcode').blur(function() {
        $(this).val('ZIP code');
        $(this).addClass('tip');
    });
*/

    $('#order-check-button').click(function() {
        $('#order-check-modal').modal({
            overlayClose: true,
            closeClass: "close",
            position: ["25%",],
            onShow: function() {
                $('#amount').val();
                $.get('/get_balance/', function(data) {
                    if (data.success) {
                        $.namespace.total_amount = 0;
                        $.namespace.regular_balance = data.regular_balance;
                        $.namespace.reserved_balance = data.reserved_balance;
                        $.namespace.total_amount += $.namespace.regular_balance;
                        $('#amount').val(formatMoneyN($.namespace.total_amount));
                        if ($.namespace.total_amount == 0) {
                            $('#order').removeClass('active');
                            $('#none-withdraw-error').show();
                        }
                    }
                });
            },
            onClose: function(dialog) {
                $.modal.close();
            }
        });
    });
});

function setName() {
    $('#realname').hide();
    $('#realname-input').focus();
    $('#realname-input').select();
    $('#realname-input').show();
    $('#edit-name').text('save');
    $('#edit-name').one('click', function() {
        $('#realname').text($('#realname-input').val());
        $('#realname').show();
        $('#realname-input').hide();
        $('#edit-name').text('edit');
        $('#edit-name').click(setName);
    });
}