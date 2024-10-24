import requests
from bs4 import BeautifulSoup
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# Ustawienia Selenium WebDriver
def init_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--remote-debugging-port=9222')
    
    service = Service('E:\\chromedriver')  # Wskaż ścieżkę do pliku chromedriver.exe
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Funkcja do filtrowania i usuwania niepotrzebnych tagów i atrybutów, zachowując tylko <h2>, <h3>, <p>, <strong>
def filter_html_content(soup):
    allowed_tags = ['h2', 'h3', 'p', 'strong']
    
    # Znajdź wszystkie tagi
    for tag in soup.find_all(True):  
        if tag.name not in allowed_tags:
            tag.unwrap() 
        else:
            tag.attrs = {}

    return str(soup)

# Funkcja do scrapowania artykułu
def scrape_article(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        if not soup.find('article'):
            raise Exception("No article found, using Selenium WebDriver.")
        
        title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "No title found"
        
        
        category = soup.find('meta', {'property': 'article:section'})['content'] if soup.find('meta', {'property': 'article:section'}) else "No category found"
        
        
        date = soup.find('time').get_text(strip=True) if soup.find('time') else "No date found"
        
        
        article_content = soup.find('article')
        filtered_content = filter_html_content(article_content) if article_content else "No content found"
        
        return {
            "url": url,
            "title": title,
            "category": category,
            "publication_date": date,
            "content": filtered_content
        }
    
    except Exception as e:
        print(f"Error occurred for {url}: {e}")
        
        # Uruchom Selenium WebDriver, jeśli tradycyjne requesty nie działają
        driver = init_driver()
        driver.get(url)
        time.sleep(5)  # Poczekaj na załadowanie JS

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        
        title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "No title found"
        
        
        category = soup.find('meta', {'property': 'article:section'})['content'] if soup.find('meta', {'property': 'article:section'}) else "No category found"
        
        
        date = soup.find('time').get_text(strip=True) if soup.find('time') else "No date found"
        
        
        article_content = soup.find('article')
        filtered_content = filter_html_content(article_content) if article_content else "No content found"
        
        driver.quit()
        
        return {
            "url": url,
            "title": title,
            "category": category,
            "publication_date": date,
            "content": filtered_content
        }

# Funkcja do zapisu wyników w formacie JSON
def save_to_json(data, filename='response.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Lista stron do scrapowania
urls = [
    "https://bistrolubie.pl/pierniki-z-miodem-tradycyjny-przepis-na-swiateczne-ciasteczka-pelne-aromatu",
    "https://bistrolubie.pl/piernik-z-mascarpone-kremowy-i-pyszny-przepis-na-deser-idealny-na-swieta",
    "https://spidersweb.pl/2024/07/metamorfoza-w-centrum-warszawy.html",
    "https://spidersweb.pl/2024/07/kontrolery-na-steam-rosnie-popularnosc.html",
    "https://www.chip.pl/2024/06/wtf-obalamy-mity-poprawnej-pozycji-przy-biurku",
    "https://www.chip.pl/2024/07/sony-xperia-1-vi-test-recenzja-opinia",
    "https://newonce.net/artykul/chief-keef-a-sprawa-polska-opowiadaja-benito-gicik-crank-all",
    "https://newonce.net/artykul/glosna-gra-ktorej-akcja-toczy-sie-w-warszawie-1905-roku-gralismy-w-the-thaumaturge"
]

# Główna funkcja
if __name__ == "__main__":
    scraped_data = []
    
    for url in urls:
        print(f"Scraping {url}")
        article_data = scrape_article(url)
        scraped_data.append(article_data)
    
    
    save_to_json(scraped_data)
    print("Scraping completed and data saved to response.json.")
