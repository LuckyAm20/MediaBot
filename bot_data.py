import json
import os

import telebot
from dotenv import load_dotenv


load_dotenv()
bot = telebot.TeleBot(os.getenv('TELEGRAM_API_TOKEN'))

genres = ['Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family',
          'Fantasy', 'Film-Noir', 'Game-Show', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'News', 'Reality-TV',
          'Romance', 'Sci-Fi', 'Short', 'Sport', 'Thriller', 'War', 'Western']
with open('data/movie_data.json', 'r+', encoding='utf-8') as f:
    data = json.load(f)
with open('data/movie_titles.json', 'r+', encoding='utf-8') as f:
    movie_titles = json.load(f)
movies = [title[0] for title in movie_titles]

with open('data/music_data.json', 'r+', encoding='utf-8') as f:
    data_music = json.load(f)
with open('data/tracks.json', 'r+', encoding='utf-8') as f:
    tracks = json.load(f)
songs = [(value[0], value[1]) for value in tracks]

with open('data/movies_kinopoisk.json', 'r', encoding='utf-8') as file:
    movie_data_kinopoisk = json.load(file)
with open('data/movies_imdb.json', 'r', encoding='utf-8') as file:
    movie_data_imdb = json.load(file)

with open('data/music_spotify.json', 'r', encoding='utf-8') as file:
    music_data_spotify = json.load(file)

spotify_artist = []
for artist in [el['artists'] for el in music_data_spotify]:
    if artist not in spotify_artist and artist.isalnum():
        spotify_artist.append(artist)

spotify_genre = []
for genre in [el['track_genre'] for el in music_data_spotify]:
    if genre not in spotify_genre:
        spotify_genre.append(genre)
