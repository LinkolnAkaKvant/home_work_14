# Загружаем необходимые модули
import json
import sqlite3
import flask

# инициализируем flask
app = flask.Flask(__name__)
app.config['JSON_AS_ASCII'] = False


# Функция для работы БД
def run_sql(sql):
    with sqlite3.connect("netflix.db") as connection:
        connection.row_factory = sqlite3.Row
        result = []
        for item in connection.execute(sql).fetchall():
            result.append(dict(item))

        return result


# Вьюшка для поиска по названию
@app.route("/movie/<title>")
def title_search(title):
    sql = f''' select title, country, release_year, listed_in as genre, description from netflix
        where lower(title)='{title}'
        order by date_added desc
        limit 1 
            '''

    result = run_sql(sql)
    if result:
        result = result[0]

    return flask.jsonify(result)


# Вьюшка для поиска по годам
@app.route("/movie/<year1>/to/<year2>")
def search_by_years(year1, year2):
    sql = f'''
            select title, release_year
            from netflix
            where release_year between {year1} and {year2}
            limit 100
            '''

    return flask.jsonify(run_sql(sql))


# Вьюшка для поиска по рейтингу
@app.route("/rating/<rating>")
def search_by_rating(rating):
    rating_list = {"children": ("G", "G"),
                   "family": ("G", "PG", "PG-13"),
                   "adult": ("R", "NC-17")
                   }
    sql = f'''
            select title, rating, description
            from netflix
            where rating in {rating_list.get(rating)}
            '''
    return flask.jsonify(run_sql(sql))


# Вьюшка для поиска по жанру
@app.route("/genre/<genre>")
def search_by_genre(genre):
    sql = f'''
        select title, description
        from netflix
        where listed_in like '%{genre}%'
        order by date_added
        limit 10
        '''

    return flask.jsonify(run_sql(sql))


# Функция поиска данных по актерам и вывода совпадений
def search_by_two_actors(name1='Rose McIver', name2='Ben Lamb'):
    sql = f'''
            select "cast" from netflix
            where "cast" like '%{name1}%' and "cast" like '%{name2}%'
            '''
    result = run_sql(sql)
    main_name = {}
    for item in result:
        names = item.get('cast').split(", ")
        for name in names:
            if name in main_name.keys():
                main_name[name] += 1
            else:
                main_name[name] = 1
    result = []
    for item in main_name:
        if item not in (name1, name2) and main_name[item] > 2:
            result.append(item)

    return result


# Функция для поиска по типу, году и жанру
def search_by_type_year_genre(types='Movie', release_year=2020, genre='Dramas'):
    sql = f'''
            select title, description
            from netflix
            where type = '{types}'
            and release_year = '{release_year}'
            and listed_in = '{genre}'
            '''
    return json.dumps(run_sql(sql), indent=4, ensure_ascii=False)


# Запуск приложения
if __name__ == '__main__':
    app.run()
