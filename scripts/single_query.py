import requests
import re
import pandas as pd
import nltk
from nltk.tokenize import sent_tokenize
from bs4 import BeautifulSoup
import time
import random

# Download necessary NLTK datasets
nltk.download('punkt')

# Define the search term
search_term = "at 1:31 PM"
time_pattern = rf'\b{search_term}\b'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def search_wikipedia(query):
    url = f'https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch="{query}"&format=json'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    search_results = response.json()['query']['search']
    links = [f"https://en.wikipedia.org/wiki/{result['title'].replace(' ', '_')}" for result in search_results]
    return links

def fetch_wikipedia_content(url):
    response = requests.get(url, headers=headers)
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

    wikipedia_links = search_wikipedia(search_query)

    results = []

    for link in wikipedia_links[:5]:  # Limit to top 5 results
        content = fetch_wikipedia_content(link)
        filtered_events = filter_events_by_time(content, time_pattern)
        if filtered_events:
            for event in filtered_events:
                results.append((event, link))
        time.sleep(random.uniform(2, 5))  # Random sleep to avoid detection

    # Create DataFrame from results
    df = pd.DataFrame(results, columns=['Excerpt', 'Link'])
    print(df)

    return df

if __name__ == "__main__":
    df = main()
