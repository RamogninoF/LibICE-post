
#####################################################################
#                                  DOC                              #
#####################################################################

"""
Functions for adding user interface functionalities to the ICEpost package.

Content of the module:
    - loadDictionary (`function`): Load a dictionary from a file and a set of templates.

@author: F. Ramognino       <federico.ramognino@polimi.it>
"""

#####################################################################
#                               IMPORT                              #
#####################################################################

from libICEpost import Dictionary

#############################################################################
#                               MAIN FUNCTIONS                              #
#############################################################################
def loadDictionary(path:str, *templates:str, verbose=True) -> Dictionary:
    """
    Load a dictionary from a file. If templates are provided,
    the templates are loaded in reversed order and iteratively updated (the last one is the first loaded, which is iteratively updated).
    Finally, the dictionary is updated with the main one ('path').

    Args:
        path (str): Path to the dictionary file.
        *templates (str): Optional template names to load.
        verbose (bool, optional): If True, print loading information (default is True).

    Returns:
        Dictionary: Loaded dictionary object.
    """
    if verbose:
        print(f"Loading dictionary from: {path}")
    
    # Load the templates control dictionary in order
    D = Dictionary()
    for t in reversed(templates):
        if verbose:
            print(f"\tLoading template: {t}")
        D.update(Dictionary.fromFile(t))
    
    # Load the main control dictionary
    if verbose:
        print(f"\tLoading main dictionary: {path}")
    D.update(Dictionary.fromFile(path))
    
    return D