$(function() {
    $('.deposit-button').click(function(e) {
        var trade_id = getNumber(this.id);
        $('#deposit-modal').modal({
            overlayClose: true,
            closeClass: "close",
            position: ["25%",],
            onShow: function() {
                $('#deposit_trade_id').val(trade_id);
            }
        });
        return false;
    });
    
    $('.pay-button').click(function(e) {
        var trade_id = getNumber(this.id);
        $('#pay-modal').modal({
            closeClass: "close",
            position: ["25%",],
            onShow: function() {
                $('#pay_trade_id').val(trade_id);
            },
        });
        return false;
    });
    
    $('.action-button').click(function(e) {
        var trade_id = getNumber(this.id);
        $('#action-modal').modal({
            closeClass: "close",
            position: ["25%",],
            onShow: function() {
                $('#action_trade_id').val(trade_id);
            },
        });
        return false;
    });
        
    $('.pickup-button').click(function(e) {
        var trade_id = getNumber(this.id);
        $('#pickup-modal').modal({
            closeClass: "close",
            position: ["25%",],
            onShow: function() {
                $('#pickup_trade_id').val(trade_id);
            },
        });
        return false;
    });
    
});