from datetime import datetime
from flask import request
from flask_restx import Namespace, Resource, fields
from utils.http_status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_ERROR,
)
from utils.validation import validate_datetime
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
@history_ns.param("device_id", "ID do dispositivo")
class DeviceHistoryResource(Resource):
    @history_ns.doc(
        params={
            "begin_date": {
                "description": "Data/hora inicial no formato ISO 8601 (ex: 2025-07-29T23:11:32)",
                "required": False,
                "type": "string",
            },
            "end_date": {
                "description": "Data/hora final no formato ISO 8601 (ex: 2025-07-30T23:11:32)",
                "required": False,
                "type": "string",
            },
        }
    )
    @history_ns.marshal_list_with(device_status_history_model)
    def get(self, device_id):
        """Retorna o histórico de status de um dispositivo pelo ID e intervalo de datas (ISO 8601)"""

        # Verifica Datas
        begin_date = request.args.get("begin_date")
        end_date = request.args.get("end_date")
        if (begin_date and not validate_datetime(begin_date)) or (
            end_date and not validate_datetime(end_date)
        ):
            history_ns.abort(
                HTTP_400_BAD_REQUEST,
                "Formato de data inválido. Use o formato ISO 8601: YYYY-MM-DDTHH:MM",
            )

        # Requisição no Banco
        try:
            history = get_device_history(device_id, begin_date, end_date)
        except Exception as e:
            logger.error(f"Erro ao buscar histórico do dispositivo {device_id}: {e}")
            history_ns.abort(HTTP_500_INTERNAL_ERROR, "Erro interno.")

        if not history:
            history_ns.abort(
                HTTP_404_NOT_FOUND, "Histórico não encontrado para o dispositivo."
            )
        return history, HTTP_200_OK
