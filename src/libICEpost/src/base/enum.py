#####################################################################
#                                 DOC                               #
#####################################################################

"""
Enumeration classes that when instantiated with a value not in the enumeration, list the allowed values.
This extends the functionality of the standard enum module, adding debugging information 
by extending the `EnumType` metaclass.

Content of the module:
    - `MetaCheckedEnum` (class): Metaclass that adds the functionality of 
    listing the allowed values when an invalid value is passed.
    - `Enum` (class): Enum class that uses the MetaCheckedEnum metaclass.
    - `StrEnum` (class): Enum class that uses the MetaCheckedEnum metaclass 
    and where members are also (and must be) strings.

@author: F. Ramognino       <federico.ramognino@polimi.it>
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

from enum import Enum as _Enum
from enum import StrEnum as _StrEnum
from enum import EnumType

#####################################################################
#                               CODE                                #
#####################################################################
#CheckedEnum metaclass
class MetaCheckedEnum(EnumType):
    """
    Enumeration metaclass that adds the functionality of listing the allowed values when an invalid value is passed.
    """
    def __call__(cls, value, *args, **kwargs):
        try:
            return EnumType.__call__(cls, value, *args, **kwargs)
        except ValueError as err:
            err.add_note(f"Allowed {cls.__name__}s are:\n\t" + '\n\t'.join(cls.__members__.keys()))
            raise err
            
#####################################################################
#Base classes
class Enum(_Enum, metaclass=MetaCheckedEnum):
    """
    Create a collection of name/value pairs. See the enum module for more information.
    """

class StrEnum(_StrEnum, metaclass=MetaCheckedEnum):
    """
    Enum where members are also (and must be) strings.
    """