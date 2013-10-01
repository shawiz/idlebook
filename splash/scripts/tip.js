$(function() {
	$('#email').focus(function() {
		$('#invite-tip').fadeIn('fast');
	});
	
	var timer;
	$('#email').blur(function() {
		timer = setTimeout(removeTip, 10);
	});
	
	$('#submit').click(function() {
		clearTimeout(timer);
	});
	
	$('#invite-form').submit(checkEmail);
	$('#email').keydown(function() {
		$('#error').fadeOut('fast');
		$('#submit').removeClass('clicked');
	});
	
	$('#launch').one('click', function() {
		var launch_time = new Date("August 13, 2011 16:45:00");
		var now = new Date();
		var seconds = Math.floor((launch_time.getTime() - now.getTime()) / 1000);
		launch_countdown.init(seconds, 'countdown');
		$('#bar').show();
		$('#launch').prepend($('<span class="remove">×</span>'));
		$('.remove').click(function() {
			$('#launch').remove();
		});
	});
});

function removeTip() {
	$('#invite-tip').fadeOut('fast');
}

function checkEmail() {
	$('#submit').addClass('clicked');
	var email = $('#email').val();
	if (email.match(/^[\w\.%\-]+@[\w.\-]+\.[a-zA-Z]{2,4}$/)) {
		sendInvite();
	} else {
		$('#error').fadeIn('fast');
		$('#email').focus();
	}
	return false;
}

function sendInvite() {
	$.post('invite.php', $("#invite-form").serialize(), function(data) {
		$('#invite-tip').fadeOut('fast');
		$('#invite-form').replaceWith('<p class="message">' + data + '</p>');
	});
	return false;
}

var launch_countdown = function () {
	var time_left = 3600;
	var output_element_id = 'launch';
	var keep_counting = 1;
	var no_time_left_message = 'NOW';
 
	function countdown() {
		if(time_left < 2) {
			keep_counting = 0;
		}
 
		time_left = time_left - 1;
	}
 
	function add_leading_zero(n) {
		if(n.toString().length < 2) {
			return '0' + n;
		} else {
			return n;
		}
	}
 
	function format_output() {
		var hours, minutes, seconds;
		seconds = time_left % 60;
		minutes = Math.floor(time_left / 60) % 60;
		hours = Math.floor(time_left / 3600);
 
		seconds = add_leading_zero( seconds );
		minutes = add_leading_zero( minutes );
		hours = add_leading_zero( hours );
 
		return hours + ':' + minutes + ':' + seconds;
	}
 
	function show_time_left() {
		document.getElementById(output_element_id).innerHTML = format_output();//time_left;
	}
 
	function no_time_left() {
		document.getElementById(output_element_id).innerHTML = no_time_left_message;
	}
 
	return {
		count: function () {
			countdown();
			show_time_left();
		},
		timer: function () {
			launch_countdown.count();
 
			if(keep_counting) {
				setTimeout("launch_countdown.timer();", 1000);
			} else {
				no_time_left();
			}
		},
		setTimeLeft: function (t) {
			time_left = t;
			if(keep_counting == 0) {
				launch_countdown.timer();
			}
		},
		init: function (t, element_id) {
			time_left = t;
			output_element_id = element_id;
			launch_countdown.timer();
		}
	};
}();

