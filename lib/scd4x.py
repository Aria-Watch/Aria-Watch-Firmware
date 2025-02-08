import time
import machine
from micropython import const

class SCD4X:

    DEFAULT_ADDRESS = 0x62
    DATA_READY = const(0xE4B8)
    STOP_PERIODIC_MEASUREMENT = const(0x3F86)
    START_PERIODIC_MEASUREMENT = const(0x21B1)
    READ_MEASUREMENT = const(0xEC05)
    REINIT = const(0x3646)
    FACTORY_RESET = const(0x3632)
    FORCED_RECAL = const(0x362F)
    SELF_TEST = const(0x3639)
    START_LOWPOWER_PERIODIC_MEASUREMENT = const(0x21AC)
    SERIALNUMBER = const(0x3682)
    GET_TEMP_OFFSET = const(0x2318)
    SET_TEMP_OFFSET = const(0x241D)
    GET_ALTITUDE = const(0x2322)
    SET_ALTITUDE = const(0x2427)
    SET_PRESSURE = const(0xE000)
    PERSIST_SETTINGS = const(0x3615)
    GET_ASCE = const(0x2313)
    SET_ASCE = const(0x2416)

    def __init__(self, i2c_bus, address=DEFAULT_ADDRESS):
        self.i2c_device = i2c_bus
        self.address = address
        self._buffer = bytearray(18)
        self._cmd = bytearray(2)
        self._crc_buffer = bytearray(2)

        self._temperature = None
        self._relative_humidity = None
        self._co2 = None

        self.stop_periodic_measurement()

    @property
    def co2(self):
        if self.data_ready:
            self._read_data()
        return self._co2

    @property
    def temperature(self):
        if self.data_ready:
            self._read_data()
        return self._temperature

    @property
    def relative_humidity(self):
        if self.data_ready:
            self._read_data()
        return self._relative_humidity

    def reinit(self):
        self.stop_periodic_measurement()
        self._send_command(REINIT, cmd_delay=0.02)

    def factory_reset(self):
        self.stop_periodic_measurement()
        self._send_command(FACTORY_RESET, cmd_delay=1.2)

    def force_calibration(self, target_co2):
        self.stop_periodic_measurement()
        self._set_command_value(FORCED_RECAL, target_co2)
        time.sleep(0.5)
        self._read_reply(self._buffer, 3)
        correction = struct.unpack_from(">h", self._buffer[0:2])[0]
        if correction == 0xFFFF:
            raise RuntimeError(
                "Forced recalibration failed.\
            Make sure sensor is active for 3 minutes first"
            )

    @property
    def self_calibration_enabled(self):
        self._send_command(GET_ASCE, cmd_delay=0.001)
        self._read_reply(self._buffer, 3)
        return self._buffer[1] == 1

    @self_calibration_enabled.setter
    def self_calibration_enabled(self, enabled: bool):
        self._set_command_value(SET_ASCE, enabled)

    def self_test(self):
        self.stop_periodic_measurement()
        self._send_command(SELF_TEST, cmd_delay=10)
        self._read_reply(self._buffer, 3)
        if (self._buffer[0] != 0) or (self._buffer[1] != 0):
            raise RuntimeError("Self test failed")
        
    def _read_data(self):
        self._send_command(self.READ_MEASUREMENT, cmd_delay=0.001)
        self._read_reply(self._buffer, 9)
        self._co2 = (self._buffer[0] << 8) | self._buffer[1]
        temp = (self._buffer[3] << 8) | self._buffer[4]
        self._temperature = -45 + 175 * (temp / 2 ** 16)
        humi = (self._buffer[6] << 8) | self._buffer[7]
        self._relative_humidity = 100 * (humi / 2 ** 16)

    @property
    def data_ready(self):
        self._send_command(self.DATA_READY, cmd_delay=0.001)
        self._read_reply(self._buffer, 3)
        return not ((self._buffer[0] & 0x03 == 0) and (self._buffer[1] == 0))
    
    @property
    def serial_number(self):
        self._send_command(SERIALNUMBER, cmd_delay=0.001)
        self._read_reply(self._buffer, 9)
        return (
            self._buffer[0],
            self._buffer[1],
            self._buffer[3],
            self._buffer[4],
            self._buffer[6],
            self._buffer[7],
        )

    def stop_periodic_measurement(self):
        self._send_command(self.STOP_PERIODIC_MEASUREMENT, cmd_delay=0.5)

    def start_periodic_measurement(self):
        self._send_command(self.START_PERIODIC_MEASUREMENT, cmd_delay=0.01)
        
    def start_low_periodic_measurement(self):
        self._send_command(START_LOWPOWER_PERIODIC_MEASUREMENT)

    def persist_settings(self):
        self._send_command(PERSIST_SETTINGS, cmd_delay=0.8)

    def set_ambient_pressure(self, ambient_pressure):
        if ambient_pressure < 0 or ambient_pressure > 65535:
            raise AttributeError("`ambient_pressure` must be from 0~65535 hPascals")
        self._set_command_value(SET_PRESSURE, ambient_pressure)

    @property
    def temperature_offset(self):
        self._send_command(GET_TEMP_OFFSET, cmd_delay=0.001)
        self._read_reply(self._buffer, 3)
        temp = (self._buffer[0] << 8) | self._buffer[1]
        return 175.0 * temp / 2**16

    @temperature_offset.setter
    def temperature_offset(self, offset: Union[int, float]) :
        if offset > 374:
            raise AttributeError(
                "Offset value must be less than or equal to 374 degrees Celsius"
            )
        temp = int(offset * 2**16 / 175)
        self._set_command_value(SET_TEMP_OFFSET, temp)

    @property
    def altitude(self):
        self._send_command(GET_ALTITUDE, cmd_delay=0.001)
        self._read_reply(self._buffer, 3)
        return (self._buffer[0] << 8) | self._buffer[1]

    @altitude.setter
    def altitude(self, height):
        if height > 65535:
            raise AttributeError("Height must be less than or equal to 65535 meters")
        self._set_command_value(SET_ALTITUDE, height)
    
    def _send_command(self, cmd, cmd_delay=0.0):
        self._cmd[0] = (cmd >> 8) & 0xFF
        self._cmd[1] = cmd & 0xFF
        self.i2c_device.writeto(self.address, self._cmd)
        time.sleep(cmd_delay)
    
    def _set_command_value(self, cmd, value, cmd_delay=0):
        self._buffer[0] = (cmd >> 8) & 0xFF
        self._buffer[1] = cmd & 0xFF
        self._crc_buffer[0] = self._buffer[2] = (value >> 8) & 0xFF
        self._crc_buffer[1] = self._buffer[3] = value & 0xFF
        self._buffer[4] = self._crc8(self._crc_buffer)
        self.i2c_device.writeto(self.address, self._buffer[:5])
        time.sleep(cmd_delay)

    def _read_reply(self, buff, num):
        self.i2c_device.readfrom_into(self.address, buff, num)
        self._check_buffer_crc(self._buffer[0:num])

    def _check_buffer_crc(self, buf: bytearray):
        for i in range(0, len(buf), 3):
            self._crc_buffer[0] = buf[i]
            self._crc_buffer[1] = buf[i + 1]
            if self._crc8(self._crc_buffer) != buf[i + 2]:
                raise RuntimeError("CRC check failed while reading data")
        return True

    @staticmethod
    def _crc8(buffer):
        crc = 0xFF
        for byte in buffer:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = (crc << 1) ^ 0x31
                else:
                    crc = crc << 1
        return crc & 0xFF  # return the bottom 8 bits
