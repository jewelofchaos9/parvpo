import requests
import redis
import os
import json
from flask import Flask, request

app = Flask(__name__)
conn = redis.Redis(
    host='redis',
    port=int(os.getenv('REDIS_PORT', '6379'))
)

def get_info(ip):
    """Хак для того чтобы хоть как то аггрегировать айпишники
    последний октет наверняка будет принадлежать одному провайдеру, поэтому просто кэшируем первые три байта айпишника, считаем что все норм"""
    masked_ip = ''.join(ip.split('.')[:-1])

    cached = conn.get(masked_ip)
    if cached is not None: 
        return json.loads(cached)

    ip_data = requests.get(f'https://json.geoiplookup.io/{ip}').json()

    temp = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={ip_data.get('latitude')}&longitude={ip_data.get('longitude')}&hourly=temperature_2m").json()
    temp = temp.get('hourly').get('temperature_2m')[0]
    currency_rate = str(requests.get('https://open.er-api.com/v6/latest/USD').json()['rates'][ip_data['currency_code']]) + ip_data['currency_code']

    ans = {'weather': temp, 'usd price': currency_rate}
    conn.set(masked_ip, json.dumps(ans), ex=60*60)
    return ans


@app.route('/api/get_bar')
def get_bar():
    # let assume that remote_addr is literally remote
    ip = request.args.get(
        'ip',
        request.remote_addr
    )
    return get_info(ip)

def cache_warmer():
    with open('./ips.txt', 'r') as f:
        for l in f.readlines():
            try:
                get_info(l.strip())
            except:
                continue

if __name__ == "__main__":
    cache_warmer()
    app.run('0.0.0.0', 3232)
