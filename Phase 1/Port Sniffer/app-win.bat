@echo off

:start

cls

cd venv/Scripts

.\activate

cd ../..

pip install -r requirement.txt

python ./app.py

pause
exit    