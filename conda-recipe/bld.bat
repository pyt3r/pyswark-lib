"%PYTHON%" setup.py install --prefix="$PREFIX" --single-version-externally-managed --record=record.txt
if errorlevel 1 exit 1