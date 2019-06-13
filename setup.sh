# Strip output of Jupyter notebooks on commit.
pip install --upgrade nbstripout
git config filter.nbstripout.clean 'nbstripout'
git config filter.nbstripout.smudge cat
git config filter.nbstripout.required true
git config diff.ipynb.textconv 'nbstripout -t'
git update-index --assume-unchanged constants.py
