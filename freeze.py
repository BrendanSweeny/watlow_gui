import subprocess
subprocess.call(['pyinstaller', 'main.py', '-y', '--onefile', '--clean', \
                '--icon=icon.ico', '--paths', 'C:\\Python34\\Lib\\site-packages\\PyQt5\\', \
				'--paths', 'C:\\Python34\\Lib\\site-packages\\serial\\', \
				'--paths', 'C:\\Python34\\Lib\\site-packages\\crcmod\\'])

# The crcmod module needs to be changed to only import _crcfunpy not crcmod._crcfunpy on line 45-47.
# Otherwise, PyInstaller does not seem to handle the execution of crcmod properly and the compile exe
# will not start.