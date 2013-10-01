$(function() {    
    $('#set-username').submit(function(event) {
        event.preventDefault();
        var username = $('#username').val();
        $.post('/check_username/', {username:username}, function(data) {
            if (data.success) {
                if (confirm('Are you sure to set your username as "' + username + '"?')) { 
                    $.post('/set_username/', {username:username}, function(data) {
                        if (data.success) {
                            window.location.reload();
                        } else {
                            $('#username-exist').text(data.error);
                            $('#username-exist').show();                            
                        }
                    });
                }
            } else {    
                $('#username-exist').text(data.error);
                $('#username-exist').show();
            }
        });
    });
    
    $('#username').keyup(function(event) {
        if (event.which != 13) {
            $('#username-exist').hide();
        }
        var username = $.trim($(this).val());
        $('#url-username').text(username);
    });
    
    $('#dept-add').click(function() {
        $('.account-dept-add').hide();
        $('.account-dept-input').show();
        $('#dept-input').focus();
        $('#dept-input').blur(function() {
            $('.account-dept-input').hide();
            $('.account-dept-add').show();
        });
    });
    $('.remove-dept').live('click', function(event) {
        event.preventDefault();
        var dept_id = getNumber(this.id);
        var dept_row = $(this).parent();
        $.post('/remove_dept/', {dept_id: dept_id}, function(data) {
            if (data.success) {
                dept_row.remove();
            }
        });
    });
    
    $('#dept-input').autocomplete({
        url: '/lookup/department/',
        minChars: 1,
        delay: 50,
        remoteDataType: 'json',
        maxItemsToShow: 5,
        resultWidth: 320,
        showResult: function(value, data) {
            return '<div class="result-row" id="book-' + data.id + '">' + value + '</div>';
        },
        onItemSelect: function(item) {
            $.post('/add_dept/', {dept_id:item.data.id}, function(data) {
                if (data.success) {
                    $('.account-dept-input').before('<p class="account-dept"><a href="/library/washington/depts/' + item.data.id + '/">' + item.value.replace(/ <span class="x-8q">.+<\/span>$/, "") + '</a> <a class="remove-dept" id="remove-dept-' + item.data.id + '" title="Remove this department" href="#">×</a></p>');
                    $('.account-dept-input').hide();
                    $('#dept-input').val('');
                    $('.account-dept-add').show();
                }
            });
        },
        displayValue: function(value, data) {
            return value.replace(/ <span class="x-8q">.+<\/span>$/, "");
        }
    });
    
    
});