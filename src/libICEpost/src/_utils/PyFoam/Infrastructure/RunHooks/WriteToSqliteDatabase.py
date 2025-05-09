"""Write the data to a sqlite database"""

from libICEpost.src._utils.PyFoam.Infrastructure.RunHook import RunHook

from libICEpost.src._utils.PyFoam.Error import error

from libICEpost.src._utils.PyFoam.Basics.RunDatabase import RunDatabase

from os import path

from libICEpost.src._utils.PyFoam.ThirdParty.six import print_

class WriteToSqliteDatabase(RunHook):
    """Write the run information to a sqlite database"""
    def __init__(self,runner,name):
        RunHook.__init__(self,runner,name)

        self.create=self.conf().getboolean("createDatabase")
        self.database=path.expanduser(self.conf().get("database"))

        if not self.create and not path.exists(self.database):
            error("The database",self.database,"does not exists")

    def __call__(self):
        print_("Adding run information to database",self.database)
        db=RunDatabase(self.database,create=self.create)
        db.add(self.runner.getData())
