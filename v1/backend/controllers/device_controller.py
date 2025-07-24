from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from loguru import logger
from services.device_service import (
    get_all_devices,
    get_device_by_id,
    get_device_by_ip,
    get_device_by_hostname,
    create_device,
    get_enabled_devices,
    update_device,
    delete_device,
)
from utils.http_status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_ERROR,
)
from models.device_model import Device

device_ns = Namespace("devices", description="Operações de dispositivos de rede")

device_model = device_ns.model(
    "Device",
    {
        "id": fields.Integer(description="ID do dispositivo"),
        "ip_address": fields.String(required=True, description="Endereço IP"),
        "hostname": fields.String(required=True, description="Hostname"),
        "site": fields.String(required=True, description="Site"),
        "type": fields.String(required=True, description="Tipo"),
        "monitoring_interval_seconds": fields.Integer(
            description="Intervalo de monitoramento (segundos)"
        ),
        "ping_timeout_ms": fields.Integer(description="Timeout do ping (ms)"),
        "ping_count": fields.Integer(description="Quantidade de pings"),
        "monitoring_enabled": fields.Boolean(description="Monitoramento habilitado"),
        "current_status": fields.String(description="Status atual"),
        "last_status_change": fields.String(description="Última alteração de status"),
        "current_history_id": fields.Integer(
            description="ID do histórico atual do dispositivo"
        ),
    },
)

device_status_enum = device_ns.model(
    "DeviceStatus",
    {
        "UP": fields.Integer(example=0, description="Dispositivo está online"),
        "DOWN": fields.Integer(example=1, description="Dispositivo está offline"),
        "NOT_STARTED": fields.Integer(
            example=99, description="Monitoramento não iniciado"
        ),
    },
)


@device_ns.route("/")
class DeviceList(Resource):
    @device_ns.marshal_list_with(device_model)
    def get(self):
        """Lista todos os dispositivos"""
        try:
            devices = get_all_devices()
            return devices, HTTP_200_OK
        except Exception as e:
            logger.error(f"Erro ao buscar dispositivos: {e}")
            device_ns.abort(
                HTTP_500_INTERNAL_ERROR, "Erro interno ao buscar dispositivos."
            )

    @device_ns.expect(device_model)
    @device_ns.marshal_with(device_model, code=HTTP_201_CREATED)
    def post(self):
        """Cria um novo dispositivo"""
        try:
            data = request.get_json()
            result = create_device(data)
            if "error" in result:
                device_ns.abort(HTTP_400_BAD_REQUEST, result["error"])
            return result, HTTP_201_CREATED
        except Exception as e:
            logger.error(f"Erro ao criar dispositivo: {e}")
            device_ns.abort(HTTP_500_INTERNAL_ERROR, "Erro interno.")


@device_ns.route("/enabled")
class EnabledDevices(Resource):
    @device_ns.marshal_list_with(device_model)
    def get(self):
        """Lista dispositivos habilitados"""
        try:
            devices = get_enabled_devices()
            return devices, HTTP_200_OK
        except Exception as e:
            logger.error(f"Erro ao buscar dispositivos habilitados: {e}")
            device_ns.abort(
                HTTP_500_INTERNAL_ERROR,
                "Erro interno ao buscar dispositivos habilitados.",
            )


@device_ns.route("/<int:id>")
class DeviceById(Resource):
    @device_ns.marshal_with(device_model)
    def get(self, id):
        """Busca dispositivo por ID"""
        try:
            device = get_device_by_id(id)
            if device:
                return device, HTTP_200_OK
            else:
                logger.info(f"Dispositivo com ID {id} não encontrado.")
                device_ns.abort(HTTP_404_NOT_FOUND, "Dispositivo não encontrado.")
        except Exception as e:
            logger.error(f"Erro ao buscar dispositivo por ID {id}: {e}")
            device_ns.abort(HTTP_500_INTERNAL_ERROR, "Erro interno.")

    @device_ns.expect(device_model)
    @device_ns.marshal_with(device_model)
    def put(self, id):
        """Atualiza dispositivo por ID"""
        try:
            data = request.get_json()
            result = update_device(id, data)
            if "error" in result:
                device_ns.abort(HTTP_400_BAD_REQUEST, result["error"])
            return result, HTTP_200_OK
        except Exception as e:
            logger.error(f"Erro ao atualizar dispositivo {id}: {e}")
            device_ns.abort(HTTP_500_INTERNAL_ERROR, "Erro interno.")

    def delete(self, id):
        """Deleta dispositivo por ID"""
        try:
            result = delete_device(id)
            return result, HTTP_200_OK
        except Exception as e:
            logger.error(f"Erro ao deletar dispositivo {id}: {e}")
            device_ns.abort(HTTP_500_INTERNAL_ERROR, "Erro interno.")


@device_ns.route("/ip/<string:ip_address>")
class DeviceByIp(Resource):
    @device_ns.marshal_with(device_model)
    def get(self, ip_address):
        """Busca dispositivo por IP"""
        try:
            device = get_device_by_ip(ip_address)
            if device:
                return device, HTTP_200_OK
            else:
                device_ns.abort(HTTP_404_NOT_FOUND, "Dispositivo não encontrado.")
        except Exception as e:
            logger.error(f"Erro ao buscar dispositivo por IP {ip_address}: {e}")
            device_ns.abort(HTTP_500_INTERNAL_ERROR, "Erro interno.")


@device_ns.route("/hostname/<string:hostname>")
class DeviceByHostname(Resource):
    @device_ns.marshal_with(device_model)
    def get(self, hostname):
        """Busca dispositivo por hostname"""
        try:
            device = get_device_by_hostname(hostname)
            if device:
                return device, HTTP_200_OK
            else:
                device_ns.abort(HTTP_404_NOT_FOUND, "Dispositivo não encontrado.")
        except Exception as e:
            logger.error(f"Erro ao buscar dispositivo por HOSTNAME {hostname}: {e}")
            device_ns.abort(HTTP_500_INTERNAL_ERROR, "Erro interno.")
