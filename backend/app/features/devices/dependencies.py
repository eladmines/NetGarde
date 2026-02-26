from app.features.devices.services.device_service import DeviceService
from app.features.devices.services.device_service_interface import IDeviceService


def get_device_service() -> IDeviceService:
    return DeviceService()
