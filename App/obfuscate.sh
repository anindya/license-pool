cd ..
pyarmor obfuscate --recursive App/app.py
rm -rf dist/pytransform
cp -r pytransform dist/pytransform
cp App/Dockerfile dist/
cp App/requirements.txt dist/
