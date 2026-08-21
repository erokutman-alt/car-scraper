from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

SCRAPER_API_KEY = 'a54a4eb03063ab0aa96c46f2b5c3def'

@app.route('/', methods=['GET'])
@app.route('/scrape', methods=['GET'])
def scrape():
    target_url = request.args.get('url')
    if not target_url:
        return jsonify({'status': 'error', 'message': 'URL gerekli'}), 400

    try:
        proxy_url = f'http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={target_url}&render=true'
        
        response = requests.get(proxy_url, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Fiyat çekme
        fiyat_elem = soup.select_one('.classifiedInfo h3')
        fiyat = fiyat_elem.text.strip() if fiyat_elem else 'Bulunamadı'

        # Detay listesi (KM, Yıl vb.)
        info_list = {}
        for li in soup.select('.classifiedInfoList li'):
            label = li.select_one('strong')
            value = li.select_one('span')
            if label and value:
                info_list[label.text.strip()] = value.text.strip()

        # İlan Açıklaması
        aciklama_elem = soup.select_one('#classifiedDescription')
        aciklama = aciklama_elem.text.strip() if aciklama_elem else 'Bulunamadı'

        return jsonify({
            'status': 'success',
            'fiyat': fiyat,
            'km': info_list.get('KM', 'Bulunamadı'),
            'yil': info_list.get('Yıl', 'Bulunamadı'),
            'marka_model': info_list.get('Model', 'Bulunamadı'),
            'aciklama': aciklama,
            'tum_detaylar': info_list
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
