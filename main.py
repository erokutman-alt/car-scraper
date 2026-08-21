from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/', methods=['GET'])
@app.route('/scrape', methods=['GET'])
def scrape():
    url = request.args.get('url')
    if not url:
        return jsonify({'status': 'error', 'message': 'URL gerekli'}), 400

    try:
        with sync_playwright() as p:
            # Bot tespitini zorlaştıran sanal tarayıcı başlatma
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            page.goto(url, timeout=15000, wait_until='domcontentloaded')
            page.wait_for_timeout(3000) # Sayfanın ve JavaScript'in yüklenmesi için kısa bekleme
            
            html_content = page.content()
            browser.close()

        soup = BeautifulSoup(html_content, 'html.parser')

        # Fiyat alma
        fiyat_elem = soup.select_one('.classifiedInfo h3')
        fiyat = fiyat_elem.text.strip() if fiyat_elem else 'Bulunamadı'

        # Detay listesi (KM, Yıl vb.)
        info_list = {}
        for li in soup.select('.classifiedInfoList li'):
            label = li.select_one('strong')
            value = li.select_one('span')
            if label and value:
                info_list[label.text.strip()] = value.text.strip()

        # Açıklama
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
