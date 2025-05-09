#  ICE Revision: $Id$
""" Utility-classes for OpenFOAM

Module for the Execution of OpenFOAM-commands and processing their output
"""

from libICEpost.src._utils.PyFoam.Infrastructure.Configuration import Configuration


def version():
    """:return: Version number as a tuple"""
    return (2023, 7)   # Release version
    # return (2023, 7, 99)  # Change in bin/pyFoamVersion.py as well !!!!


def versionString():
    """:return: Version number of PyFoam"""
    v = version()

    vStr = "%d" % v[0]
    for d in v[1:]:
        if type(d) == int:
            vStr += (".%d" % d)
        else:
            vStr += ("-%s" % str(d))
    return vStr


def foamVersionString():
    from libICEpost.src._utils.PyFoam.FoamInformation import foamVersionString
    return foamVersionString()


_configuration = Configuration()


def configuration():
    """:return: The Configuration information of PyFoam"""
    return _configuration

# Should work with Python3 and Python2
