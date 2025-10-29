Herramientas auxiliares para pruebas: publish_test, sniff_collect, sniff_mqtt, send_test_image

Ejecuta estas herramientas desde el entorno virtual en la raíz del proyecto:

PowerShell (ejemplo):

py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python tools\publish_test.py

