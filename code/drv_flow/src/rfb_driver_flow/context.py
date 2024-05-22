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
DEFAULT_MAX_REQUESTS            : int       = 3
DEFAULT_MAX_READS               : int       = 10
DEFAULT_MAX_MSG                 : int       = 50 # Max number of allowed message per chan
DEFAULT_MAX_MESSAGE_SIZE        : int       = 500 # Size of message sent through IPC message queue
DEFAULT_TX_CHAN                 : str       = 'TX_SCPI' # Name of the TX channel in CAN
DEFAULT_RX_CHAN                 : str       = 'RX_SCPI_FLOW'  #Name of the RX channel for epc



CONSTANTS_NAMES = ('DEFAULT_MAX_REQUESTS', 'DEFAULT_MAX_READS',
                   'DEFAULT_MAX_MSG', 'DEFAULT_MAX_MESSAGE_SIZE',
                   'DEFAULT_TX_CHAN', 'DEFAULT_RX_CHAN',
                   'DEFAULT_TIMEOUT_REC')
sys_conf_update_config_params(context=globals(),
                              constants_names=CONSTANTS_NAMES)
