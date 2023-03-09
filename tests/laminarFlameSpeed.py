import sys
# setting path
sys.path.append('../')

from src.thermophysicalModels.laminarFlameSpeed.tabulatedLFS.tabulatedLFS import tabulatedLFS

tab = tabulatedLFS.fromFile("./Table")

print(tab.tables["Su"].__dict__)
