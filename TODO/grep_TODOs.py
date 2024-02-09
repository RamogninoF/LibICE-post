import os

thisPath = "/".join(__file__.split("/")[:-1])
outputFileName = thisPath + "/TODO.out"

with open(outputFileName,"w") as outputFile:
    #Grep TODOs
    fileName = "grep.tmp"
    print(f"grep TODO -rn {thisPath}/../libICEpost > {thisPath}/{fileName}")
    os.system(f"grep TODO -rn {thisPath}/../libICEpost > {thisPath}/{fileName}")

    with open(thisPath+"/"+fileName) as f:
        for line in f:
            if ":" in line:
                line = line.split(":")
                file = line[0]
                lineNum = int(line[1])
                
                with open(file) as ff:
                    output = ""
                    ii = 1
                    for l in ff:
                        if ii >= lineNum:
                            end = False
                            for char in l:
                                if char == " ":
                                    continue
                                elif char != "#":
                                    end = True
                                    break
                                output += l[1:]
                                break
                            if end:
                                break
                        ii += 1

                outputFile.write(" ".join([file,"at line",str(lineNum)]) + ":\n")
                outputFile.write(output + "\n\n")
                outputFile.write("-----------------------------------------------------\n\n")