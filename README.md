# messenger
Analysis tools for Facebook Messenger data.

## Installation
1. Run `brew install pipenv` (or your system's
   [equivalent](https://docs.pipenv.org/en/latest/install/#installing-pipenv)).
2. Install the Python virtualenv by running `PIPENV_VENV_IN_PROJECT=true pipenv install` in the
   top-level of this repo. The environment variable forces `pipenv` to put the environment folder in
   your project workspace.
3. Download your chat dump in JSON format from Facebook.
4. Place the `messages` directory from the dump in the top-level of this repo.
5. Run `pipenv shell` to launch a virtual shell.
6. Run `pipenv run jupyter notebook` to launch Jupyter Notebook.
7. Open `Setup.ipynb` to get started.
