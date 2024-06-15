from libICEpost.src.base.Functions.functionsForOF import scalarList

LL = scalarList.from_file("./cMax")
LL.write("./cMax.dat")