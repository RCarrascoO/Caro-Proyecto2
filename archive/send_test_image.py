import json
import time
from io import BytesIO


print('Este archivo fue movido a tools/send_test_image.py')
print('Usa: python tools/send_test_image.py desde la raíz del proyecto (después de activar .venv)')


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
