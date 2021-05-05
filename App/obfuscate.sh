pyarmor obfuscate --recursive App/app.py
cp App/Dockerfile dist/
cp App/requirements.txt dist/
#rm -rf dist/pytransform
#cp -r pytransform dist/pytransform
