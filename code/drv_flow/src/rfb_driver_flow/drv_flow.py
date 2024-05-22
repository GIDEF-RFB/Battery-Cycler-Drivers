#!/usr/bin/python3
'''
Driver of ea power supply.
'''
#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations
from sys import path
import os

#######################         GENERIC IMPORTS          #######################
from enum import Enum
from time import sleep, time

#######################       THIRD PARTY IMPORTS        #######################

#######################      SYSTEM ABSTRACTION IMPORTS  #######################
path.append(os.getcwd())
from rfb_logger_tool import SysLogLoggerC, sys_log_logger_get_module_logger # pylint: disable=wrong-import-position
if __name__ == '__main__':
    cycler_logger = SysLogLoggerC(file_log_levels='./log_config.yaml')
log = sys_log_logger_get_module_logger(__name__)
from rfb_shared_tool import SysShdIpcChanC # pylint: disable=wrong-import-position

#######################          PROJECT IMPORTS         #######################
from rfb_scpi_sniffer import DrvScpiSerialConfC, DrvScpiCmdDataC, DrvScpiCmdTypeE
from rfb_driver_bases import DrvBaseStatusE, DrvBaseStatusC

#######################          MODULE IMPORTS          #######################
######################             CONSTANTS              ######################
from .context import (DEFAULT_MAX_MSG, DEFAULT_MAX_MESSAGE_SIZE, DEFAULT_RX_CHAN, DEFAULT_TX_CHAN,
                    DEFAULT_MAX_READS, DEFAULT_MAX_REQUESTS)
#######################              ENUMS               #######################

class _ScpiCmds(Enum):
    "Modes of the device"
    READ_INFO = ':IDN*?'
    SEPARATOR = '\n'
    GET_MEAS  = ':MEASure:FLOW?\n'

#######################             CLASSES              #######################

class DrvFlowDataC():
    "Obtain the data of flowmeter"
    def __init__(self, flow_pos: int, flow_neg: int ) -> None:
        '''
        Args:
            - flow_pos (int): Value of main flow.
            - flow_neg (int): Value of auxiliar flow.
        Raises:
            - None.
        '''
        self.flow_pos: int = flow_pos
        self.flow_neg: int = flow_neg
        self.status: DrvBaseStatusC = DrvBaseStatusC(DrvBaseStatusE.OK)


    def __str__(self) -> str:
        '''
        Returns:
            - result (str): Value of flows.
        Raises:
            - None.
        '''
        result = f"Flow->\tPOS [{self.flow_pos}] - \tNEG:[{self.flow_neg}]" +\
              f"- \tStatus: [{self.status}]"
        return result


