from flask import request
from flask_restx import Namespace, Resource, fields
from loguru import logger
from services.device_service import (
    get_all_devices,
    get_device_by_id,
    get_device_by_ip,
    get_device_by_hostname,
    get_devices_by_status,
    get_enabled_devices,
    create_device,
    update_device,
    delete_device,
)
from utils.http_status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_UPDATED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_ERROR,
)
from models.device_status import DeviceStatus, DEVICE_STATUS_DESC
from models.device_model import DEVICE_CREATION_DESC, DEVICE_DESC


device_ns = Namespace("devices", description="Operações de dispositivos de rede")

# Descrições das Classes
device_model = device_ns.model("Device", DEVICE_DESC)
device_creation_model = device_ns.model("DeviceCreate", DEVICE_CREATION_DESC)
device_status_enum = device_ns.model("DeviceStatus", DEVICE_STATUS_DESC)


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

    @device_ns.expect(device_creation_model)
    @device_ns.marshal_with(device_model, code=HTTP_201_CREATED)
    def post(self):
        """Cria um novo dispositivo"""
        try:
            data = request.get_json()
            result = create_device(data)
        except Exception as e:
            logger.error(f"Erro ao criar dispositivo: {e}")
            device_ns.abort(HTTP_500_INTERNAL_ERROR, "Erro interno.")

        if "error" in result:
            device_ns.abort(HTTP_400_BAD_REQUEST, result["error"])
        return result["data"], HTTP_201_CREATED


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
        except Exception as e:
            logger.error(f"Erro ao buscar dispositivo por ID {id}: {e}")
            device_ns.abort(HTTP_500_INTERNAL_ERROR, "Erro interno.")

        if not device:
            device_ns.abort(HTTP_404_NOT_FOUND, "Dispositivo não encontrado.")
        return device, HTTP_200_OK

    @device_ns.expect(device_model)
    @device_ns.marshal_with(device_model)
    def put(self, id):
        """Atualiza dispositivo por ID"""
        try:
            data = request.get_json()
            result = update_device(id, data)
        except Exception as e:
            logger.error(f"Erro ao atualizar dispositivo {id}: {e}")
            device_ns.abort(HTTP_500_INTERNAL_ERROR, "Erro interno.")

        if "error" in result:
            device_ns.abort(HTTP_400_BAD_REQUEST, result["error"])
        return [], HTTP_204_UPDATED

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
        except Exception as e:
            logger.error(f"Erro ao buscar dispositivo por IP {ip_address}: {e}")
            device_ns.abort(HTTP_500_INTERNAL_ERROR, "Erro interno.")

        if not device:
            device_ns.abort(HTTP_404_NOT_FOUND, "Dispositivo não encontrado.")
        return device, HTTP_200_OK


@device_ns.route("/hostname/<string:hostname>")
class DeviceByHostname(Resource):
    @device_ns.marshal_with(device_model)
    def get(self, hostname):
        """Busca dispositivo por hostname"""
        try:
            device = get_device_by_hostname(hostname)
        except Exception as e:
            logger.error(f"Erro ao buscar dispositivo por HOSTNAME {hostname}: {e}")
            device_ns.abort(HTTP_500_INTERNAL_ERROR, "Erro interno.")

        if not device:
            device_ns.abort(HTTP_404_NOT_FOUND, "Dispositivo não encontrado.")
        return device, HTTP_200_OK


@device_ns.route("/status/<int:status>")
@device_ns.param(
    "status", ", ".join(f"{member.value}: {member.name}" for member in DeviceStatus)
)
class DevicesByStatus(Resource):
    @device_ns.marshal_with(device_model)
    def get(self, status):
        """Busca dispositivos pelo status atual"""
        try:
            devices = get_devices_by_status(status)
        except Exception as e:
            logger.error(f"Erro ao buscar dispositivos com Status={status}: {e}")
            device_ns.abort(HTTP_500_INTERNAL_ERROR, "Erro interno.")

        return devices, HTTP_200_OK
