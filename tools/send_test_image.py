import json
import time
from io import BytesIO

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import requests


def make_image():
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot([1, 2, 3, 4], [10, 5, 8, 12], marker='o')
    ax.set_title('Imagen de prueba desde send_test_image')
    ax.grid(True)
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf


def send_photo(token, chat_id, img_buf):
    url = f'https://api.telegram.org/bot{token}/sendPhoto'
    files = {'photo': ('test.png', img_buf, 'image/png')}
    data = {'chat_id': str(chat_id), 'caption': 'Prueba de envío de imagen'}
    resp = requests.post(url, data=data, files=files, timeout=20)
    resp.raise_for_status()
    return resp.json()


if __name__ == '__main__':
    print('Este script está ahora en tools/. Ejecuta desde el entorno virtual con libs instaladas.')
