from flask_restx import Namespace, Resource, fields
from utils.http_status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_ERROR,
)
from services.history_service import get_device_history
from loguru import logger

history_ns = Namespace("history", description="Histórico de status dos dispositivos")

device_status_history_model = history_ns.model(
    "DeviceStatusHistory",
    {
        "id": fields.Integer(description="ID do histórico"),
        "device_id": fields.Integer(description="ID do dispositivo"),
        "status": fields.String(description="Status do dispositivo"),
        "last_status_change": fields.String(
            description="Data/hora da última alteração"
        ),
        "count": fields.Integer(description="Quantidade de ocorrências"),
    },
)


@history_ns.route("/<int:device_id>")
class DeviceHistoryResource(Resource):
    @history_ns.marshal_list_with(device_status_history_model)
    def get(self, device_id):
        """Retorna o histórico de status de um dispositivo pelo ID"""
        try:
            history = get_device_history(device_id)
            if history:
                return history, HTTP_200_OK
            else:
                history_ns.abort(
                    HTTP_404_NOT_FOUND, "Histórico não encontrado para o dispositivo."
                )
        except Exception as e:
            logger.error(f"Erro ao buscar histórico do dispositivo {device_id}: {e}")
            history_ns.abort(HTTP_500_INTERNAL_ERROR, "Erro interno.")
