import requests
import re
import pandas as pd
import nltk
from nltk.tokenize import sent_tokenize
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime, timedelta

# Download necessary NLTK datasets
nltk.download('punkt')

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

def filter_events_by_time(content, time_patterns):
    soup = BeautifulSoup(content, 'html.parser')
    paragraphs = [p.get_text().strip() for p in soup.find_all('p')]

    filtered_events = []
    for paragraph in paragraphs:
        sentences = sent_tokenize(paragraph)
        for sentence in sentences:
            if any(re.search(time_pattern, sentence, re.IGNORECASE) for time_pattern in time_patterns):
                filtered_events.append(sentence)
                return filtered_events  # Exit after finding the first match to avoid duplicates
    return filtered_events

def generate_time_range(start_time, end_time):
    start = datetime.strptime(start_time, '%I:%M %p')
    end = datetime.strptime(end_time, '%I:%M %p')
    current_time = start

    while current_time <= end:
        full_time = current_time.strftime('%I:%M %p')
        short_time = current_time.strftime('%I:%M %p').lstrip('0')  # Manually remove leading zero
        yield full_time, short_time
        current_time += timedelta(minutes=1)

def save_dataframe(df, suffix):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"results_{suffix}_{timestamp}.csv"
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

def main():
    start_time = '12:00 AM'
    end_time = '11:59 PM'
    start_datetime = datetime.now()

    results = []
    counter = 0  # Counter to periodically save the dataframe

    for full_time, short_time in generate_time_range(start_time, end_time):
        time_patterns = [rf'\b{full_time}\b', rf'\b{short_time}\b']
        search_queries = [f'{full_time}', f'{short_time}']

        found = False

        for search_query in search_queries:
            try:
                wikipedia_links = search_wikipedia(search_query)

                for link in wikipedia_links[:5]:  # Limit to top 5 results
                    content = fetch_wikipedia_content(link)
                    filtered_events = filter_events_by_time(content, time_patterns)
                    if filtered_events:
                        for event in filtered_events:
                            results.append((search_query, event, link))
                        found = True

            except Exception as e:
                print(f"Error processing {search_query}: {str(e)}")

            time.sleep(random.uniform(2, 5))  # Random sleep to avoid detection

        if found:
            print(f"{full_time} or {short_time} records added.")
        else:
            print(f"No results for {full_time} or {short_time} found.")
            results.append((full_time, '', ''))

        counter += 1

        # Save the dataframe every 30 minutes or so
        if counter % 30 == 0:
            df = pd.DataFrame(results, columns=['Time', 'Excerpt', 'Link'])
            save_dataframe(df, "interim")

        # Print elapsed time
        elapsed_time = datetime.now() - start_datetime
        print(f"Elapsed time: {elapsed_time}")

    # Final save
    df = pd.DataFrame(results, columns=['Time', 'Excerpt', 'Link'])
    save_dataframe(df, "final")

    return df

if __name__ == "__main__":
    df = main()
