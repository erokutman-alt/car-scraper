from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/scrape', methods=['GET'])
def scrape():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL parametresi gerekli'}), 400

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')

        # Sahibinden / Otomobil ilan yapısına göre css selector'lar
        # Sayfa yapısına göre buradaki class isimleri filtrelenebilir
        fiyat = soup.select_one('.classifiedInfo h3')
        
        # Genel bilgi listesini alma (KM, Yıl vb.)
        info_list = {}
        for li in soup.select('.classifiedInfoList li'):
            label = li.select_one('strong')
            value = li.select_one('span')
            if label and value:
                info_list[label.text.strip()] = value.text.strip()

        # İlan Açıklaması
        aciklama = soup.select_one('#classifiedDescription')

        data = {
            'status': 'success',
            'fiyat': fiyat.text.strip() if fiyat else 'Bulunamadı',
            'km': info_list.get('KM', 'Bulunamadı'),
            'yil': info_list.get('Yıl', 'Bulunamadı'),
            'marka_model': info_list.get('Model', 'Bulunamadı'),
            'aciklama': aciklama.text.strip() if aciklama else 'Bulunamadı',
            'tum_detaylar': info_list
        }
        return jsonify(data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)