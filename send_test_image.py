import json
import time
from io import BytesIO

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import requests


def load_cfg(path='client1.json'):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


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
    print(resp.status_code)
    print(resp.text)
    resp.raise_for_status()
    return resp.json()


def main():
    cfg = load_cfg('client1.json')
    token = cfg.get('bot_token')
    chat_id = cfg.get('chat_id')
    if not token or not chat_id:
        print('Faltan bot_token o chat_id en client1.json')
        return
    img = make_image()
    print('Enviando imagen a Telegram...')
    res = send_photo(token, chat_id, img)
    print('Resultado:', res.get('ok'))


if __name__ == '__main__':
    main()
