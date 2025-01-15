from libICEpost.src.thermophysicalModels.thermoModels.EgrModel.StoichiometricMixtureEGR import StoichiometricMixtureEGR
from libICEpost.src.thermophysicalModels.thermoModels.CombustionModel.PremixedCombustion import PremixedCombustion
from libICEpost.src.thermophysicalModels.specie.reactions.ReactionModel.functions import computeAlphaSt

#Database
from libICEpost.Database.chemistry.specie.Mixtures import Mixtures, Molecules, Mixture

#Chemistry
print("========================================")
print("Testing air-fuel mixtures computation")
print("========================================")
#Air and fuel
air:Mixture = Mixtures.dryAir
fuel:Mixture = Mixture([Molecules.IC8H18], [1.0])

print(f"Air composition = {[(mol.specie.name, mol.Y) for mol in air]}")
print(f"Fuel composition = {[(mol.specie.name, mol.Y) for mol in fuel]}")
print()

#Data
phi = 2.0
alphaSt = computeAlphaSt(air, fuel)
alpha = alphaSt/phi
yf = 1. / (alpha + 1.)
mixture = air.copy().dilute(fuel, yf, "mass")

print(f"phi = {phi}")
print(f"alphaSt = {alphaSt}")
print(f"alpha = {alpha}")
print(f"yf = {yf}")
print(f"Air+Fuel = {[(mol.specie.name, mol.Y) for mol in mixture]}")
print()

#EgrModel
print("========================================")
print(f"Testing classes: {StoichiometricMixtureEGR.mro()[1].__name__}.{StoichiometricMixtureEGR.__name__}")
print("========================================")
egr = 0.2
combEff = 1.0
egrModel = StoichiometricMixtureEGR(mixture=mixture, air=air, fuel=fuel, egr=egr, combustionEfficiency=combEff)
dilutedMix = mixture.copy().dilute(egrModel.EgrMixture, egr)

print(f"egr = {egr}")
print(f"combEff = {combEff}")
print(f"EgrMix = {[(mol.specie.name, mol.Y) for mol in egrModel.EgrMixture]}")
print(f"dilutedMix = {[(mol.specie.name, mol.Y) for mol in dilutedMix]}")
print()

#CombustionModel
print("========================================")
print(f"Testing classes: {PremixedCombustion.mro()[1].__name__}.{PremixedCombustion.__name__}")
print("========================================")
xb = 0.2
combMod = PremixedCombustion(reactants=dilutedMix, air=air, fuel=fuel, xb=xb)

print(f"xb = {xb}")
print(f"freshMixture = {[(mol.specie.name, mol.Y) for mol in combMod.freshMixture]}")
print(f"combustionProducts = {[(mol.specie.name, mol.Y) for mol in combMod.combustionProducts]}")
print(f"mixture = {[(mol.specie.name, mol.Y) for mol in combMod.mixture]}")
print()

import pandas as pd
from pandas import DataFrame as df
import numpy as np
from matplotlib import pyplot as plt    

xList = np.linspace(0,1,100)
species = [mol.specie.name for mol in combMod.combustionProducts] + [mol.specie.name for mol in combMod.freshMixture if not mol.specie in combMod.combustionProducts]
outputs = df({s:[] for s in species + ["xb"]}, dtype=float)

for ii,xb in enumerate(xList):
    combMod.update(xb=xb)
    out = {s:(combMod.mixture[s].Y if s in combMod.mixture else 0.0) for s in species}
    out.update(xb=xb)
    outputs = pd.concat([outputs, df(out,index=[ii])], axis=0)


ax = outputs.plot(x="xb",y=species)
for ii, specie in enumerate(species):
    ax.axhline(egrModel.EgrMixture[specie].Y*egr if specie in egrModel.EgrMixture else 0.0, color=plt.color_sequences["tab10"][ii], ls="--")

plt.axvline(0,c="k", lw=2)
plt.axvline(1,c="k", lw=2)
plt.grid(True)
plt.xlim([0,1])

plt.tight_layout()
plt.show()