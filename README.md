# messenger
Analysis tools for Facebook Messenger data.

## Installation
1. [Install](https://docs.pipenv.org/en/latest/install/#installing-pipenv)) the `pipenv` command.
2. Grab dependencies by running `pipenv install` in the repository root.
3. [Download](https://facebook.com/dyi) your Facebook dump in JSON format.
4. Place the `messages` directory from the dump in the repository root.

## Usage
1. Execute `run.sh` to launch Jupyter Notebook with dependencies loaded.
2. Open `notebooks/Setup.ipynb` to get started. (The other notebooks assume that you've completed
   the setup.)

## Development
1. To use the VS Code workspace template, it's useful for the virtualenv to be installed in the same
   directory as the repo. The corresponding install command is
   `PIPENV_VENV_IN_PROJECT=true pipenv install --dev`. Note the `--dev` suffix to get
   auto-formatting and other useful dev dependencies.
2. Execute `setup.sh` to install some useful Git hooks (e.g. stripping Jupyter notebooks of their
   output when you stage changes).
