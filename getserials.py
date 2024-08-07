import requests
from bs4 import BeautifulSoup
from app import app, db  # Убедитесь, что app и db импортированы правильно
from models.models import Serial

def fetch_series_links(url, max_links=30):
    """
        Извлекает и возвращает список ссылок на сериалы с указанной веб-страницы.

        Args:
            url (str): URL веб-страницы для скрапинга.
            max_links (int): Максимальное количество ссылок для извлечения.

        Returns:
            list: Список URL-адресов сериалов.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    links = soup.select('.redesign_afisha_movie a.wrapper_block_stack')
    base_url = 'https://www.film.ru'
    series_links = {base_url + link['href'] for link in links}
    return list(series_links)[:max_links]


def fetch_series_details(url):
    """
        Извлекает и возвращает детали сериала с указанной страницы.

        Args:
            url (str): URL страницы сериала.

        Returns:
            dict: Словарь с подробной информацией о сериале.
    """
    excluded_words = [
        "2024", "США", "Великобритания", "Франция", "Россия", "Германия", "Япония", "Южная Корея",
        "Канада", "Италия", "Индия", "Испания", "Австралия", "Швеция", "Республика Корея",
        "Турция", "Бразилия", "Польша", "Австрия", "Тайвань", "Таиланд", "Чили",
        "Индонезия", "Колумбия"
    ]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    all_info = [info.get_text(strip=True) for info in soup.select('.block_info a[href*="/a-z/serials"]')]
    title = soup.find('h1').text.strip().split('(')[0].strip()
    engname = soup.find('h2').text.strip()
    year = soup.find('h1').find('span').text.strip() if soup.find('h1').find('span') else 'No year specified'
    description = soup.select_one('div.wrapper_movies_text p').text.strip() if soup.select_one(
        'div.wrapper_movies_text p') else 'No description'
    description = description[:499]
    genres = [info for info in all_info if not any(word in info for word in excluded_words)]
    country = ", ".join([info for info in all_info if info in excluded_words and info != "2024"])
    time_text = ''
    director = ''
    time_duration = soup.find_all('div', class_='block_table')
    for block in time_duration:
        if 'время' in block.find('div').text.lower():
            time_text = block.find_all('div')[1].text.strip()
            time_text = time_text.split()[0]
        if 'режиссер' in block.find('div').text.lower():
            director = block.find_all('div')[1].text.strip().replace('\n', ', ').replace('\xa0', ' ')

    poster_img = soup.find('img', alt=title.split('(')[0].strip())
    poster_url = 'https://www.film.ru' + poster_img[
        'src'] if poster_img and 'src' in poster_img.attrs else ''

    series_details = {
        'name': title,
        'engname': engname,
        'year_of_release': year,
        'description': description,
        'genres': ", ".join(genres),
        'poster_url': poster_url,
        'county': country,
        'time_duration': time_text,
        'director': director,
        'mpaa': '18+'
    }

    return series_details


def save_serials_to_db(serials_details):
    """
        Сохраняет детали сериалов в базу данных.

        Args:
            serials_details (list): Список словарей с информацией о каждом сериале.
    """
    for serial in serials_details:
        print("Creating new serial with the following details:")
        print(f"Name: {serial['name']}")
        print(f"English Name: {serial['engname']}")
        print(f"Poster URL: {serial['poster_url']}")
        print(f"Genres: {serial['genres']}")
        print(f"Year of Release: {serial['year_of_release']}")
        print(f"Country: {serial['county']}")
        print(f"MPAA: {serial['mpaa']}")
        print(f"Time Duration: {serial['time_duration']}")
        print(f"Description: {serial['description']}")
        print(f"Director: {serial['director']}")

        new_serial = Serial(
            name=serial['name'],
            engname=serial['engname'],
            poster=serial['poster_url'],
            genres=serial['genres'],
            year_of_release=int(serial['year_of_release']),
            county=serial['county'],
            mpaa=serial['mpaa'],
            time_duration=serial['time_duration'],
            description=serial['description'],
            director=serial['director'],
            average_rating=0.0
        )
        db.session.add(new_serial)
    db.session.commit()


def main():
    list_url = 'https://www.film.ru/a-z/serials/united_states-2024'
    series_links = fetch_series_links(list_url)
    all_series_details = [fetch_series_details(link) for link in series_links]

    with app.app_context():
        save_serials_to_db(all_series_details)


if __name__ == "__main__":
    main()
