 #!/usr/bin/python3
'''
Example of use of drv flow.
'''
#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations

#######################         GENERIC IMPORTS          #######################
import os
import sys
from sys import path
from time import sleep
from serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE

#######################       THIRD PARTY IMPORTS        #######################

#######################      SYSTEM ABSTRACTION IMPORTS  #######################
path.append(os.getcwd())
from rfb_logger_tool import SysLogLoggerC, sys_log_logger_get_module_logger # pylint: disable=wrong-import-position
if __name__ == '__main__':
    cycler_logger = SysLogLoggerC(file_log_levels='code/log_config.yaml')
log = sys_log_logger_get_module_logger(__name__)

#######################          PROJECT IMPORTS         #######################
from rfb_scpi_sniffer import DrvScpiSerialConfC # pylint: disable=wrong-import-position

#######################          MODULE IMPORTS          #######################
sys.path.append(os.getcwd()+'/code/drv_flow/')
from src.rfb_driver_flow import DrvFlowDeviceC # pylint: disable=wrong-import-position

#######################              ENUMS               #######################

#######################             CLASSES              #######################
__SERIAL_PORT = '/dev/wattrex/arduino/ARDUINO_24233323435351611252'

def example_flowmeter():
    '''
    Example of raw usage of drv_scpi with a flowmeter device.
    '''
    flow_conf_scpi = DrvScpiSerialConfC(port = __SERIAL_PORT,
                                        separator = '\n',
                                        baudrate = 19200,
                                        bytesize = EIGHTBITS,
                                        parity = PARITY_NONE,
                                        stopbits = STOPBITS_ONE ,
                                        timeout = 2, #0.00003,
                                        write_timeout = None,
                                        inter_byte_timeout  = None)

    flowmeter = DrvFlowDeviceC(config = flow_conf_scpi)
    log.info(f"Device: {flowmeter.device_id} \t Firmware: {flowmeter.firmware_version}") # pylint: disable=logging-fstring-interpolation

    cont = 0
    while cont < 10:
        sleep(1.5)
        log.info(f"Get meas: {flowmeter.get_data()}") # pylint: disable=logging-fstring-interpolation
        cont += 1

    flowmeter.close()


if __name__ == '__main__':
    example_flowmeter()
