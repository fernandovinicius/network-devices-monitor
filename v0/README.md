## Preparação do Ambiente

Requisitos:
- Python 3.11+

<br>

```bash
    # Cria ambiente virtual
    python -m venv venv

    # Ativar ambiente -- Windows
    ./venv/Scripts/activate

    # Ativar ambiente -- Linux
    source ./venv/bin/activate

    # Atualizar pip e instalar requisitos
    python -m pip install --upgrade pip
    pip install -r requirements.txt
```


## Backend

Abra um novo terminal, e ative o ambiente virtual Python conforme o passo anterior.


### 1) Criar Banco de Dados

```bash
    cd ./backend/database/
    python create_db.py
```
- Nesse diretório deverá ser criado um arquivo para o banco de dados SQLite, com o nome "___network\_monitor.db___".

_______

### 2) Iniciar Monitoração

 - Confira no arquivo _config.py_ (dentro da pasta _monitor_) se a variável __DATABASE_URL__ está apontando corretamente para o banco de dados.

 - Para executar a aplicação de monitoração:
```bash
    cd ./backend/monitor/
    python main.py
```

- A aplicação de monitoração começará a executar de forma ininterrupta.

_______

## Frontend

 - Em um novo terminal, diferente de onde o backend está sendo executado, ative o ambiente virtual Python e execute:

 - Confira no arquivo _config.py_ (dentro da pasta _web-app_) se a variável __DATABASE_URL__ está apontando corretamente para o banco de dados.

```bash
    cd web-app
    python app.py
```

Abra no browser o endereço: http://localhost:5000