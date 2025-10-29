import time
import random
import paho.mqtt.publish as publish

BROKER = '127.0.0.1'
TOPIC = 'DATA/MP'

def main():
    for i in range(10):
        mp01 = round(random.uniform(0,5),2)
        mp25 = round(random.uniform(5,40),2)
        mp10 = round(random.uniform(10,50),2)
        temp = round(random.uniform(15,30),2)
        hr = round(random.uniform(30,80),2)
        payload = f"{mp01},{mp25},{mp10},{temp},{hr}"
        publish.single(TOPIC, payload, hostname=BROKER)
        print(f"Published {i+1}/10 -> {payload}")
        time.sleep(1)

if __name__ == '__main__':
    main()
