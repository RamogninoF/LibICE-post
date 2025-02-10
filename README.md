# libICEpost

Postprocessing of data sampled from internal combustion engines (Experimental, 1D/0D (Gasdyn/GT-Power), 3D (LibICE-OpenFOAM/commercial codes), etc.)

## Installation

### Requirements

#### Conda

Suggested to use [anaconda](https://www.anaconda.com/) python environment manager to use the library, so that the correct python version can be used in a dedicated environment. Currently working on python version 3.11.4.

> [!NOTE]  
> When you install conda (eg. `C:\Users\your_name\anaconda3`), go in the installation directory, open a Windows terminal in that folder and execute the script:

```bash
Scripts\conda.exe init
```

#### Visual Studio Code
Visual Studio Code (VS Code) is suggested, install it from [this link](https://code.visualstudio.com). No further action are necessary.

#### GIT
GIT is necessary, install it from [this link](https://git-scm.com/downloads/win). Execute the installation program. No further action are necessary.

### Installing from PyPI (__skip for ICEGroup__)

Installation from PyPI repositories (not up-to-date):
```bash
pip install libICEpost
```

### Downloading and installing the source code of LibICEpost

#### Download

In order to download the source code of LibICEpost proceed as follow:  
1. Create a folder in your `C:\Users\your_name` folder called `LibICE_repo`, where the various libraries will be stored
2. In that folder, create another folder called `LibICE-post`;
3. Now open VS Code and with the `Open Folder` command open the folder you created;
4. You should find yourself in VS Code with the `Explorer` tab on the left that has as title the name of the folder you created.

Now open a new terminal with `Ctrl+shitf+ò` or the `New Terminal` command from the menu. A window on the bottom of VS Code should appear.  
In the terminal, copy the following command to download the repository

```bash
git clone https://github.com/RamogninoF/LibICE-post.git
```

#### Installing LibICEPost

In the terminal insert the following:

```bash
cd LibICE-post
pip install .
```

Suggested to run `pip install` with `-e` option to install in editable mode, so that the changes are detected when pulling from the repository:

```bash
pip install -e .
```

It might happen that spyder or VS Code cannot access the module when installed in editable mode (`ImportError: module libICEpost not found`). If so, install it with `editable_mode=strict` (highly suggested):

```bash
pip install -e . --config-settings editable_mode=strict
```

## Usage

- TODO

Interactive documentation avaliable at [this page](https://libice-post.readthedocs.io/en/latest/).

## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`libICEpost` was created by Federico Ramognino. It is licensed under the terms of the MIT license.

## Credits

`libICEpost` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
