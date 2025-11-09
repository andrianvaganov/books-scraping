import pytest

from scraper.scraper import get_book_data, scrape_books


def test_get_book_data_structure():
    """Проверяем, что get_book_data возвращает словарь с нужными ключами."""
    url = "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    data = get_book_data(url)
    expected_keys = {"title", "price", "rating", "availability", "description",
                     "UPC", "Product Type", "Price (excl. tax)", "Price (incl. tax)",
                     "Tax", "Number of reviews"}
    assert isinstance(data, dict), "Результат должен быть словарем"
    assert expected_keys.issubset(data.keys()), "Отсутствуют некоторые ключевые поля книги"

def test_get_book_data_content():
    """Проверяем корректность отдельных полей для известной книги."""
    url = "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    data = get_book_data(url)
    assert data.get("title") == "A Light in the Attic", "Некорректное название книги"
    assert data.get("price") == "£51.77", "Цена книги не совпадает с ожидаемой"
    assert data.get("rating") == "Three", "Рейтинг книги получен некорректно"
    assert data.get("description"), "Описание книги не получено (пустое)"

def test_scrape_books_count(monkeypatch):
    """Проверяем, что scrape_books собирает информацию со всех страниц каталога."""
    books = scrape_books(save_to_file=False)
    assert isinstance(books, list), "Результат должен быть списком"
    assert books, "Список книг не должен быть пустым"
    assert len(books) >= 1000, "Собрано меньше книг, чем ожидается для полного каталога"
    book = books[0]
    assert isinstance(book, dict), "Каждый элемент списка должен быть словарем с данными о книге"
    for key in ("title", "price", "rating", "availability"):
        assert key in book, f"В данных книги отсутствует поле {key}"