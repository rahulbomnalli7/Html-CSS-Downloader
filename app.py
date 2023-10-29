from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def get_external_css(soup, base_url):
    css_links = []
    for link in soup.find_all("link", rel="stylesheet"):
        href = link.get("href")
        if href:
            css_url = href if href.startswith("http") else base_url + href
            css_links.append(css_url)
    return css_links

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_code', methods=['POST'])
def get_code():
    url = request.form['url']
    try:
        response = requests.get(url)
        if response.status_code == 200:
            content = response.text
            soup = BeautifulSoup(content, 'html.parser')
            html_code = soup.prettify()
            base_url = response.url

            # Fetch external CSS files
            css_links = get_external_css(soup, base_url)
            css_code = ""
            for css_url in css_links:
                css_response = requests.get(css_url)
                if css_response.status_code == 200:
                    css_code += f"/* CSS from {css_url} */\n" + css_response.text + "\n"

            return render_template('result.html', html_code=html_code, css_code=css_code)
        else:
            return "Failed to fetch the URL"
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run(debug=True)
