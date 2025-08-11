"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Vehicle, Favorite
from sqlalchemy import select
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
jwt = JWTManager(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


###EndPoints
@app.route('/users', methods=['GET'])
def get_users():
    all_users = db.session.execute(select(User)).scalars().all()
   
    results = list(map(lambda user: user.serialize(), all_users))

   
    response_body = {
        "results": results
    }

    return jsonify(response_body), 200

@app.route('/signup', methods=['POST'])
def create_user():
    data = request.get_json()
    user_email = data.get("email")
    user_password = data.get("password")

    user = db.session.execute(select(User).where(User.email == user_email)).scalar_one_or_none()

    if user is not None:
        return jsonify({"msg": "email already in use"}), 409
    
    new_user = User(email=user_email, password=user_password, is_active=True)
    db.session.add(new_user)
    db.session.commit()

    response_body = {
        "msg": "User added successfully",
        "user": new_user.serialize()
    }

    return jsonify(response_body), 201

# Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.
@app.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    user = db.session.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if user is None:
        return jsonify({"msg": "Bad username or password"}), 404
    
    if email != user.email or password != user.password:
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=email)
    return jsonify(access_token=access_token), 200

# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.
@app.route("/favorites", methods=["GET"])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user_email = get_jwt_identity()

    user = db.session.execute(select(User).where(User.email == current_user_email)).scalar_one_or_none()

    user_favorites = db.session.execute(select(Favorite).where(Favorite.user_id == user.id)).scalars().all()
    results = list(map(lambda favorite: favorite.serialize(), user_favorites))
    return jsonify(logged_in_as=current_user_email, favorites=results), 200

@app.route('/characters', methods=['GET'])
def get_characters():

    all_characters = db.session.execute(select(Character)).scalars().all()
   
    results = list(map(lambda character: character.serialize(), all_characters))

    # characters= Character.query.all()
    response_body = {
        "results": results
    }

    return jsonify(response_body), 200

    # return jsonify([character.serialize()for character in all_characters]), 200

@app.route('/characters/<int:id>', methods=['GET'])
def get_one_characters(id):
    print(id)
    character = db.session.execute(select(Character).where(Character.id == id)).scalar_one_or_none()
    
    
    if character is None:
        return jsonify({"msg": "Character not found"}), 404

    response_body = {
        "msg": "ok",
        "result": character.serialize()
    }

    return jsonify(response_body), 200

@app.route('/planets', methods=['GET'])
def get_planets():
    try:

        all_planets = db.session.execute(select(Planet)).scalars().all()
   
        results = list(map(lambda planets: planets.serialize(), all_planets))

    # characters= Character.query.all()
        response_body = {
            "results": results
        }

        return jsonify(response_body), 200
    except Exception as e:
        return jsonify({"msg": "Error retrieving planets", "error": str(e)}), 500
    

@app.route('/planets/<int:id>', methods=['GET'])
def get_one_planet(id):
    print(id)
    planet = db.session.execute(select(Planet).where(Planet.id == id)).scalar_one_or_none()
    
    
    if planet is None:
        return jsonify({"msg": "Planet not found"}), 404

    response_body = {
        "msg": "ok",
        "result": planet.serialize()
    }

    return jsonify(response_body), 200

@app.route('/user/favorites/<int:user_id>', methods=['GET'])
def get_user_favorites(user_id):
    user = db.session.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    
    if user is None:
        return jsonify({"msg": "User not found"}), 404

    favorites = db.session.execute(select(Favorite).where(Favorite.user_id == user_id)).scalars().all()
    
    results = list(map(lambda favorite: favorite.serialize(), favorites))

    response_body = {
        "results": results
    }

    return jsonify(response_body), 200

@app.route('/<int:user_id>/favoritesplanet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(user_id, planet_id):
    user = db.session.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    planet = db.session.execute(select(Planet).where(Planet.id == planet_id)).scalar_one_or_none()
    
    if user is None:
        return jsonify({"msg": "User not found"}), 404
    if planet is None:
        return jsonify({"msg": "Planet not found"}), 404

    new_favorite = Favorite(user_id=user_id, planet_id=planet_id)
    db.session.add(new_favorite)
    db.session.commit()

    response_body = {
        "msg": "Favorite added successfully",
        "favorite": new_favorite.serialize()
    }

    return jsonify(response_body), 201

@app.route('/<int:user_id>/favoritescharacter/<int:character_id>', methods=['POST'])
def add_favorite_character(user_id, character_id):
    user = db.session.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    planet = db.session.execute(select(Character).where(Character.id == character_id)).scalar_one_or_none()
    
    if user is None:
        return jsonify({"msg": "User not found"}), 404
    if planet is None:
        return jsonify({"msg": "Character not found"}), 404

    new_favorite = Favorite(user_id=user_id, character_id=character_id)
    db.session.add(new_favorite)
    db.session.commit()

    response_body = {
        "msg": "Favorite added successfully",
        "favorite": new_favorite.serialize()
    }

    return jsonify(response_body), 201


@app.route('/<int:user_id>/favoritescharacter/<int:character_id>', methods=['DELETE'])
def delete_favorite_character(user_id, character_id):
    favorite = db.session.execute(select(Favorite).where(Favorite.user_id == user_id, Favorite.character_id == character_id)).scalar_one_or_none()
    
    if favorite is None:
        return jsonify({"msg": "Favorite not found"}), 404

    db.session.delete(favorite)
    db.session.commit()

    response_body = {
        "msg": "Favorite deleted successfully"
    }

    return jsonify(response_body), 200

@app.route('/<int:user_id>/favoritesplanet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(user_id, planet_id):
    favorite = db.session.execute(select(Favorite).where(Favorite.user_id == user_id, Favorite.planet_id == planet_id)).scalar_one_or_none()
    
    if favorite is None:
        return jsonify({"msg": "Favorite not found"}), 404

    db.session.delete(favorite)
    db.session.commit()

    response_body = {
        "msg": "Favorite deleted successfully"
    }

    return jsonify(response_body), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
