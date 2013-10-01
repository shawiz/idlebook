$(function() {
    $('#inviter-name').autocomplete({
        data: friends,
        minChars: 2,
        delay: 50,
        maxItemsToShow: 5,
        selectOnly: true,
        showResult: function(value, data) {
            return '<div class="result-row" id="' + data.id + '">' + value + '</div>';
        },
        onItemSelect: function(item) {
            $('#inviter-id').val(item.data);
        }
    });
});