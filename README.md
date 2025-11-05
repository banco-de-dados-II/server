# tecnologias utilizadas

- mysql
- mongodb (a fazer)
- python
    + flask
    + flask alchemy
    + jinja2

# como executar

## entrar em deselvolvimento

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