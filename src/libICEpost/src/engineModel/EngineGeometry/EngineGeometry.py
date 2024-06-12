#####################################################################
#                                 DOC                               #
#####################################################################

"""
@author: F. Ramognino       <federico.ramognino@polimi.it>
Last update:        12/06/2023
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

from libICEpost.src.base.BaseClass import BaseClass, abstractmethod

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class EngineGeometry(BaseClass):
    """
    Base class for handling engine geometrical parameters during cycle.
    
    NOTE: Crank angles are defined with 0 CAD at TDC
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attibutes:
        
    """
    
    
    #########################################################################
    def __str__(self):
        STR =  "{:15s} {:15s}".format("TypeName", self.TypeName)
        
        return STR
    
    ###################################
    #Instant. chamber volume:
    @abstractmethod
    def V(self,CA):
        """
        CA:     float / list<float/int>
            Crank angle
        
        Returns the instantaneous chamber volume at CA
        """
        pass
    
    ###################################
    #Time (in CA) derivative of chamber volume:
    @abstractmethod
    def dVdCA(self,CA):
        """
        CA:     float / list<float/int>
            Crank angle
        
        Returns the time (in CA) derivative of instantaneous in-cylinder at CA
        """
        pass
    
    
#########################################################################
#Create selection table
EngineGeometry.createRuntimeSelectionTable()