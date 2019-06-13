# Strip output of Jupyter notebooks on commit.
git config filter.nbstripout.clean 'python -m nbstripout'
git config filter.nbstripout.smudge cat
git config filter.nbstripout.required true
git config diff.ipynb.textconv 'python -m nbstripout -t'
