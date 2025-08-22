class VehicleNotFoundError(Exception):
    """
    Exception khi không tìm thấy xe
    """
    def __init__(self, vehicle_id: str):
        self.vehicle_id = vehicle_id
        super().__init__(f"Vehicle with ID {vehicle_id} not found")


class DuplicateLicensePlateError(Exception):
    """
    Exception khi biển số xe đã tồn tại
    """
    def __init__(self, license_plate: str):
        self.license_plate = license_plate
        super().__init__(f"Vehicle with license plate {license_plate} already exists")


class DeviceNotFoundError(Exception):
    """
    Exception khi không tìm thấy thiết bị
    """
    def __init__(self, device_id: str):
        self.device_id = device_id
        super().__init__(f"Device with ID {device_id} not found")
