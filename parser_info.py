import requests
from bs4 import BeautifulSoup


def parse_website_film(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/58.0.3029.110 Safari/537.3'
    }

    url_data = requests.get(url, headers=headers).text
    s_data = BeautifulSoup(url_data, 'html.parser')
    imdb_content = s_data.find("meta", attrs={"name": "description"})

    if imdb_content is not None:
        movie_descr = imdb_content.attrs.get('content', '').split('.')

        if len(movie_descr) >= 3:
            movie_director = movie_descr[0]
            movie_cast = str(movie_descr[1]).replace('With', 'Актёры: ').strip()
            movie_story = 'Описание: ' + str(movie_descr[2]).strip() + '.'

            return [movie_director, movie_cast, movie_story]
        else:
            return None
    else:
        return None


def parse_video_link(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                      ' AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/58.0.3029.110 Safari/537.3'
    }

    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.content, 'html.parser')

    video_link_element = soup.find('a', href=lambda href: href and href.startswith('/video/'))
    if video_link_element:
        video_link = video_link_element['href']
        return f'https://www.imdb.com{video_link}'
    return None
