<?php
mysqli_report(MYSQLI_REPORT_ERROR | MYSQLI_REPORT_STRICT);

$db = mysqli_connect("localhost", "root", "", "bd2");
if (array_key_exists("wow", $_POST)) {
    $input = $_POST["wow"];
    $insert_stmt = mysqli_prepare($db, "insert into bd2.a values (?)");
    mysqli_stmt_bind_param($insert_stmt, 'i', $input);
    mysqli_stmt_execute($insert_stmt);
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>db2</title>
    <script src="main.js" defer></script>
</head>
<body>
    <canvas id="canvas" heigth="400" width="400">
    </canvas>
    <svg height="250" width="300">
      <circle r="105" cx="150" cy="120" fill=<?= array_key_exists("color", $_POST) ? $_POST["color"] : "green" ?> />
    </svg>
    <form method="POST">
        <input type="text" name="wow"><br>
        <input type="text" name="color"><br>
        <input type="submit">
    </form>
</body>
</html>