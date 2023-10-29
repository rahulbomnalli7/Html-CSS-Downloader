from flask import Flask, render_template, request, Response, send_file
import requests
from bs4 import BeautifulSoup
import csscompressor
import htmlmin
import tempfile
import os

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
            base_url = response.url

            # Fetch external CSS files
            css_links = get_external_css(soup, base_url)
            css_code = ""
            for css_url in css_links:
                css_response = requests.get(css_url)
                if css_response.status_code == 200:
                    css_code += f"/* CSS from {css_url} */\n" + css_response.text + "\n"

            # Minify HTML and CSS
            minified_html = htmlmin.minify(soup.prettify(), remove_comments=True)
            minified_css = csscompressor.compress(css_code)

            # Create temporary files for HTML and CSS
            with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix=".html") as html_file:
                html_file.write(minified_html)

            with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix=".css") as css_file:
                css_file.write(minified_css)

            # Get the file paths
            html_filepath = html_file.name
            css_filepath = css_file.name

            # Offer the HTML and CSS files for download
            return render_template('result.html', html_filepath=html_filepath, css_filepath=css_filepath)
        else:
            return "Failed to fetch the URL"
    except Exception as e:
        return f"An error occurred: {str(e)}"

@app.route('/download_html')
def download_html():
    html_filepath = request.args.get('filepath')
    return send_file(html_filepath, as_attachment=True)

@app.route('/download_css')
def download_css():
    css_filepath = request.args.get('filepath')
    return send_file(css_filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
