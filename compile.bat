@CALL ./.venv/Scripts/activate.bat

pyinstaller --onedir --noconsole --icon icon.ico --clean ^
 --exclude-module PySide6.QtBluetooth ^
 --exclude-module PySide6.QtMultimedia ^
 --exclude-module PySide6.QtNfc ^
 --exclude-module PySide6.QtNetwork ^
 --exclude-module PySide6.QtWebEngineCore ^
 --exclude-module PySide6.QtWebEngineWidgets ^
 --exclude-module PySide6.QtWebChannel ^
 --exclude-module PySide6.Qt3DAnimation ^
 --exclude-module PySide6.Qt3DRender ^
 --exclude-module PySide6.QtLocation ^
 --exclude-module PySide6.QtPositioning ^
 --exclude-module PySide6.QtSensors ^
 PcsCheck.py

del dist\PcsCheck\_internal\PySide6\opengl32sw.dll
del dist\PcsCheck\_internal\PySide6\Qt6Network.dll
del dist\PcsCheck\_internal\PySide6\Qt6Pdf.dll
del dist\PcsCheck\_internal\PySide6\Qt6Qml.dll
del dist\PcsCheck\_internal\PySide6\Qt6QmlModels.dll
del dist\PcsCheck\_internal\PySide6\Qt6Quick.dll
del dist\PcsCheck\_internal\PySide6\Qt6Svg.dll
rmdir /q /s dist\PcsCheck\_internal\PySide6\translations