class DrvFlowDeviceC():
    "Principal class of flowmeter"
    def __init__(self, config: DrvScpiSerialConfC, jet: int= 0) -> None:
        '''
        Args:
            - config (DrvScpiSerialConfC): Configuration of the serial port.
            - jet (int): Type of jet. 0 is there is no jet.
        Raises:
            - None.
        '''
        if jet < 0 and jet > 4:
            raise ValueError("Jet not valid")
        self.__device_id: int = 0
        self.__firmware_version: int = 0
        self.__tx_chan = SysShdIpcChanC(name = DEFAULT_TX_CHAN)
        self.__rx_chan = SysShdIpcChanC(name = DEFAULT_RX_CHAN+'_'+config.port.split('_')[-1],
                                      max_msg = DEFAULT_MAX_MSG,
                                      max_message_size= DEFAULT_MAX_MESSAGE_SIZE)
        self.__port = config.port
        self.__config = config

        add_msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.ADD_DEV,
                                  port = config.port,
                                  payload = self.__config,
                                  rx_chan_name = DEFAULT_RX_CHAN+'_'+self.__port.split('_')[-1])
        # self.__rx_chan.delete_until_last()
        self.__tx_chan.send_data(add_msg)
        self.__last_meas: DrvFlowDataC = DrvFlowDataC(flow_pos = 0, flow_neg = 0)
        self.read_buffer()
        self.__wait_4_response = False
        self.__request_data = 0
        self.__read_device_properties(jet)
        while self.__firmware_version == 0:
            self.read_buffer()
            sleep(1)


    @property
    def device_id(self) -> int:
        ''' Get the device id. '''
        return self.__device_id


    @property
    def firmware_version(self) -> int:
        ''' Get the firmware version. '''
        return self.__firmware_version

    def read_buffer(self) -> None: #pylint: disable=too-many-branches, too-many-statements
        """
        Reads data from the receive channel and updates the device properties and last data.

        Returns:
            None
        """
        i = 0
        while i < DEFAULT_MAX_READS and not self.__rx_chan.is_empty(): #pylint: disable=too-many-nested-blocks
            msg: DrvScpiCmdDataC = self.__rx_chan.receive_data_unblocking()
            if msg is not None:
                if msg.data_type == DrvScpiCmdTypeE.ERROR:
                    log.critical("ERROR DEVICE NOT ADDED IN SCPI")
                    add_msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.ADD_DEV,
                                    port = self.__port,
                                    payload = self.__config,
                                    rx_chan_name = DEFAULT_RX_CHAN+'_'+self.__port.split('/')[-1])
                    self.__tx_chan.send_data(add_msg)
                    add_msg = DrvScpiCmdDataC(data_type = msg.last_order,
                                    port = self.__port,
                                    payload = msg.payload,
                                    rx_chan_name = DEFAULT_RX_CHAN+'_'+self.__port.split('/')[-1])
                    self.__tx_chan.send_data(add_msg)
                elif msg.data_type == DrvScpiCmdTypeE.RESP: #pylint: disable=too-many-nested-blocks
                    if hasattr(msg, 'status') and msg.status.value == DrvBaseStatusE.COMM_ERROR: #pylint: disable=attribute-defined-outside-init
                        log.critical("ERROR READING DEVICE")
                    for data in msg.payload: #pylint: disable=too-many-nested-blocks #pylint: disable=attribute-defined-outside-init
                        if len(data) >0 and not str(data).startswith(":"):
                            if all (x in data for x in ("error", "Error", "ERROR")):
                                log.critical("Hola")
                                log.error(f"Error reading device: {data}")
                                self.__wait_4_response = False
                                self.__last_meas.status = DrvBaseStatusC(DrvBaseStatusE.COMM_ERROR)
                            elif 'IDN' in data:
                                data = data.split(':')
                                self.__device_id = int(data[data.index('DEVice')+1])
                                self.__firmware_version = int(data[data.index('VERsion')+1])
                                log.critical(f"Device ID: {int(data[data.index('DEVice')+1])} \t Firmware: {int(data[data.index('VERsion')+1])}")
                                self.__wait_4_response = False
                            elif 'MEASure' in data:
                                data = data.split(':')
                                self.__last_meas.flow_pos = int(data[data.index('DATA')+1])
                                self.__last_meas.flow_neg = int(data[data.index('DATA')+2])
                                self.__last_meas.status = DrvBaseStatusC(DrvBaseStatusE.OK)
                                self.__wait_4_response = False
                            log.debug(f"Response: {data}")
            elif msg is None:
                pass
            else:
                log.error(f'Unknown message type received: {msg.__dict__}')
            i += 1

    def __read_device_properties(self, jet_type: int) -> None:
        ''' Read device properties.
        Args:
            - None.
        Returns:
            - None.
        Raises:
            - ConnectionError: Device not found.
        '''
        exception = True
        msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE_READ,
                port = self.__port,
                payload = _ScpiCmds.READ_INFO.value+f'_{jet_type}'+_ScpiCmds.SEPARATOR.value,
                rx_chan_name = DEFAULT_RX_CHAN+'_'+self.__port.split('_')[-1])
        self.__tx_chan.send_data(msg)
        self.read_buffer()
        # Wait until receive the message
        time_init = time()
        exception = True
        while (time() - time_init) < 3:
            sleep(1.5)
            self.read_buffer()
            if self.__firmware_version != 0:
                msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE_READ,
                    port = self.__port,
                    payload = _ScpiCmds.READ_INFO.value+f'_{jet_type}'+_ScpiCmds.SEPARATOR.value,
                    rx_chan_name = DEFAULT_RX_CHAN+'_'+self.__port.split('_')[-1])
                self.__tx_chan.send_data(msg)
            else: exception = False
        if exception:
            raise ConnectionError("Device not found")


    def get_data(self) -> DrvFlowDataC:
        ''' Get the measurement of the flowmeter.
        Args:
            - None.
        Returns:
            - res (DrvFlowDataC): Get the measurement of the flowmeter.
        Raises:
            - None.
        '''
        if self.__request_data >= DEFAULT_MAX_REQUESTS:
            self.__wait_4_response = False
            self.__request_data = 0
        if not self.__wait_4_response:
            msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.WRITE_READ,
                                port = self.__port,
                                payload = _ScpiCmds.GET_MEAS.value,
                                rx_chan_name = DEFAULT_RX_CHAN+'_'+self.__port.split('_')[-1])
            self.__tx_chan.send_data(msg)
            self.__wait_4_response = True
        else:
            self.__request_data += 1
        self.read_buffer()
        return self.__last_meas


    def close(self) -> None:
        ''' Close the serial port.
        Args:
            - None.
        Returns:
            - res (DrvFlowDataC): Get the measurement of the flowmeter.
        Raises:
            - None.
        '''
        del_msg = DrvScpiCmdDataC(data_type = DrvScpiCmdTypeE.DEL_DEV,
                                  port = self.__port) # pylint: disable=no-member
        self.__tx_chan.send_data(del_msg)
        self.__rx_chan.terminate()
