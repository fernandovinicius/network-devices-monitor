from flask import request
from flask_restx import Namespace, Resource, fields
from services.data_service import get_monitoring_data
from loguru import logger
from utils.http_status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_ERROR,
)


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
class MonitoringDataResource(Resource):
    @data_ns.marshal_with(monitoring_data_model)
    def get(self, device_id):
        """Retorna os dados de monitoramento de um dispositivo pelo ID"""
        try:
            data = get_monitoring_data(device_id)
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
