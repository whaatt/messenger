# Strip output of Jupyter notebooks on commit.
# Ensure you have some `pip` installed globally.
pip install --upgrade nbstripout
git config filter.nbstripout.clean 'nbstripout'
git config filter.nbstripout.smudge cat
git config filter.nbstripout.required true
git config diff.ipynb.textconv 'nbstripout -t'

# Ignore changes to `constants.py`.
git update-index --assume-unchanged constants.py

# If you ever need to edit `constants.py`, run this first so that your changes aren't ignored.
# git update-index --no-assume-unchanged constants.py
