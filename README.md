# libICEpost

Postprocessing of data sampled from internal combustion engines (Experimental, 1D/0D (Gasdyn/GT-Power), 3D (LibICE-OpenFOAM/commercial codes), etc.)

## Installation

### Requirements

#### <img src=https://img.icons8.com/fluent/512/anaconda--v2.png width="13" height="13" /> Conda

It is required to use [Anaconda](https://www.anaconda.com/) python environment manager to use the library, so that the correct python version can be used in a dedicated environment. Currently working on python version 3.11.4.

> [!IMPORTANT]  
> When you install conda (eg. `C:\Users\your_name\anaconda3`), go in the installation directory, open a Windows terminal in that folder and execute the script:
>```bash
>Scripts\conda.exe init
>```

Open a new terminal in the folder and execute the following line:

```bash
conda install python==3.11
```
to install Python 3.11, which is required.
#### <img src=https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Visual_Studio_Code_1.35_icon.svg/512px-Visual_Studio_Code_1.35_icon.svg.png width="13" height="13"/> Visual Studio Code
Installation of [Visual Studio Code](https://code.visualstudio.com) (VS Code) is suggested. Follow the instructions to install the program. The following extension for Python has to be installed [Python Extension Pack](https://marketplace.visualstudio.com/items?itemName=donjayamanne.python-extension-pack). 

> [!NOTE]
> In VS Code the Python interpreter has to be selected. To do so, use `Ctrl+Maiusc+P`, search for `Python: Select Interpreter` and then select the available Python interpreter.

#### <img src=https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Git_icon.svg/2048px-Git_icon.svg.png  width="13" height="13"/> GIT
[GIT](https://git-scm.com/downloads/win) is necessary to download the repository. Follow the instructions to install the program. No further action are necessary.

### Downloading and installing the source code of LibICEpost

#### Download

In order to download the source code of `libICEpost` proceed as follow:  
1. Create a new folder in your `C:\Users\your_name` repository called `LibICE_repo`, where the various libraries will be stored;
2. In that folder (`LibICE_repo`), create another folder called `LibICE_post`;
3. Now open VS Code and with the `Open Folder` command, under the `File` tab open the folder you just created;
4. You should find yourself in VS Code with the `Explorer` bar on the left that has the name of the folder you created as title.

![screenshot](./docs/imagesForMd/First_Explorer.png)

> [!IMPORTANT]  
> Only for Windows user  
> Open `Setting` (shortcut `Ctrl+,`), and input in the search bar:  
> ```bash
> select default profile
> ```
> Dind and select the Command Prompt as **Default Profile**, you should see a similar result as reported here:
>> **Terminal > Integrated > Default Profile: Windows**  
>> The default terminal profile on Windows.  
>> Command Prompt

Now open a new terminal with `Ctrl+shitf+ò` or the `New Terminal` command from the `Terminal` menu. A window on the bottom of VS Code should have appeared.  
In the terminal, copy the following command to download the repository.

```bash
git clone https://github.com/RamogninoF/LibICE-post.git
```

You should now see in the explorer bar that a new `LIBICE-POST` tab has appeared, like so

![screenshot](./docs/imagesForMd/Second_Explorer.png)

#### Installing `libICEpost`

Now that `libICEPost` is downloaded, it has to be installed. In the terminal insert the following:

```bash
conda activate
cd LibICE-post
pip install . -e
```

Suggested to run `pip install` with `-e` option to install in editable mode, so that the changes are detected when pulling from the repository. You can choose not to put the `-e` option if you want.

It might happen that spyder or VS Code cannot access the module when installed in editable mode (`ImportError: module libICEpost not found`). If so, install it with `editable_mode=strict` (highly suggested):

```bash
pip install -e . --config-settings editable_mode=strict
```

Follow the instruction on the terminal and you should see the following line as a result.

```bash
Successfully installed libICEpost-0.9.7
```

## Usage

Now that `libICEpost` is installed, you can start to use it. To do so, under [`LibICE-post\tutorials\sparkIgnition`](./tutorials/sparkIgnition) you find a simple case intended to be used as base to understand the usage of this tool. Please duplicate the `sparkIgnition` folder in another location of your choice and the open that folder in VS Code. You should find yourself in this image.

![screenshot](./docs/imagesForMd/Tutorial_1.png)

### Setting the `dictionaries`

In the [`dictionaries`](./tutorials/sparkIgnition/dictionaries) folder you find four different Python scripts that will be used to compose the dictionary used by the post-processing tool. In particular these are:
- [`combustionProperties.py`](./tutorials/sparkIgnition/dictionaries/combustionProperties.py), used to specify the initial mixture of the charge trapped inside the cylinder;
-  [`dataDict.py`](./tutorials/sparkIgnition/dictionaries/dataDict.py), used to determine the pre-processing of the data that will be used in the tool;
- [`thermophysicalProperties.py`](./tutorials/sparkIgnition/dictionaries/thermophysicalProperties.py) used to choose the models to compute the various thermodynamic quantities;
- [`controlDict.py`](./tutorials/sparkIgnition/dictionaries/controlDict.py), acts as wrapper of the previous three files and allows the specification of engine-specific features and the crank angle period of interest to be processed.

The user is highly encouraged to read and understand each of these files as they greatly influence the results of the post-processing.

Additional documentation will be provided in later releases.

### Including the `data`

The [`data`](./tutorials/sparkIgnition/data) folder contains the experimental/simulated data that will be imported by the tool to be processed. The minimum requirement is to have a in-cylinder pressure file (in this case the `p.cyl` file). It is not necessary that your data is formatted in the same way as the one in the tutorial case. You can specify the reading of a given format in the `dataDict.py` script. In the proposed case the reading of pressure is performed as follow in `dataDict.py`:

```Python
#Pressure (mandatory)
"p":\ #specify how the variables will be called in runtime
{
    #The format of the data to load
    "format":"file",    #Retrieve from file
    
    #The parameters to use
    "data":
    {
        #Name of the file
        "fileName":"p.Cyl",
        
        #Options to apply (scaling, shifting, etc.)
        "opts":\
            {
                #"delimiter":",",   #Delimiter in file, in this case there was no delimiter !
                # "varScale":1.0,   #Scaling variable
                # "varOff":0.0,     #Offset to variable
                # "CAscale":1.0,    #Scaling CA
                # "CAoff":0.0,      #Offset to CA
            }
    }
},
```

As specified before, the pressure is the only mandatory data needed as import. However, other quantities can and have to specified, such as the mass at IVC, the wall temperatures and others. The user can decide to specify any variable of interest by reading those from files, by considering them constant or by defining a specific function.

### Running the `main.py` script

After having set-up the files in the [`dictionaries`](./tutorials/sparkIgnition/dictionaries) folder and having made sure to include in the [`data`](./tutorials/sparkIgnition/data) folder the required quantities, you can open the `main.py` file in which you'll find the main script to postprocess the data.

The `main.py` script is mainly divided of two parts: data processing and post-processing. The former is composed of the loading of the model from the various dictionaries stored in the [`dictionaries`](./tutorials/sparkIgnition/dictionaries)directory, plus the call to the processing of the data.

```python
#Load the model
model = loadModel("./dictionaries/")

#Process the data in the engine model
model.process()
```

The following part of the code is intended to post-process the data that was processed by the tool. Here you can define some specific plots you want to see like a p-V diagram, which is already impelemented as part of the `model` class:

```python
#Plotting p-V diagram
ax = model.plotPV(label="CFD", timingsParams={"markersize":120, "linewidth":2})
plt.tight_layout()
```

It is possible to produce user-defined plots with the `model.data.plot()` function, like done here:
```python
#Plotting ROHR vs CA diagram
model.data.plot(x = "CA", y="ROHR", label="CFD", legend=True, c="k", figsize=(10,10))
plt.xlabel("Crank angle [CA]")
plt.ylabel("Rate of heat release [J/deg]")
plt.tight_layout()
```

You can change the `x` and `y` axes as you wish, paying attention that they are defined in the `model.data` structure.

To launch the script use the `Run Python File` command on the upper-right corner.

![screenshot](./docs/imagesForMd/Tutorial_2.png)

A terminal should open and two plots should appear.

From this simple case setup you can explore and expand to run the postprocess you wish. A brief documentation (that will be expanded) is reported in each of the files under the [`dictionaries`](./tutorials/sparkIgnition/dictionaries) folder. 

In the [`data`](./tutorials/sparkIgnition/data) folder, the data that has to be processed has to be included.

Additional documentation can be found in [`references`](./docs/references)

## Troubleshooting

Sometimes, for Windows user, when reopening VS Code the following orange warning may appear in the terminal tab

![screenshot](./docs/imagesForMd/ErrorRelaunch.png)

If this happens, please click on `Relaunch Terminal` with hovering (not clicking) on `cmd`. The next time you reopen the folder it should not happen again.

### Installation
- **Ubuntu 18.04**: Installation may fail when compiling CANTERA due to missing BLAS library. If so, install an older version of CANTERA:
```bash
pip install cantera==3.0.0
```
## Installing from PyPI (_skip for ICEGroup_)

Installation from PyPI repositories (not up-to-date):

```bash
pip install libICEpost
```

## Contributing

- Federico Ramognino - Code development (all of it)
- Alberto Ballerini - Testing and documentation

## License

`libICEpost` was created by Federico Ramognino. It is licensed under the terms of the MIT license.

## Credits

`libICEpost` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
