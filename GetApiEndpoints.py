from flask import Flask, jsonify
from models.models import Film, Serial, User
from app import app, db

@app.route('/api/films')
def api_get_films():
    films = db.session.query(Film).all()
    films_json = [
        {"id": film.fid, "name": film.name, "year_of_release": film.year_of_release, "description": film.description}
        for film in films]
    return jsonify(films_json)

@app.route('/api/serials')
def api_get_serials():
    serials = db.session.query(Serial).all()
    serials_json = [{"id": serial.sid, "name": serial.name, "year_of_release": serial.year_of_release,
                     "description": serial.description} for serial in serials]
    return jsonify(serials_json)

@app.route('/api/users')
def api_get_users():
    users = db.session.query(User).all()
    users_json = [{"id": user.uid, "login": user.login} for user in users]
    return jsonify(users_json)

def test_api_endpoints():
    with app.test_request_context():
        print("Тестирование /api/films:")
        response = api_get_films()
        films_data = response.get_json()
        for film in films_data:
            print(f'ID: {film["id"]}, Name: {film["name"]}, Year: {film["year_of_release"]}, Description: {film["description"]}')

        print("\nТестирование /api/serials:")
        response = api_get_serials()
        serials_data = response.get_json()
        for serial in serials_data:
            print(f'ID: {serial["id"]}, Name: {serial["name"]}, Year: {serial["year_of_release"]}, Description: {serial["description"]}')

        print("\nТестирование /api/users:")
        response = api_get_users()
        users_data = response.get_json()
        for user in users_data:
            print(f'ID: {user["id"]}, Login: {user["login"]}')

if __name__ == '__main__':
    with app.app_context():
        test_api_endpoints()
    app.run(debug=True)
