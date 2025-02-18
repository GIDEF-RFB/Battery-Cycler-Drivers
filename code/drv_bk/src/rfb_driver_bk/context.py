#!/usr/bin/python3
'''
This module manages the constants variables.
Those variables are used in the scripts inside the module and can be modified
in a config yaml file specified in the environment variable with name declared
in system_config_tool.
'''

#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations
#######################         GENERIC IMPORTS          #######################

#######################      SYSTEM ABSTRACTION IMPORTS  #######################
from rfb_logger_tool import Logger, sys_log_logger_get_module_logger
log: Logger = sys_log_logger_get_module_logger(__name__)

#######################       THIRD PARTY IMPORTS        #######################

#######################          PROJECT IMPORTS         #######################
from rfb_config_tool import sys_conf_update_config_params

#######################          MODULE IMPORTS          #######################

######################             CONSTANTS              ######################
# For further information check out README.md
DEFAULT_MAX_MSG : int           = 100 # Max number of allowed message per chan
DEFAULT_MAX_MESSAGE_SIZE : int  = 400 # Size of message sent through IPC message queue
DEFAULT_TX_CHAN : str           = 'TX_SCPI' #'TX_SCPI' # Name of the TX channel in CAN
DEFAULT_RX_CHAN: str            = 'RX_SCPI_BK'  #Name of the RX channel for epc
DEFAULT_MAX_VOLT: int =1000 #V # Max voltage allowed
DEFAULT_MAX_CURR: int = 20 #A # Max current allowed
DEFAULT_MAX_WAIT_TIME: int = 3
DEFAULT_TIME_BETWEEN_ATTEMPTS: float = 0.1
DEFAULT_MAX_READS: int = 10

CONSTANTS_NAMES = ('DEFAULT_MAX_VOLT', 'DEFAULT_MAX_CURR', 'DEFAULT_MAX_READS',
                   'DEFAULT_MAX_MSG', 'DEFAULT_MAX_MESSAGE_SIZE',
                   'DEFAULT_TX_CHAN', 'DEFAULT_RX_CHAN', 'DEFAULT_MAX_WAIT_TIME')
sys_conf_update_config_params(context=globals(),
                              constants_names=CONSTANTS_NAMES)
