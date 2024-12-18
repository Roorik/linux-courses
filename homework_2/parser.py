import os
import time
import logging
import requests
import pandas as pd

from schedule import every, run_pending, idle_seconds
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

# настраиваем логгирование
logging.basicConfig(filename='log.txt', level=logging.INFO)
log = logging.getLogger(__name__)

def books_to_csv(base_url: str, output_file: str) -> None:
    '''
    Парсит указанный ресурс и записывает результат в csv файл
    
    :param base_url: str - базовый адрес ресурса
    :param base_url: str - имя файла для записи
    '''
    # объявляем заголовочник для csv файла
    headers = ['title', 'rating', 'available', 'description', 'upc', 'product_type', 'price', 'price_incl_tax', 'tax', 'number_of_reviews']
    # лист для полученных данных
    data = []
    # страница с которой начинаем скрапинг
    page = 0
    
    while True:
        # открываем следующую страницу
        page += 1
        # адрес по которому будем парсить
        url = f'{base_url}/catalogue/page-{page}.html'
        # получаем ответ от страницы
        response = requests.get(url)
        
        # если не 200й статус (т.е. любая ошибка) то выходим из цикла
        status = response.status_code
        if status != 200:
            log.error(f'Произошла ошибка при обращении к серверу, код ошибки: {status}')
            break
        
        # передаём html парсеру контент со страницы
        soup = BeautifulSoup(response.content, 'html.parser')
        # поиск по тегу
        books = soup.select('.product_pod')
        
        # если книг на странице нет - завершаем цикл 
        if not books:
            log.error(f'Произошла ошибка, страница пуста')
            break
        
        # перебираем книги на странице
        for book in books:
            # составляем адрес книги которую собираемся парсить
            book_link = base_url + '/catalogue/' + book.h3.a['href']
            # парсим книгу
            book_data = scrape_book_data(book_link)
            # добавляем полученные значения в лист с данными
            data.append(book_data)          
    
    log.info(f'Распаршено {page-1} страниц')
    # составляем датафрейм из полученных данных
    df = pd.DataFrame(data=data, columns=headers)
    # чистим данные
    clean_dataframe(df=df)
    # записываем в csv файл без индексации
    df.to_csv(output_file, index=False)

def scrape_book_data(book_url: str) -> list:
    '''
    Парсит данные указанной книги и отдаёт её характеристики
    
    :param book_url: str - адрес разбираемой книги
    :return: list - полученные характеристики книги
    '''
    # получаем ответ от страницы с книгой
    response = requests.get(book_url)
    # передаём html парсеру контент со страницы
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # собираем данные:
    title = soup.h1.text # Заголовок
    
    rating_classes = soup.select_one('.star-rating')['class'] 
    rating = rating_classes[1] if len(rating_classes) > 1 else 'No rating' # Рейтинг
    
    availability_text = soup.select_one('.availability').text.strip()
    availability = ''.join(filter(str.isdigit, availability_text)) # В наличии 
    
    description = '' # Описание 
    description_element = soup.select_one('#product_description ~ p')
    if description_element:
        description = description_element.text.strip() 
    
    product_info = {} # Дополнительные характеристики
    table = soup.select('.table.table-striped tr')
    for row in table:
        key = row.th.text.strip()
        value = row.td.text.strip()
        product_info[key] = value
    
    # отдаём лист характеристик
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
    
def clean_dataframe(df: pd.DataFrame) -> None:
    '''
    Очищает полученный датафрейм от дубликатов и пустых значений
    
    :param df: DataFrame - исходный датафрейм
    '''
    # количество пустых строк
    isna_sum = df.isna().sum()
    # количество полных дупликатов
    dupl_sum = df.duplicated().sum()
    
    # чистим дубликаты
    df.drop_duplicates(inplace=True)
    # чистим пустые данные
    df = df.dropna(inplace=True)
    log.info(f'Пустых строк при парсе:\n{isna_sum}, дубликатов:\n{dupl_sum}')

def main():
    # базовый url
    BASE_URL = os.getenv('TOSCRAPE_BASE_URL')
    # имя файла для записи результата
    OUTPUT_FILE = 'books_data.csv'
    # парсим ресурс
    books_to_csv(base_url=BASE_URL, output_file=OUTPUT_FILE)

if __name__ == '__main__': 
    # запускается ежедневно в 19:00  
    every().day.at('19:00').do(main)
    while True:
        n = idle_seconds()
        if n is None:
            break
        elif n > 0:
            # Засыпаем на время ожидание
            log.info('Засыпаю до времени выполенния')
            time.sleep(n)
        run_pending()