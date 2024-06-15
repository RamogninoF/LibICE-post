from libICEpost.Database.chemistry.specie.Molecules import Molecules
from libICEpost.src.thermophysicalModels.specie.specie.Mixture import Mixture

mix = Mixture([Molecules.O2, Molecules.H2], [0.5, 0.5], "mass")
print(mix)

pass