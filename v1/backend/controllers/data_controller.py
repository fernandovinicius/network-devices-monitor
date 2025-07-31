from flask import request
from flask_restx import Namespace, Resource, fields
from services.data_service import get_monitoring_data
from loguru import logger
from utils.http_status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_ERROR,
)
from utils.validation import validate_datetime


data_ns = Namespace("monitoring", description="Dados de monitoramento dos dispositivos")

monitoring_data_model = data_ns.model(
    "MonitoringData",
    {
        "timestamp": fields.String(description="Data e hora da coleta"),
        "device_id": fields.Integer(description="ID do dispositivo"),
        "status": fields.String(description="Status do dispositivo"),
        "pack_sent": fields.Integer(description="Pacotes enviados"),
        "pack_recv": fields.Integer(description="Pacotes recebidos"),
        "rtt_min": fields.Float(description="RTT mínimo"),
        "rtt_max": fields.Float(description="RTT máximo"),
        "rtt_avg": fields.Float(description="RTT médio"),
    },
)


@data_ns.route("/<int:device_id>")
@data_ns.param("device_id", "ID do dispositivo")
class MonitoringDataResource(Resource):
    @data_ns.doc(
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
    @data_ns.marshal_with(monitoring_data_model)
    def get(self, device_id):
        """Retorna os dados de monitoramento de um dispositivo por ID e intervalo de datas (ISO 8601)"""

        # Verifica Datas
        begin_date = request.args.get("begin_date")
        end_date = request.args.get("end_date")
        if (begin_date and not validate_datetime(begin_date)) or (
            end_date and not validate_datetime(end_date)
        ):
            data_ns.abort(
                HTTP_400_BAD_REQUEST,
                "Formato de data inválido. Use o formato ISO 8601: YYYY-MM-DDTHH:MM",
            )

        try:
            data = get_monitoring_data(device_id, begin_date, end_date)
        except Exception as e:
            logger.error(
                f"Erro ao buscar dados de monitoramento para o dispositivo {device_id}: {e}"
            )
            data_ns.abort(HTTP_500_INTERNAL_ERROR, "Erro interno.")

        if not data:
            data_ns.abort(
                HTTP_404_NOT_FOUND, "Nenhum dado de monitoramento encontrado."
            )
        return data, HTTP_200_OK
