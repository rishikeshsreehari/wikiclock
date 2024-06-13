from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import nltk
import time
import random

# Download necessary NLTK datasets
nltk.download('punkt')
from nltk.tokenize import sent_tokenize

# Define the search term
search_term = "at 1:31 PM"
time_pattern = rf'\b{search_term}\b'

# Path to your ChromeDriver
chrome_driver_path = 'C:/Users/rishi/Desktop/chromedriver-win64/chromedriver.exe'

def google_search(query):
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        # Add more user agents
    ]
    options.add_argument(f'user-agent={random.choice(user_agents)}')

    service = ChromeService(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(f"https://www.google.com/search?q=\"{query}\"+site:wikipedia.org&num=10&hl=en")

    # Random sleep to avoid detection
    time.sleep(random.uniform(5, 10))

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a')))
    links = set()
    for a in driver.find_elements(By.CSS_SELECTOR, 'a'):
        href = a.get_attribute('href')
        if href and "https://en.wikipedia.org/wiki/" in href:
            clean_link = re.search(r'(https://en.wikipedia.org/wiki/[^&]*)', href)
            if clean_link:
                clean_link = clean_link.group(1)
                if not re.search(r'\b(?:Special|Talk|File|Help|Category|Portal|Template|Wikipedia|MediaWiki):\b', clean_link):
                    links.add(clean_link)

    driver.quit()
    return list(links)

def fetch_wikipedia_content(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def filter_events_by_time(content, time_pattern):
    soup = BeautifulSoup(content, 'html.parser')
    paragraphs = [p.get_text().strip() for p in soup.find_all('p')]

    filtered_events = []
    for paragraph in paragraphs:
        sentences = sent_tokenize(paragraph)
        for sentence in sentences:
            if re.search(time_pattern, sentence, re.IGNORECASE):
                filtered_events.append(sentence)
                return filtered_events  # Exit after finding the first match to avoid duplicates
    return filtered_events

def main():
    search_query = f'{search_term}'

    wikipedia_links = google_search(search_query)

    results = []

    for link in wikipedia_links[:5]:  # Limit to top 5 results
        content = fetch_wikipedia_content(link)
        filtered_events = filter_events_by_time(content, time_pattern)
        if filtered_events:
            for event in filtered_events:
                results.append((event, link))

    # Create DataFrame from results
    df = pd.DataFrame(results, columns=['Excerpt', 'Link'])
    print(df)

    return df

if __name__ == "__main__":
    df = main()
