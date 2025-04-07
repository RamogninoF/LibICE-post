"""Base class for all Run-Hooks"""

from libICEpost.src._utils.PyFoam import configuration
from libICEpost.src._utils.PyFoam.Error import notImplemented

class RunHook(object):
    """The actual class"""

    def __init__(self,runner,name):
        self.runner=runner
        self.name=name

    def conf(self):
        """Quick access to the configuration"""
        return configuration().sectionProxy(self.name)

    def execute(self):
         notImplemented(self,"execute")