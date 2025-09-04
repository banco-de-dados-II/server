<?php
mysqli_report(MYSQLI_REPORT_ERROR | MYSQLI_REPORT_STRICT);
$db = mysqli_connect("localhost", "root", "", "bd2");

$insert_stmt = mysqli_prepare($db, "insert into bd2.pessoas (nome, email) values (?, ?)");
mysqli_stmt_bind_param($insert_stmt, 'ss', $_POST["$table_user-nome"], $_POST["$table_user-email"]);
mysqli_stmt_execute($insert_stmt);