from libICEpost.src import GLOBALS
GLOBALS.CUSTOM_ERROR_MESSAGE = False

#Load mixing rules
from libICEpost.src.thermophysicalModels.thermoModels.thermoMixture import mixingRules

#Load database
from libICEpost.Database import database

#Plotting
from matplotlib import pyplot as plt
import numpy as np
from matplotlib import colors as mcolors

from libICEpost.src.thermophysicalModels.specie.specie.Mixture import Mixture, mixtureBlend
from libICEpost.src.thermophysicalModels.thermoModels.thermoMixture.ThermoMixture import ThermoMixture

#########################################################################
# TESTING MIXTURE CLASS
#########################################################################
def testMixture():
    #Load mixture
    from libICEpost.src.thermophysicalModels.specie.specie.Mixture import Mixture

    ################################
    #Create 50/50 (mass) mixture of O2 and N2:
    O2 = database.chemistry.specie.Molecules.O2
    N2 = database.chemistry.specie.Molecules.N2
    myMix1 = Mixture\
    (
        [O2, N2],
        [0.5, 0.5],
        "mass"
    )
    print("myMix1")
    print(myMix1)

    ################################
    #Building it from mole fractions of myMix1
    myMix2 = Mixture\
    (
        [O2, N2],
        myMix1.X,
        "mole"
    )
    print("myMix2")
    print(myMix2)

    ################################
    #Building it as dilution
    myMix3 = Mixture\
    (
        [O2],
        [1],
        "mass"
    )
    myMix3.dilute(N2, 0.5, "mass")
    print("myMix3")
    print(myMix3)

    ################################
    #Assert equalities
    assert myMix1 == myMix2, "Failed myMix1 == myMix2"
    assert myMix1 == myMix3, "Failed myMix1 == myMix3"

#########################################################################
# CHECKING THERMO AND EQUATION OF STATE
#########################################################################
def testThermo(Trange=None):
    #Set the temperature range
    if not Trange is None:
        T = Trange
    else:
        T = np.linspace(300, 3000, 1000)

    #Create the figure
    fig, ax = plt.subplots(1,1)

    colorList = mcolors.TABLEAU_COLORS
    styleList = ["solid", "dashed", "dotted", "dashdot"]
    colors = {}
    ii = 0

    iterType = 0
    l1_plots = {}
    l2_plots = {}
    for thermoType in database.chemistry.thermo.Thermo:
        print(f"Thermo:{thermoType}")
        thermo = database.chemistry.thermo.Thermo[thermoType]
        
        #Plot all thermos:
        for specie in thermo:
            print(f"\tSpecie:{specie}")
            data = thermo[specie]

            if not (specie in colors):
                colors[specie] = colorList[list(colorList.keys())[ii]]
                ii += 1
                if ii == len(colorList):
                    ii = 0
            col = colors[specie]
            
            T = np.linspace(300, 3000, 1000)
            if iterType == 0:
                label = f"specie:{specie} [R={data.Rgas:.2f}]"
            p_cp, = ax.plot(T, [data.cp(0.0,t)/1e3 for t in T], c=col, ls=styleList[iterType], label=label)

            if not specie in l1_plots:
                l1_plots[specie] = p_cp

        if not specie in l2_plots:
            l2_plots[thermoType] = p_cp
        label = "_no"
        iterType += 1

    ax.set_title("$c_p$ [kJ/kgK]")
    ax.set_xlabel("$T$ [K]")

    legend1 = ax.legend([l1_plots[s] for s in l1_plots], list(l1_plots.keys()), loc="center", bbox_to_anchor=(1.3, 0.5))
    ax.legend([l2_plots[s] for s in l2_plots], list(l2_plots.keys()), loc="center", bbox_to_anchor=(-0.3, 0.5))
    ax.add_artist(legend1)
    fig.tight_layout()
    plt.show()

#########################################################################
def testThermoMixture(Trange=None):
    Air = database.chemistry.specie.Mixtures.dryAir.copy()
    Air.dilute(database.chemistry.specie.Molecules.IC8H18, 0.05, 'mass')
    AirThermo = ThermoMixture(Air,"janaf7", "PerfectGas")
    specieThermos = {s["specie"].name:ThermoMixture(Mixture([s["specie"]],[1]),"janaf7", "PerfectGas") for s in Air}
    
    #Set the temperature range
    if not Trange is None:
        T = Trange
    else:
        T = np.linspace(300, 3000, 1000)

    #Create the figure
    fig, ax = plt.subplots(1,3, figsize=(11,9))
    for specie in specieThermos:
        data = specieThermos[specie]
        ax[0].plot(T, [data.cp(0.0,t)/1e3 for t in T], label=specie)
        ax[1].plot(T, [data.cv(0.0,t)/1e3 for t in T], label=specie)
        ax[2].plot(T, [data.gamma(0.0,t) for t in T], label=specie)
    
    ax[0].plot(T, [AirThermo.cp(0.0,t)/1e3 for t in T], label="Mixture")
    ax[1].plot(T, [AirThermo.cv(0.0,t)/1e3 for t in T], label="Mixture")
    ax[2].plot(T, [AirThermo.gamma(0.0,t) for t in T], label="Mixture")
    
    ax[0].set_title("$c_p$ [kJ/kgK]")
    ax[1].set_title("$c_v$ [kJ/kgK]")
    ax[2].set_title("$\gamma$ [-]")
    ax[0].set_xlabel("$T$ [K]")
    ax[1].set_xlabel("$T$ [K]")
    ax[2].set_xlabel("$T$ [K]")
    
    ax[2].legend()
    fig.suptitle("Mixutre: " + " + ".join([f"{s['X']} {s['specie'].name}" for s in Air]))
    fig.tight_layout()
    plt.show()

#########################################################################
def testReaction():
    from libICEpost.src.thermophysicalModels.specie.reactions.ReactionModel.ReactionModel import ReactionModel
    
    CH4 = database.chemistry.specie.Molecules.CH4
    O2 = database.chemistry.specie.Molecules.O2
    H2 = database.chemistry.specie.Molecules.H2
    N2 = database.chemistry.specie.Molecules.N2
    NH3 = database.chemistry.specie.Molecules.NH3
    
    Mix1 = Mixture([H2, CH4, NH3, O2, N2], [0.1, 0.2, 0.1, 0.4, 0.2], 'mole')
    R1 = ReactionModel.selector("StoichiometricCombustion", {"reactants":Mix1})
    
    
#########################################################################

def main1():
    import timeit

    executing = "testThermoMixture(False)"
    num = 10
    glob = \
    {
        "testThermoMixture":testThermoMixture
    }
    
    total_time = timeit.timeit(executing,globals=glob, number=10)
    print("Execution time of",f"'{executing}'","is", total_time/num,"s")

def main2():
    pass

if __name__ == "__main__":
    main2()
