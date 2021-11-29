# Schoology-Assistant
A python script that uses Schoolopy module to retreive student grades displalys them and also graphs them

# Notes:
opening matplotlib in a pyvenv is diffuclut due to gui dependancies. So, I found documentation that said to add a file to the bin in the env.
the file is called `frameworkpython` containing:
```#!/bin/bash

# what real Python executable to use
PYVER=3.8
PATHTOPYTHON=PATH_TO_PYTHON_FOLDER_IN_THE_ENV
PYTHON=${PATHTOPYTHON}python${PYVER}

# find the root of the virtualenv, it should be the parent of the dir this script is in
ENV=`$PYTHON -c "import os; print(os.path.abspath(os.path.join(os.path.dirname(\"$0\"), '..')))"``

# now run Python with the virtualenv set as Python's HOME
export PYTHONHOME=$ENV
exec $PYTHON "$@"
```

schoolopy has to be installed manually (`pip3 install -e .`) becuase current installation is missing a function called `get_user_grades_by_section()`

`
