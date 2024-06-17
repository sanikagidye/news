from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import datetime
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
import urllib.parse

# Initialize NLTK tools
nltk.download('vader_lexicon')

app = Flask(__name__)

PUBLICATIONS = {
    'Economic Times': 'https://economictimes.indiatimes.com',
    'Mint': 'https://www.livemint.com/',
    'Moneycontrol': 'https://www.moneycontrol.com/'
}

def fetch_news(publication, company, start_date, end_date):
    if publication == 'Economic Times':
        url = f"https://economictimes.indiatimes.com/topic/{urllib.parse.quote(company)}"
    elif publication == 'Mint':
        url = f"https://www.livemint.com/Search/Link/Keyword/{urllib.parse.quote(company)}"
    elif publication == 'Moneycontrol':
        url = f"https://www.moneycontrol.com/news/tags/{urllib.parse.quote(company)}.html"
    
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    base_url = PUBLICATIONS[publication]
    
    if publication == 'Economic Times':
        for a_tag in soup.find_all('a', href=True):
            if company.lower() in a_tag.text.lower():
                article_url = urllib.parse.urljoin(base_url, a_tag['href'])
                links.append((article_url, a_tag.text))
    elif publication == 'Mint':
        for a_tag in soup.find_all('a', href=True):
            if company.lower() in a_tag.text.lower():
                article_url = urllib.parse.urljoin(base_url, a_tag['href'])
                links.append((article_url, a_tag.text))
    elif publication == 'Moneycontrol':
        for div_tag in soup.find_all('div', class_='clearfix'):
            a_tag = div_tag.find('a', href=True)
            if a_tag and company.lower() in a_tag.text.lower():
                article_url = urllib.parse.urljoin(base_url, a_tag['href'])
                links.append((article_url, a_tag.text))

    return links

def analyze_sentiment(title):
    sia = SentimentIntensityAnalyzer()
    sentiment_score = sia.polarity_scores(title)['compound']
    if sentiment_score > 0.05:
        return 'Positive'
    elif sentiment_score < -0.05:
        return 'Negative'
    else:
        return 'Neutral'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        company = request.form['company']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

        report = []
        for publication in PUBLICATIONS:
            news_links = fetch_news(publication, company, start_date, end_date)
            for link, title in news_links:
                sentiment = analyze_sentiment(title)
                report.append({'publication': publication, 'title': title, 'link': link, 'sentiment': sentiment})

        return render_template('index.html', report=report, company=company)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
