#####################################################################
#                                 DOC                               #
#####################################################################

"""
@author: <N. Surname>       <e-mail>
Last update:        DD/MM/YYYY
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

#load the base class
from .EngineModel import EngineModel

#Other imports
from libICEpost.src.base.dataStructures.Dictionary import Dictionary
from libICEpost.src.thermophysicalModels.thermoModels.CombustionModel.PremixedCombustion import PremixedCombustion

#############################################################################
#                               MAIN CLASSES                                #
#############################################################################
class SparkIgnitionEngine(EngineModel):
    """
    Simple spark-ignition engine model with single-zone modeling.
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Attributes:
        
    """
    Types = {t:EngineModel.Types[t] for t in EngineModel.Types}
    Types["CombustionModel"] = PremixedCombustion
    
    #########################################################################
    #Properties:

    #########################################################################
    #Class methods and static methods:
    
    @classmethod
    def fromDictionary(cls, dictionary:Dictionary) -> EngineModel:
        """
        Construct from dictionary like:
        {
            EngineTime:         str
                Name of the EngineTime model to use
            <EngineTime>Dict:   dict
                Dictionary containing the data specific of the selected 
                SngineTime model (e.g., if engineTime is 'SparkIgnitionTime',
                then this dictionary must be named 'SparkIgnitionTimeDict'). 
                See at the helper for function 'fromDictionary' of the specific 
                EngineTime model selected.
                
            EngineGeometry:         str
                Name of the EngineGeometry model to use
            <EngineGeometry>Dict:   dict
                Dictionary with data required from engineGeometry.
                See at the helper for function 'fromDictionary' of the specific 
                EngineGeometry model selected.
            
            CombustionModel:         str
                Name of the CombustionModel to use
            <CombustionModel>Dict:   dict
                Dictionary with data required from CombustionModel
                See at the helper for function 'fromDictionary' of the specific 
                CombustionModel model selected.
        }
        """
        try:
            #Manipulating the combustionProperties
            
            
            return super().fromDictionary(dictionary)
        
        except BaseException as err:
            cls.fatalErrorInClass(cls.fromDictionary, "Failed contruction from dictionary", err)
    
    #########################################################################
    # def __init__(self, arg2:<type_arg2>, arg1:<type_arg1>=default_val1):
    #     """
    #     arg2 (<type_arg2>): Description
    #     arg1 (<type_arg1>): Description (default: default_val1)
    #     """
    #     #Argument checking:
    #     try:
    #         # Check that the arguments satisfy what is expected from the init method

    #         #Type checking
    #         self.checkType(arg2, type_arg2, "arg2")

    #         #Here I only check for arg2 as arg1 is already handled bu the __init__ of class Base
            
    #         #...
    #     except BaseException as err:
    #         self.fatalErrorInArgumentChecking(self.__init__, err)
        
    #     try:
    #         #Initialize the object
    #         #Here might be convenient to call the __init__ method of the base
    #         #class to initialize arg1 which is shared with the base class Base.
    #         #To do so i use the function super()

    #         super().__init__(arg1)

    #         #Other stuff to initialize specific of Child


    #     except BaseException as err:
    #         self.fatalErrorInClass(self.__init__, "Failed construction of ...", err)
    
    #########################################################################
    #Dunder methods:
    
    #########################################################################
    #Methods:
    def process(self):
        """
        Process the data (to be overwritten)
        """
        pass

#########################################################################
#Add to selection table of Base
EngineModel.addToRuntimeSelectionTable(SparkIgnitionEngine)
