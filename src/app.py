import os
from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from models import db, User, People, Planets, Favorites
from utils import APIException, generate_sitemap
from admin import setup_admin

def create_app():
    app = Flask(__name__)
    app.url_map.strict_slashes = False
    
    configure_app(app)
    setup_extensions(app)
    register_routes(app)
    
    return app

def configure_app(app):
    db_url = os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://") if db_url else "sqlite:////tmp/test.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = os.getenv("FLASK_APP_KEY", "sample key")

def setup_extensions(app):
    Migrate(app, db)
    db.init_app(app)
    CORS(app)
    setup_admin(app)

def register_routes(app):
    @app.route('/')
    def sitemap():
        return generate_sitemap(app)

    @app.route('/planets', methods=['GET'])
    def get_planets():
        planets = Planets.query.all()
        return jsonify([planet.serialize() for planet in planets])

    @app.route('/planets/<int:planet_id>', methods=['GET'])
    def get_planet(planet_id):
        planet = Planets.query.get(planet_id)
        if not planet:
            return jsonify({"message": "Planet not found"}), 404
        return jsonify(planet.serialize())

    @app.route('/people', methods=['GET'])
    def get_people():
        people = People.query.all()
        return jsonify([person.serialize() for person in people])

    @app.route('/people/<int:people_id>', methods=['GET'])
    def get_person(people_id):
        person = People.query.get(people_id)
        if not person:
            return jsonify({"message": "Character not found"}), 404
        return jsonify(person.serialize())

    @app.route('/users', methods=['GET'])
    def get_users():
        users = User.query.all()
        return jsonify([user.serialize() for user in users])

    @app.route('/users/<int:user_id>/favorites', methods=['GET'])
    def get_user_favorites(user_id):
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404
        return jsonify([fav.serialize() for fav in user.favorites])

    @app.route('/users/<int:user_id>/favorites/planet/<int:planet_id>', methods=['POST'])
    def add_favorite_planet(user_id, planet_id):
        user = User.query.get(user_id)
        planet = Planets.query.get(planet_id)
        if not user or not planet:
            return jsonify({"message": "User or Planet not found"}), 404
        if Favorites.query.filter_by(user_id=user_id, planet_id=planet_id).first():
            return jsonify({"message": "Planet is already in favorites"}), 400
        new_fav = Favorites(user_id=user_id, planet_id=planet_id)
        db.session.add(new_fav)
        db.session.commit()
        return jsonify({"message": "Planet added to favorites"}), 201

    @app.route('/users/<int:user_id>/favorites/people/<int:people_id>', methods=['POST'])
    def add_favorite_people(user_id, people_id):
        user = User.query.get(user_id)
        person = People.query.get(people_id)
        if not user or not person:
            return jsonify({"message": "User or Character not found"}), 404
        if Favorites.query.filter_by(user_id=user_id, people_id=people_id).first():
            return jsonify({"message": "Character is already in favorites"}), 400
        new_fav = Favorites(user_id=user_id, people_id=people_id)
        db.session.add(new_fav)
        db.session.commit()
        return jsonify({"message": "Character added to favorites"}), 201

    @app.route('/users/<int:user_id>/favorites/planet/<int:planet_id>', methods=['DELETE'])
    def delete_favorite_planet(user_id, planet_id):
        favorite = Favorites.query.filter_by(user_id=user_id, planet_id=planet_id).first()
        if not favorite:
            return jsonify({"message": "Favorite not found"}), 404
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"message": "Planet removed from favorites"}), 200

    @app.route('/users/<int:user_id>/favorites/people/<int:people_id>', methods=['DELETE'])
    def delete_favorite_people(user_id, people_id):
        favorite = Favorites.query.filter_by(user_id=user_id, people_id=people_id).first()
        if not favorite:
            return jsonify({"message": "Favorite not found"}), 404
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"message": "Character removed from favorites"}), 200

if __name__ == '__main__':
    app = create_app()
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
