# libICEpost

Postprocessing of data sampled from internal combustion engines (Experimental, 1D/0D (Gasdyn/GT-Power), 3D (LibICE-OpenFOAM/commercial codes), etc.)

## Installation
Suggested to use [anaconda](https://www.anaconda.com/) python environment manager to use the library, so that the correct python version can be used in a dedicated environment. Currently working on python version 3.11.4.

Installation from PyPI repositories (not up-to-date):
```bash
$ pip install libICEpost
```

Installation from source code (suggested):
```bash
$ git clone https://github.com/RamogninoF/LibICE-post.git
$ cd LibICE-post
$ pip install .
```

Suggested to run `pip install` with `-e` option to install in editable mode, so that the changes are detected when pulling from the repository:

```bash
$ pip install -e .
```

It might appen that spyder or VS Code cannot access the module when installed in editable mode (`ImportError: module libICEpost not found`). If so, install it with `editable_mode=strict`:

```bash
$ pip install -e . --config-settings editable_mode=strict
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
