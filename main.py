from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/', methods=['GET'])
@app.route('/scrape', methods=['GET'])
def scrape():
    url = request.args.get('url')
    if not url:
        return jsonify({
            'status': 'error',
            'message': 'Lütfen url parametresi gönderin. Örnek: /scrape?url=https://...'
        }), 400

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')

        # Fiyat çekme
        fiyat_elem = soup.select_one('.classifiedInfo h3')
        fiyat = fiyat_elem.text.strip() if fiyat_elem else 'Bulunamadı'

        # Liste bilgilerini (KM, Yıl vb.) çekme
        info_list = {}
        for li in soup.select('.classifiedInfoList li'):
            label = li.select_one('strong')
            value = li.select_one('span')
            if label and value:
                info_list[label.text.strip()] = value.text.strip()

        # İlan Açıklaması
        aciklama_elem = soup.select_one('#classifiedDescription')
        aciklama = aciklama_elem.text.strip() if aciklama_elem else 'Bulunamadı'

        data = {
            'status': 'success',
            'fiyat': fiyat,
            'km': info_list.get('KM', 'Bulunamadı'),
            'yil': info_list.get('Yıl', 'Bulunamadı'),
            'marka_model': info_list.get('Model', 'Bulunamadı'),
            'aciklama': aciklama,
            'tum_detaylar': info_list
        }
        return jsonify(data), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
