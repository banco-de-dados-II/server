<?php
$tabela_login = "pessoas";
$args_login = ["email", "senha"];
?>

<!DOCTYPE html>
<html lang="pt-br">
<head>
    <link href="https://fonts.googleapis.com/css2?family=League+Spartan&display=swap" rel="stylesheet">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Plataforma Analytics - Login</title>
    <style>
        body {
            margin: 0;
            font-family:'League Spartan', sans-serif;
            font-size:xx-large;
            background-color: #181818;
            color: white;
        }

        .navbar {
            display:flex;
            align-items: center;
            width: 100%;
            background-color: #111111;
            height: 100px;
            padding-top: 20px;
        }

        .navbar a {
            display: block;
            color: white;
            padding: 15px;
            text-decoration: none;
            transition: 0.3s;
        }

        .logo_dark {
            display: flex;
            align-items: center;
            padding: 10px 20px;
            gap: 10px;
        }

        .logo_dark img {
            width: 100px;
            height: auto;
        }

        .logo-text {
            font-weight: 700;
            font-size: 1.8rem;
            letter-spacing: 2px;
        }

        .navbar a:hover {
            background-color: #575757;
        }

        .main-content {
            padding: 20px;
            flex: 1;
        }

        .form-container {
            background-color: #131313;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(255, 255, 255, 0.1);
            width: 300px;
            margin: 0 auto;
        }

        .form-container h2 {
            margin-bottom: 20px;
        }

        input[type="text"],
        input[type="password"] {
            width: 100%;
            padding: 8px;
            margin: 10px 0;
            border: none;
            border-radius: 4px;
        }

        .btn {
            background-color: #4CAF50;
            border: none;
            color: white;
            padding: 10px 15px;
            cursor: pointer;
            width: 100%;
            margin-top: 10px;
        }

        .btn:hover {
            background-color: #45a049;
        }

    </style>
</head>
<body>

    <div class="navbar">
        <div class="logo_dark">
            <img src="./logo_dark.png" alt="logo" width="70">
            <span class="logo-text">TRIVEREST</span>
        </div> 
    </div>

    <div class="main-content">
        <div class="form-container">
            <h2>Login</h2>
            <form method="POST" action="<?= $tabela_login ?>">
                <?php foreach ($args_login as $arg): ?>
                    <label><?= ucfirst($arg) ?></label>
                    <input type="text" name="<?= "$tabela_login-$arg" ?>"><br>
                <?php endforeach; ?>
                <input class="btn" type="submit" value="Entrar">
            </form>
        </div>
    </div>

</body>
</html>
