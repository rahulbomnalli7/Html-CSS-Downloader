from flask import Flask, render_template, request, send_file
import requests
from bs4 import BeautifulSoup

app = Flask(__name__, static_folder='static')

def get_external_resources(soup, base_url):
    resource_links = {
        "css": [],
        "js": []
    }

    for link in soup.find_all("link", rel="stylesheet"):
        href = link.get("href")
        if href:
            css_url = href if href.startswith("http") else base_url + href
            resource_links["css"].append(css_url)

    for script in soup.find_all("script"):
        src = script.get("src")
        if src:
            js_url = src if src.startswith("http") else base_url + src
            resource_links["js"].append(js_url)

    return resource_links

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

            # Fetch external resources (CSS, JS)
            resource_links = get_external_resources(soup, base_url)
            css_code = ""
            js_code = ""

            for css_url in resource_links["css"]:
                css_response = requests.get(css_url)
                if css_response.status_code == 200:
                    css_code += f"/* CSS from {css_url} */\n" + css_response.text + "\n"

            for js_url in resource_links["js"]:
                js_response = requests.get(js_url)
                if js_response.status_code == 200:
                    js_code += f"/* JS from {js_url} */\n" + js_response.text + "\n"

            # Create HTML, CSS, and JS files
            html_file = f"{base_url.replace('/', '_').replace(':', '_')}.html"
            css_file = f"{base_url.replace('/', '_').replace(':', '_')}.css"
            js_file = f"{base_url.replace('/', '_').replace(':', '_')}.js"

            with open(html_file, 'w') as file:
                file.write(html_code)

            with open(css_file, 'w') as file:
                file.write(css_code)

            with open(js_file, 'w') as file:
                file.write(js_code)

            # Offer HTML, CSS, and JS files for download
            return render_template('result.html', html_file=html_file, css_file=css_file, js_file=js_file)
        else:
            return "Failed to fetch the URL"
    except Exception as e:
        return str(e)

# Define a route to download the files
@app.route('/download/<filename>')
def download(filename):
    if filename.endswith('.html'):
        return send_file(filename, as_attachment=True, download_name='downloaded.html')
    elif filename.endswith('.css'):
        return send_file(filename, as_attachment=True, download_name='downloaded.css')
    elif filename.endswith('.js'):
        return send_file(filename, as_attachment=True, download_name='downloaded.js')

if __name__ == '__main__':
    app.run(debug=True)
