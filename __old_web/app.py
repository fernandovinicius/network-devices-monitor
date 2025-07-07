from flask import Flask
from routes import all_routes


app = Flask(__name__)


# Registra todas as rotas
for bp in all_routes:
    app.register_blueprint(bp)

if __name__ == "__main__":
    app.run(debug=True)
