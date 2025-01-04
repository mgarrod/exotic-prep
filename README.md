# exotic-prep

Prerequisite:
1. FITs images have been reviewed
2. Set values in config.ini
3. EXOTIC is installed in a MiniConda env

##### Windows: Add at the end of ```C:\Users\{USERNAME}\miniconda3\Scripts\activate.bat```

```doskey exotic-prep=python "C:\Users\\{USERNAME}\exotic-prep\exotic-prep.py"```

```doskey update-exotic-prep=cd "C:\Users\\{USERNAME}\exotic-prep" $T git pull```

```conda activate exotic_env```

Steps:
1. Run in the same virtual env as EXOTIC - ```python exotic-prep.py```
