import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import sqlite3
from sqlite3 import Error
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
import random

BASE_URL = "https://www.example-real-estate.com"
SEARCH_URL = "/houses-for-sale"
DATABASE_FILE = "realestate.db"
NUM_THREADS = 5 


PROXIES = [
    "http://proxy1.example.com",
    "http://proxy2.example.com",
    "http://proxy3.example.com",
]


def create_database():
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS houses
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, price INTEGER, description TEXT)''')
        conn.commit()
        conn.close()
    except Error as e:
        print(e)


def scrape_page(page_url):
    try:
        user_agent = UserAgent().random
        proxy = random.choice(PROXIES)
        headers = {'User-Agent': user_agent}
        response = requests.get(page_url, proxies={"http": proxy}, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        for house in soup.find_all('div', class_='house-listing'):
            title = house.find('h2').text.strip()
            price = int(house.find('span', class_='price').text.replace(',', '').replace('$', ''))
            description = house.find('p').text.strip()

            save_to_database(title, price, description)
    except Exception as e:
        print(f"Error scraping page: {e}")


def save_to_database(title, price, description):
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO houses (title, price, description) VALUES (?, ?, ?)", (title, price, description))
        conn.commit()
        conn.close()
    except Error as e:
        print(e)


def scrape_real_estate_website():
    create_database()
    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        futures = []
        for page_num in range(1, 11):  # Scrape 10 pages of search results
            page_url = urljoin(BASE_URL, f"{SEARCH_URL}?page={page_num}")
            future = executor.submit(scrape_page, page_url)
            futures.append(future)

        for future in futures:
            future.result()


scrape_real_estate_website()
