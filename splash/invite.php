<?php

$db = mysql_connect("localhost", "inviter", "YouMuYou!");
if (!$db) {
	die("Connect failed: " . mysql_error());
}

if (!mysql_select_db("idlebook_invites")) {
	die("Selecting DB failed: " . mysql_error());
}

$email = mysql_real_escape_string(trim($_POST['email']));

$query = sprintf("SELECT * FROM email WHERE email = '%s'", $email);

$result = mysql_query($query) or die(mysql_error());

if (mysql_num_rows($result) !=0) {
	print "You're already in our invite list.";
} else {
	$query = sprintf("INSERT INTO email(email) VALUES ('%s')", $email);
	
	$results = mysql_query($query) or print(mysql_errno());
	
	print "Thank you. We'll send you an invite as soon as our preview is ready.";
}

mysql_close($db);

?>