import os
import requests
import pandas as pd

from bs4 import BeautifulSoup
from dotenv import load_dotenv, dotenv_values

load_dotenv()

def books_to_csv(base_url: str, output_file: str):
    headers = ['Title', 'Rating', 'Available', 'Description', 'UPC', 'Product Type', 'Price (excl. tax)', 'Price (incl. tax)', 'Tax', 'Number of Reviews']
    
    data = []
    # страница с которой начинаем скрапинг
    page = 0
    
    while page < 10:
        page += 1
        print(page)
        url = f'{base_url}catalogue/page-{page}.html'
        response = requests.get(url)
        if response.status_code != 200:
            break
        
        soup = BeautifulSoup(response.content, 'html.parser')
        books = soup.select('.product_pod')
        
        if not books:
            continue
        
        for book in books:
            book_link = base_url + 'catalogue/' + book.h3.a['href']
            book_data = scrape_book_data(book_link)
            data.append(book_data)          
        
    df = pd.DataFrame(data=data, columns=headers)
    df.to_csv(output_file, index=False)

def scrape_book_data(book_url: str):
    response = requests.get(book_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Заголовок
    title = soup.h1.text
    # Рейтинг
    rating_classes = soup.select_one('.star-rating')['class']
    rating = rating_classes[1] if len(rating_classes) > 1 else 'No rating'
    # В наличии 
    availability_text = soup.select_one('.availability').text.strip()
    availability = "".join(filter(str.isdigit, availability_text))
    # Описание 
    description = ''
    description_element = soup.select_one('#product_description ~ p')
    if description_element:
        description = description_element.text.strip() 
    # Дополнительные характеристики
    product_info = {}
    table = soup.select('.table.table-striped tr')
    for row in table:
        key = row.th.text.strip()
        value = row.td.text.strip()
        product_info[key] = value
        
    return [
        title, 
        rating, 
        availability,
        description,
        product_info.get('UPC', ''),
        product_info.get('Product Type', ''),
        product_info.get('Price (excl. tax)', ''),
        product_info.get('Price (incl. tax)', ''),
        product_info.get('Tax', ''),
        product_info.get('Number of Reviews', ''),
    ]

def main():
    BASE_URL = os.getenv('TOSCRAPE_BASE_URL')
    OUTPUT_FILE = 'homework_2/books_data.csv'
    
    books_to_csv(base_url=BASE_URL, output_file=OUTPUT_FILE)

if __name__ == '__main__':   
    main()