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
        # render=true ve render_sdk=true ile JavaScript'in tam yüklenmesini sağlıyoruz
        proxy_url = f'http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={target_url}&render=true'
        
        response = requests.get(proxy_url, timeout=60)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Alternatif selector'lar ile Fiyat Çekme
        fiyat_elem = (
            soup.select_one('.classifiedInfo h3') or 
            soup.select_one('.classified-price-container') or 
            soup.select_one('.price-value') or
            soup.find(text=re.compile(r'TL'))
        )
        fiyat = fiyat_elem.text.strip() if fiyat_elem else 'Bulunamadı'

        # Liste Detayları (KM, Yıl, Marka/Model)
        info_list = {}
        # Standart liste arama
        rows = soup.select('.classifiedInfoList li') or soup.select('.classified-props-list li') or soup.select('ul.info-list li')
        
        for li in rows:
            label = li.select_one('strong') or li.select_one('b') or li.select_one('.title')
            value = li.select_one('span') or li.select_one('a') or li.select_one('.value')
            if label and value:
                key = label.text.strip().replace(':', '')
                val = value.text.strip()
                info_list[key] = val

        # İlan Açıklaması
        aciklama_elem = (
            soup.select_one('#classifiedDescription') or 
            soup.select_one('.classifiedDescription') or 
            soup.select_one('.uiBoxContainer')
        )
        aciklama = aciklama_elem.text.strip() if aciklama_elem else 'Bulunamadı'

        return jsonify({
            'status': 'success',
            'fiyat': fiyat,
            'km': info_list.get('KM', info_list.get('Km', 'Bulunamadı')),
            'yil': info_list.get('Yıl', info_list.get('Model Yılı', 'Bulunamadı')),
            'marka_model': info_list.get('Model', info_list.get('Seri', 'Bulunamadı')),
            'aciklama': aciklama[:500] if aciklama != 'Bulunamadı' else aciklama, # Temiz görünüm için ilk 500 karakter
            'tum_detaylar': info_list
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
