from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

SCRAPER_API_KEY = 'a54a4eb03063ab0aa96c46f2b5c3def'

@app.route('/', methods=['GET'])
@app.route('/scrape', methods=['GET'])
def scrape():
    target_url = request.args.get('url')
    if not target_url:
        return jsonify({'status': 'error', 'message': 'URL gerekli'}), 400

    try:
        # Türkiye lokasyonlu premium residential IP ve JavaScript rendering kullanımı
        proxy_url = (
            f'http://api.scraperapi.com?'
            f'api_key={SCRAPER_API_KEY}&'
            f'url={target_url}&'
            f'render=true&'
            f'country_code=tr&'
            f'premium=true'
        )
        
        response = requests.get(proxy_url, timeout=60)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Fiyat alma
        fiyat_elem = (
            soup.select_one('.classifiedInfo h3') or 
            soup.select_one('.classified-price-container') or 
            soup.select_one('.price-value')
        )
        fiyat = fiyat_elem.text.strip() if fiyat_elem else 'Bulunamadı'

        # Detay listesi (KM, Yıl vb.)
        info_list = {}
        rows = soup.select('.classifiedInfoList li') or soup.select('.classified-props-list li')
        
        for li in rows:
            label = li.select_one('strong') or li.select_one('b')
            value = li.select_one('span') or li.select_one('a')
            if label and value:
                key = label.text.strip().replace(':', '')
                val = value.text.strip()
                info_list[key] = val

        # İlan Açıklaması
        aciklama_elem = (
            soup.select_one('#classifiedDescription') or 
            soup.select_one('.classifiedDescription')
        )
        aciklama = aciklama_elem.text.strip() if aciklama_elem else 'Bulunamadı'

        return jsonify({
            'status': 'success',
            'fiyat': fiyat,
            'km': info_list.get('KM', info_list.get('Km', 'Bulunamadı')),
            'yil': info_list.get('Yıl', info_list.get('Model Yılı', 'Bulunamadı')),
            'marka_model': info_list.get('Model', info_list.get('Seri', 'Bulunamadı')),
            'aciklama': aciklama[:500] if aciklama != 'Bulunamadı' else aciklama,
            'tum_detaylar': info_list
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
