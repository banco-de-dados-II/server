<?php
mysqli_report(MYSQLI_REPORT_ERROR | MYSQLI_REPORT_STRICT);
$db = mysqli_connect("localhost", "root", "", "bd2");
$tabela_login = "pessoas";
$args_login = [ "nome", "email" ];