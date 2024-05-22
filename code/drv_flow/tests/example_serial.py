#!/usr/bin/python3

'''
Example to bk precision.
'''

#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations
import sys
import time
from serial import Serial, PARITY_ODD
#######################         GENERIC IMPORTS          #######################


#######################       THIRD PARTY IMPORTS        #######################


#######################      SYSTEM ABSTRACTION IMPORTS  #######################
from rfb_logger_tool import sys_log_logger_get_module_logger
if __name__ == '__main__':
    from rfb_logger_tool import SysLogLoggerC
    cycler_logger = SysLogLoggerC(file_log_levels= 'code/log_config.yaml')
log = sys_log_logger_get_module_logger(__name__)


#######################          PROJECT IMPORTS         #######################
from rfb_scpi_sniffer import DrvScpiSerialConfC

#######################          MODULE IMPORTS          #######################

#######################              ENUMS               #######################

#######################             CLASSES              #######################
def main():
    flow_scpi_conf = DrvScpiSerialConfC(port = '/dev/wattrex/arduino/ARDUINO_85937313737351814170',
                                        separator='\n', baudrate=19200,
                                        timeout=1, write_timeout=1, parity= PARITY_ODD)
    flow_serial: Serial = Serial(port              = flow_scpi_conf.port,
                                baudrate           = flow_scpi_conf.baudrate,
                                # bytesize           = flow_scpi_conf.bytesize,
                                # parity             = flow_scpi_conf.parity,
                                # stopbits           = flow_scpi_conf.stopbits,
                                timeout            = flow_scpi_conf.timeout,
                                write_timeout      = flow_scpi_conf.write_timeout,
                                inter_byte_timeout = flow_scpi_conf.inter_byte_timeout,
                                xonxoff=True, rtscts=False, dsrdtr=False)
    try:
        #Create driver
        input("Press Enter to lock source...")
        flow_serial.write(b':IDN*?\n')
        while not flow_serial.readable():
            pass
        time.sleep(2)
        log.info(flow_serial.readlines())
        input("Press Enter to set output...")
        sys.exit(0)
    except KeyboardInterrupt:
        log.info('SCPI node stopped')
    except Exception as e:
        log.error(f"Error creating handler: {e}")
    finally:
        flow_serial.close()
        sys.exit()

if __name__ == '__main__':
    main()
