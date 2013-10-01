$(function() {
    $('#tab-buyer').click(function() {
        $('.reviews-seller').hide();
        $('.reviews-buyer').show();
        $(this).addClass('active');
        $('#tab-seller').removeClass('active');
    });
    $('#tab-seller').click(function() {
        $('.reviews-buyer').hide();
        $('.reviews-seller').show();
        $(this).addClass('active');
        $('#tab-buyer').removeClass('active');
    });
});