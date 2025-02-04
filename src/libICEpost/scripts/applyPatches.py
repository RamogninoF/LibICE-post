import sys
import subprocess
import os
import platform

def patchPackages(packages:list[str], patches:list[str]) -> None:
    """
    Patch the given packages with the corresponding patch files.
    
    Args:
        packages (list[str]): List of packages to patch
        patches (list[str]): List of patch files to use for patching
    """
    patchCount = 0
    for pack, patch in zip(packages, patches):
        print(f"Patching {pack}")
        result = subprocess.run([sys.executable, "-m", "pip", "show", pack], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error: package not found")
            continue

        # Get the package path
        lines = result.stdout.split("\n")
        path = None
        for line in lines:
            if line.startswith("Location:"):
                path = line.split(":",1)[1].strip()
                break

        if path is None:
            print(f"Error: package path not found")
            continue
        else:
            path = os.path.join(path,"PyFoam")
        
        if not os.path.isdir(path):
            print(f"Error: package path not found")
            continue
            
        print(f"Package path:", path)

        # Patch the package
        patchFile = os.path.join(os.path.dirname(__file__), "patch", patch)
        print(f"Patching {pack} package with:", patchFile)

        if not os.path.isfile(patchFile):
            print(f"Error: patch file not found")
            continue
        
        result = subprocess.run(["patch", "-d", path, "-p1", "-i", patchFile], capture_output=True, text=True)
        if result.returncode != 0:
            print("Error: Patching failed")
            print("Patch output:")
            for line in result.stdout.split("\n"):
                print("\t",line)
            for line in result.stderr.split("\n"):
                print("\t",line)
            continue

        print("Patch applied successfully")
        
        #Try importing the patched package
        print("Checking import...", end="")
        try:
            __import__(pack)
        except Exception as e:
            print()
            print(f"Error: Importing patched package failed")
            print(e)
            continue
        print(" OK")
        
        print(f"Package {pack} patched successfully")
        patchCount += 1

    print(f"Succesfully patched {patchCount} packages out of {len(packages)}")
    

packages = [{"pack":"PyFoam", "OS":"Windows", "patch":"PyFoam.patch"}]
def main():
    for p in packages:
        if platform.system() == p["OS"]:
            patchPackages([p["pack"]], [p["patch"]])
            
if __name__ == "__main__":
    main()