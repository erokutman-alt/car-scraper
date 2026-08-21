from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import json
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
        # Mobil UA ve Keep-Headers ile doğrudan istek
        proxy_url = f'http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={target_url}&keep_headers=true'
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
            'Accept-Language': 'tr-TR,tr;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }

        response = requests.get(proxy_url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. Yöntem: HTML içindeki gömülü JSON-LD verisini yakalama (En Garanti Yöntem)
        json_ld = soup.find('script', type='application/ld+json')
        if json_ld and json_ld.string:
            try:
                data_json = json.loads(json_ld.string)
                return jsonify({
                    'status': 'success',
                    'fiyat': str(data_json.get('offers', {}).get('price', 'Bulunamadı')) + ' TL',
                    'marka_model': data_json.get('name', 'Bulunamadı'),
                    'aciklama': data_json.get('description', 'Bulunamadı'),
                    'kaynak': 'JSON-LD Data',
                    'tum_detaylar': data_json
                }), 200
            except Exception:
                pass

        # 2. Yöntem: Klasik HTML Parsing (Yedek Plan)
        fiyat_elem = soup.select_one('.classifiedInfo h3') or soup.select_one('.price')
        fiyat = fiyat_elem.text.strip() if fiyat_elem else 'Bulunamadı'

        info_list = {}
        for li in soup.select('.classifiedInfoList li'):
            label = li.select_one('strong')
            value = li.select_one('span')
            if label and value:
                info_list[label.text.strip().replace(':', '')] = value.text.strip()

        aciklama_elem = soup.select_one('#classifiedDescription')
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
