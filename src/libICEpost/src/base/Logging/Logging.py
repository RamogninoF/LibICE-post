from __future__ import annotations
import atexit
import json

import sys

from logging import LogRecord
import logging.config
import logging.handlers

import pathlib

logConfigPath = "/".join(__file__.split("/")[:-1]) + "/logging_configs"

def setup_logging() -> None:
    config_file = pathlib.Path(logConfigPath+"/0-stdout.json")
    with open(config_file) as f_in:
        config = json.load(f_in)

    logging.config.dictConfig(config)

class UsrFormatter(logging.Formatter):
    info_fmt = "%(msg)s"
    
    def _update(self,string:str):
        self._fmt = string
        self._style._fmt = string
    
    def format(self, record):
        
        # Save the original format configured by the user
        # when the logger formatter was instantiated
        format_orig = self._fmt

        # Replace the original format with one customized by logging level
        if record.levelno == logging.INFO:
            self._update(self.info_fmt)

        # Call the original formatter class to do the grunt work
        result = super().format(record)

        # Restore the original format configured by the user
        self._update(format_orig)

        return result

class FilterSwitch(logging.Filter):
    #Acts like the logging.Filter but saves a dictionary with all names to be switched on/off. 
    # By default everything is switched according to self._default
    def __init__(self,name=None, default=True):
        super().__init__()
        if default is None:
            raise ValueError("Default value cannot be None")
        self._default = default
        self._filters = {}
        if not name is None:
            self.add(name)
    
    def add(self, name:str) -> None:
        self._filters[name] = logging.Filter(name)
    
    def remove(self, name:str) -> None:
        if name in self._filters:
            del self._filters[name]
    
    def filter(self, record: LogRecord) -> bool:
        if len(self._filters) == 0:
            return self._default
        found = any(self._filters[f].filter(record) for f in self._filters)
        
        #If a switch triggers, negate the default
        if found:
            return not self._default
        else: 
            return self._default

class LoggingClass:
    _loggers = {}
    
    def __init__(self, name:str, *, parent:LoggingClass = None, level="INFO", switch:bool=None, addHandler=False, formatter:logging.Formatter=None):
        self._handler = None
        if not parent is None:
            name = parent._name + "." + name
            if not parent._handler is None:
                self._handler = parent._handler
            
        self._parent = parent
        self._name = name
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        self._loggers[self._name] = logger
        
        if addHandler:
            if not self._handler is None:
                raise ValueError(f"Handler already present in hierarchy of logger {self._name}")
            
            self._handler = logging.StreamHandler(sys.stdout)
            self._handler.addFilter(FilterSwitch(default=switch))
            self._handler.setFormatter(formatter)
            logger.addHandler(self._handler)
        elif not self._handler is None:
            if not switch is None:
                self.switch(switch)
    
    def getLogger(self, name:str, *, level="INFO", **kwargs):
        return LoggingClass(name, level=level, parent=self, **kwargs)
    
    def __call__(self) -> logging.Logger:
        return LoggingClass._loggers[self._name]

    def switch(self, val:bool):
        filtSwitch = self._handler.filters[-1]._default
        if val and not filtSwitch:
            self._handler.filters[-1].add(self._name)
        else:
            self._handler.filters[-1].remove(self._name)

#Setup loggers
setup_logging()
logger = LoggingClass("libICEpost")
devLogger = logger.getLogger\
    (
        "dev", 
        level="INFO",
        addHandler=True,
        formatter=logging.Formatter("[%(name)s] %(levelname)s: %(message)s"),
        switch=False
    )
    
usrLogger = logger.getLogger\
    (
        "usr", 
        level="INFO",
        addHandler=True,
        formatter=UsrFormatter("%(levelname)s: %(message)s"),
        switch=True
    )

_DEBUG_FORMATTER_LIST = {
    0:logging.Formatter("[%(name)s] %(levelname)s: %(message)s"),
    1:logging.Formatter("[%(name)s] at %(pathname)s:%(lineno)d\n%(levelname)s: %(message)s"),
    #other?
}

#Convenient method to change debug level of dev logger
def set_debug_level(level:int=0):
    if not level in _DEBUG_FORMATTER_LIST:
        raise ValueError(f"Unsupported debug level {level}. Available levels: {list(_DEBUG_FORMATTER_LIST.keys())}")
    devLogger._handler.setFormatter(_DEBUG_FORMATTER_LIST[level])