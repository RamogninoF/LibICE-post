#Classes to use for construction of the thermodynamic type
thermoType = \
    {
        #The equation of state to use
        "EquationOfState":"PerfectGas", #Perfect gas assumption
        
        #The thermodynamic properties for the mixture
        "Thermo":"janaf7",  # 7-coefficients NASA (janaf) polynomials
    }

#Dictionaries for class-specific entries
PerfectGasDict = {}
janaf7Dict = {}

# Here additional thermodynamic data 
# may be added to the database if needed 
# (example: new fuels, molecules, etc.)