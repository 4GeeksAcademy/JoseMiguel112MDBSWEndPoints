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
from models import db, User, Character, Planet, Vehicle
from sqlalchemy import select

#from models import Person

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

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


###EndPoints
@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

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
# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
