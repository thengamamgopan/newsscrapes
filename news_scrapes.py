import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from fpdf import FPDF
import time
import random

class PDF(FPDF):
    def header(self):
        """Header with title"""
        self.set_font("Arial", style='B', size=16)
        self.cell(0, 10, "News ", ln=True, align='C')
        self.ln(5)

    def footer(self):
        """Footer with page number"""
        self.set_y(-15)
        self.set_font("Arial", size=10)
        self.cell(0, 10, f"Page {self.page_no()}", align='C')

    def add_news_tile(self, title, link, summary, source):
        """Adds a structured news tile"""
        self.set_font("Arial", style='B', size=12)
        self.cell(0, 8, title.encode('latin-1', 'replace').decode('latin-1'), ln=True, align='L')

        self.set_font("Arial", size=10)
        self.set_text_color(0, 0, 255)  # Blue color for link
        self.cell(0, 6, f"Source: {source} | Link: {link}", ln=True, align='L', link=link)

        self.set_text_color(0, 0, 0)  # Reset color
        self.set_font("Arial", size=10)
        self.multi_cell(0, 6, summary.encode('latin-1', 'replace').decode('latin-1'), border="B")
        self.ln(5)

def get_news_headlines(url, selector, paragraph_selector="p"):
    """Fetches headlines from the given URL with error handling."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }

    try:
        with requests.Session() as session:
            response = session.get(url, headers=headers, timeout=10)

            if response.status_code in [403, 404, 429]:
                print(f"⚠️ Skipping {url} - Status Code: {response.status_code}")
                return []

            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            headlines = soup.select(selector)
            articles = []

            for item in headlines:
                text = item.get_text(strip=True)
                link = item.find_parent("a")
                href = urljoin(url, link['href']) if link and 'href' in link.attrs else url

                paragraph = get_article_paragraph(href, paragraph_selector)

                if paragraph and paragraph != "No content extracted" and paragraph != "Could not fetch article content":
                    articles.append((text, href, paragraph, url))

            return articles
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching {url}: {e}")
        return []

def get_article_paragraph(article_url, paragraph_selector="p"):
    """Extracts the first paragraph from the news article."""
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(article_url, headers=headers, timeout=10)

        if response.status_code in [403, 404, 429]:
            return "No content extracted"

        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraph = soup.select_one(paragraph_selector)

        return paragraph.get_text(strip=True) if paragraph else "No content extracted"

    except requests.exceptions.RequestException:
        return "Could not fetch article content"

def save_to_pdf(articles, filename="news_report.pdf"):
    """Saves the news articles to a PDF file."""
    if not articles:
        print("⚠️ No news articles found. PDF not generated.")
        return

    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    for idx, (title, link, summary, source) in enumerate(articles):
        pdf.add_news_tile(title, link, summary, source)

        if idx % 5 == 0 and idx > 0:  # Add new page after 5 articles
            pdf.add_page()

    pdf.output(filename)
    print(f"✅ News report saved to {filename}")

if __name__ == "__main__":
    news_sites = [
        # Cybersecurity & Tech News
        {"url": "https://thehackernews.com/", "selector": "h2"},
        {"url": "https://www.securityweek.com/", "selector": ".article-title a"},
        {"url": "https://www.bleepingcomputer.com/", "selector": "h2 a"},
        {"url": "https://www.darkreading.com/", "selector": "h3 a"},
        {"url": "https://threatpost.com/", "selector": "h2 a"},
        {"url": "https://www.csoonline.com/", "selector": "h3 a"},
        {"url": "https://www.zdnet.com/tech/", "selector": "h3 a"},
        {"url": "https://www.wired.com/", "selector": "h2 a"},
        {"url": "https://www.techrepublic.com/", "selector": "h3 a"},
        {"url": "https://www.scmagazine.com/", "selector": ".c-card__title a"},

        # General News (World & Tech)
        {"url": "https://www.cnn.com/world", "selector": "h2"},
        {"url": "https://www.bbc.com/news/technology", "selector": "h3"},
        {"url": "https://www.nytimes.com/section/technology", "selector": "h2"},
        {"url": "https://www.theguardian.com/uk/technology", "selector": "h3"},
        {"url": "https://www.reuters.com/technology/", "selector": "h3"},
        {"url": "https://www.forbes.com/innovation/", "selector": "h3"},
        {"url": "https://www.businessinsider.com/tech", "selector": "h2"},
        {"url": "https://www.cnbc.com/technology/", "selector": "h2"},
        {"url": "https://www.bloomberg.com/technology", "selector": "h1"},

        # AI, Blockchain, and Emerging Tech
        {"url": "https://www.artificialintelligence-news.com/", "selector": "h3 a"},
        {"url": "https://www.cryptopolitan.com/", "selector": "h2 a"},
        {"url": "https://cointelegraph.com/", "selector": "h2 a"},
        {"url": "https://www.decrypto.co/", "selector": "h2 a"},
        {"url": "https://www.venturebeat.com/", "selector": "h2 a"}
    
    ]

    all_articles = []
    for site in news_sites:
        print(f"🔍 Scraping: {site['url']} ...")
        articles = get_news_headlines(site['url'], site['selector'])
        all_articles.extend(articles)
        time.sleep(random.uniform(2, 5))

    save_to_pdf(all_articles)

