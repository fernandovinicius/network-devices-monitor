from flask import Flask
from flask_restx import Api
from config import setup_logger
from controllers.data_controller import data_ns
from controllers.device_controller import device_ns
from controllers.history_controller import history_ns


setup_logger()

app = Flask(__name__)
api = Api(
    app,
    title="Network Devices Monitor API",
    version="1.0",
    description="API para monitoramento de dispositivos de rede",
)


# Registre os blueprints normalmente
api.add_namespace(device_ns)
api.add_namespace(data_ns)
api.add_namespace(history_ns)


if __name__ == "__main__":
    app.run(debug=True)
