# Plataforma de gerenciamento com analytics avançado

Uma plataforma moderna para **gerenciamento de dados e visualização analítica** com gráficos, métricas e relatórios.

# Tecnologias utilizadas

- mysql
- mongodb (a fazer)
- python
    + flask
    + flask alchemy
    + jinja2

# Como executar

## Entrar em deselvolvimento

execute um servidor mysql na porta 3306
```batchfile
docker compose up
```

entrar no servidor mysql
``` batchfile
mysql -P 3306 -u root
```

entrar em um ambiente virtual python e
resolver as dependencias do python
```batchfile
python -m venv .venv
.\.venv\Scripts\activate.bat
pip install -r requirements.txt
```

iniciar o serivdor
```batchfile
python -m flask --app main run --debug
```
