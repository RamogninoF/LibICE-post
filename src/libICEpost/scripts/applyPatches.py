import sys
import subprocess
import os
import platform

def patchPackage(pack:str, patch:str) -> None:
    """
    Patch the given packages with the corresponding patch files.
    
    Args:
        pack (str): Package to patch
        patch (str): Patch file to use for patching
    """
    patchCount = 0
    print(f"Patching {pack}")
    result = subprocess.run([sys.executable, "-m", "pip", "show", pack], capture_output=True, text=True)
    if result.returncode != 0:
        raise ValueError(f"package not found")

    # Get the package path
    lines = result.stdout.split("\n")
    path = None
    for line in lines:
        if line.startswith("Location:"):
            path = line.split(":",1)[1].strip()
            break

    if path is None:
        raise IOError(f"package path not found")
    else:
        path = os.path.join(path,"PyFoam")
    
    if not os.path.isdir(path):
        raise IOError(f"package path not found")
        
    print(f"Package path:", path)

    # Patch the package
    patchFile = os.path.join(os.path.dirname(__file__), "patch", patch)
    print(f"Patching {pack} package with:", patchFile)

    if not os.path.isfile(patchFile):
        raise IOError(f"patch file not found")
    
    result = subprocess.run(["patch", "-d", path, "-p1", "-i", patchFile], capture_output=True, text=True)
    if result.returncode != 0:
        out = "Patching failed\n"
        out += "Patch output:\n"
        for line in result.stdout.split("\n"):
            out += "\t" + line + "\n"
        for line in result.stderr.split("\n"):
            out += "\t" + line + "\n"
        raise RuntimeError(out)

    print("Patch applied successfully")
    
    #Try importing the patched package
    print("Checking import...", end="")
    try:
        __import__(pack)
    except Exception as e:
        print(" Failed")
        out = f"Importing patched package failed:\n{e}"
        raise RuntimeError(out)
    print(" OK")
    
    print(f"Package {pack} patched successfully")
    

packages = \
    [
        {"pack":"PyFoam", "OS":"Windows", "patch":"PyFoam.patch"},
        {"pack":"PyFoam", "OS":"Windows", "patch":"PyFoam2.patch"},
    ]
def main():
    for p in packages:
        count = 0
        tot = 0
        if platform.system() == p["OS"]:
            try:
                tot += 1
                patchPackage(p["pack"], p["patch"])
                count += 1
            except Exception as e:
                print(e)
        print("Successfully patched", count, "packages out of", tot)
            
if __name__ == "__main__":
    main()