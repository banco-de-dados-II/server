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

- execute um servidor mysql na porta 3306

para resolver as dependencias


```sh
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

iniciar o serivdor
```sh
python -m flask --app main run --debug
```
