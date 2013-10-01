$(function() {
    $('.copy-edit-button').click(function() {
        var copy_id = getNumber(this.id);
        openModal(copy_id);
    });
    
    $('#lease-price').attr('autocomplete', 'off');
    $('#sale-price').attr('autocomplete', 'off');
    
    $('#show-notes').click(function() {
        $('#modal-notes').toggle();
    })
    
    $('#lease-price').keyup(function(e) {
        if (e.which >= 37 && e.which <= 57 || e.which == 190) {
            var price = getIntMoney($(this).val());
            $.get('/compute_price/', { price: price, type: 'lease'}, function(data) {
                if (data.success) {
                    $('#actual-lease-price').text(formatMoney(data.price));
                //    $('#lease-price-help').show();
                }
            });
        }
    });
    
    $('#sale-price').keyup(function(e) {
        if (e.which >= 37 && e.which <= 57) {
            var price = getIntMoney($(this).val());
            $.get('/compute_price/', { price: price, type: 'sale'}, function(data) {
                if (data.success) {
                    $('#actual-sale-price').text(formatMoney(data.price));
                //    $('#sale-price-help').show();
                }
            });
        }
    });
    
    $('#copy-edit-form').submit(function(e) {
        $.post('/edit_copy/', $(this).serialize(), function(data) {
            if (data.success) {
                saveCopyEdit();
            }
        });
        return false;
    });
});

function openModal(copy_id) {
    $('#copy-edit-modal').modal({
        overlayClose: true,
        closeClass: "close",
        position: ["25%",],
        onShow: function() {
            $('#copy_id').val(copy_id);
            $('#lease-price').val('');
            $('#sale-price').val('');
            $('#modal-notes').val('');
            $.get('/load_copy/',
                { copy_id: copy_id },
                function(data) {
                    if (data.success) {
                        if (data.list_price != null) {
                            $('#list-price').text(formatMoney(data.list_price));
                            $('.modal-list-price').show();
                            $('#sug-lease-low').text(formatMoney(data.lease_range[0]));
                            $('#sug-lease-high').text(formatMoney(data.lease_range[1]));
                            $('#sug-sale-low').text(formatMoney(data.sale_range[0]));
                            $('#sug-sale-high').text(formatMoney(data.sale_range[1]));
                            $('.modal-sug-sale').show();
                            $('.modal-sug-lease').show();
                        }
                        if (data.condition) {
                            $('#modal-condition').val(data.condition);
                        }
                        if (data.notes) {
                            $('#show-notes').attr('checked', 'checked');
                            $('#modal-notes').show();
                            $('#modal-notes').val(data.notes);
                        } else if ($('#show-notes').attr('checked')) {
                            $('#show-notes').removeAttr('checked');
                        }
                        if (data.lease_price) {
                            $('#actual-lease-price').text(formatMoney(data.lease_price));
                        //    $('#lease-price-help').show();
                        }
                        if (data.sale_price) {
                            $('#actual-sale-price').text(formatMoney(data.sale_price));
                        //    $('#sale-price-help').show();
                        }
                    }
                });
        },
        onClose: function(dialog) {
            dialog.container.fadeOut('fast', function () {
                $.modal.close();
            });
        }
    });
    
}