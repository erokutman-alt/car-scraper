from flask import Flask, request, jsonify
import cloudscraper
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/', methods=['GET'])
@app.route('/scrape', methods=['GET'])
def scrape():
    url = request.args.get('url')
    if not url:
        return jsonify({'status': 'error', 'message': 'URL gerekli'}), 400

    try:
        # Cloudflare korumasını aşan istemci
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False
            }
        )
        
        response = scraper.get(url, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Fiyat çekme
        fiyat_elem = soup.select_one('.classifiedInfo h3')
        fiyat = fiyat_elem.text.strip() if fiyat_elem else 'Bulunamadı'

        # Liste detayları (KM, Yıl vb.)
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
