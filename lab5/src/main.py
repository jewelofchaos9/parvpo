from flask import Flask, request
import requests

app = Flask(__name__)



@app.route('/api/get_bar')
def get_bar():
    # let assume that remote_addr is literally remote
    ip = request.args.get(
        'ip',
        request.remote_addr
    )
    """Хак для того чтобы хоть как то аггрегировать айпишники
    последний октет наверняка будет принадлежать одному провайдеру, поэтому просто кэшируем первые три байта айпишника, считаем что все норм"""

    masked_ip = ''.join(ip.split('.')[:-1])
    

    ip_data = requests.get(f'https://json.geoiplookup.io/{ip}').json()

    temp = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={ip_data.get('latitude')}&longitude={ip_data.get('longitude')}&hourly=temperature_2m").json()
    temp = temp.get('hourly').get('temperature_2m')[0]
    currency_rate = str(requests.get('https://open.er-api.com/v6/latest/USD').json()['rates'][ip_data['currency_code']]) + ip_data['currency_code']

    return {'weather': temp, 'usd price': currency_rate}

if __name__ == "__main__":
    app.run('0.0.0.0', 3232)
