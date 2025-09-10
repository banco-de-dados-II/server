<?php
require "db.php";
$insert_stmt = mysqli_prepare($db, "insert into bd2.pessoas (nome, email) values (?, ?)");
mysqli_stmt_bind_param($insert_stmt, 'ss', $_POST["$tabela_login-nome"], $_POST["$tabela_login-email"]);
mysqli_stmt_execute($insert_stmt);