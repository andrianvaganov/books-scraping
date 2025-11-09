import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import schedule
import time

def get_book_data(book_url: str) -> dict:
    """
    Получает данные о книге с указанной страницы.

    Аргументы:
        book_url (str): URL страницы книги на сайте Books to Scrape.

    Возвращает:
        dict: Словарь, содержащий информацию о книге
    """
    response = requests.get(book_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    data = {}

    title_tag = soup.find('h1')
    data['title'] = title_tag.text.strip() if title_tag else ''

    price_tag = soup.find('p', class_='price_color')
    data['price'] = price_tag.text.strip() if price_tag else ''

    rating_tag = soup.find('p', class_='star-rating')
    if rating_tag and 'class' in rating_tag.attrs:
        classes = rating_tag.attrs['class']
        data['rating'] = classes[-1] if len(classes) > 1 else ''
    else:
        data['rating'] = ''

    availability_tag = soup.find('p', class_='instock availability')
    if availability_tag:
        availability_text = availability_tag.get_text(strip=True)
        match = re.search(r'\d+', availability_text)
        data['availability'] = int(match.group()) if match else 0
    else:
        data['availability'] = 0

    description = ''
    desc_div = soup.find('div', id='product_description')
    if desc_div:
        desc_para = desc_div.find_next('p')  # параграф сразу после div
        if desc_para:
            description = desc_para.get_text(strip=True)
    data['description'] = description

    product_info = {}
    table = soup.find('table', class_='table table-striped')
    if table:
        rows = table.find_all('tr')
        for row in rows:
            header = row.find('th').get_text(strip=True)
            value = row.find('td').get_text(strip=True)
            product_info[header] = value
    for key, value in product_info.items():
        if key.lower() != 'availability':
            data[key] = value
    print('parsed: ', data)
    return data

def scrape_books(save_to_file: bool = False) -> list:
    """
    Обходит все страницы каталога и собирает данные о каждой книге.

    Аргументы:
        save_to_file (bool): Если True, сохраняет итоговый список книг в файл
        'books_data.txt'. По умолчанию False

    Возвращает:
        Список словарей, каждый из которых содержит информацию об одной книге.
    """
    base_url = "http://books.toscrape.com/catalogue/"
    books_data = []
    page_num = 1

    while True:
        print('parsing page', page_num)
        page_url = f"{base_url}page-{page_num}.html"
        res = requests.get(page_url)
        if res.status_code != 200:
            break
        soup = BeautifulSoup(res.text, 'html.parser')
        book_links = soup.select('h3 a')
        if not book_links:
            break
        for link in book_links:
            relative_url = link['href']
            book_url = urljoin(page_url, relative_url)
            try:
                book_data = get_book_data(book_url)
                books_data.append(book_data)
            except Exception as e:
                print(f"Ошибка при парсинге: {book_url}: {e}")
        if save_to_file:
            f = open('../artifacts/books_data.txt', 'a', encoding="utf-8")
            for book in books_data:
                f.write(str(book) + "\n")
            f.close()
            books_data.clear()
        page_num += 1

    return books_data

schedule.every().day.at("20:35").do(scrape_books, save_to_file=True)

f = open('../artifacts/books_data.txt', 'w')
f.close()

while True:
    print('run in progress...', time.time())
    schedule.run_pending()
    time.sleep(60)