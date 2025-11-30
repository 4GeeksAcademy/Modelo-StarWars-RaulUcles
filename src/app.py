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
from models import db, Usuario, Planetas, Personajes

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

@app.route('/people/<nombre>', methods=['GET'])
def get_people_id(nombre):
    personaje = Personajes.query.get(nombre)
    if personaje is None:
        return jsonify({"msg": "Personaje no encontrado"}), 404
    return jsonify(personaje.serialize()), 200

@app.route('/people', methods=['GET'])
def get_people():
    all_people = Personajes.query.all()
    result = [persona.serialize() for persona in all_people]
    return jsonify(result), 200

@app.route('/planets', methods=['GET'])
def get_planets():
    planetas = Planetas.query.all()
    result = [planeta.serialize() for planeta in planetas]
    return jsonify(result), 200

@app.route('/planets/<nombre>', methods=['GET'])
def get_planet_id(nombre):
    planeta = Planetas.query.get(nombre)
    if planeta is None:
        return jsonify({"msg": "Planeta no encontrado"}), 404
    return jsonify(planeta.serialize()), 200

@app.route('/users', methods=['GET'])
def all_users():
    usuarios = Usuario.query.all()
    result = [usuario.serialize() for usuario in usuarios]
    return jsonify(result), 200

@app.route('/users/favorites/<email>', methods=['GET'])
def get_user_favorites(email):
    usuario = Usuario.query.get(email)
    if usuario is None:
        return jsonify({"msg": "Usuario no encontrado"}), 404
    
    favoritos_personajes = [personaje.serialize() for personaje in usuario.personajes]
    favoritos_planetas = [planeta.serialize() for planeta in usuario.planetas]
    
    return jsonify({
        "personajes_favoritos": favoritos_personajes,
        "planetas_favoritos": favoritos_planetas
    }), 200

@app.route('/favorite/planet/<nombre_planeta>/<email_usuario>', methods=['POST'])
def add_favorite_planet(nombre_planeta, email_usuario):
    usuario = Usuario.query.get(email_usuario)
    planeta = Planetas.query.get(nombre_planeta)
    
    if usuario is None or planeta is None:
        return jsonify({"msg": "Usuario o Planeta no encontrado"}), 404
    
    if planeta in usuario.planetas:
        return jsonify({"msg": "Planeta ya está en favoritos"}), 400
    
    usuario.planetas.append(planeta)
    db.session.commit()
    return jsonify({"msg": "Planeta añadido a favoritos"}), 200

# [POST] /favorite/people/<int:people_id> - Añade un nuevo people favorito al usuario actual
@app.route('/favorite/people/<nombre_people>/<email_usuario>', methods=['POST'])
def add_favorite_people(nombre_people, email_usuario):
    usuario = Usuario.query.get(email_usuario)
    personaje = Personajes.query.get(nombre_people)
    
    if usuario is None or personaje is None:
        return jsonify({"msg": "Usuario o Personaje no encontrado"}), 404
    
    if personaje in usuario.personajes:
        return jsonify({"msg": "Personaje ya está en favoritos"}), 400
    
    usuario.personajes.append(personaje)
    db.session.commit()
    return jsonify({"msg": "Personaje añadido a favoritos"}), 200


@app.route('/favorite/planet/<nombre_planeta>/<email_usuario>', methods=['DELETE'])
def delete_favorite_planet(nombre_planeta, email_usuario):
    usuario = Usuario.query.get(email_usuario)
    planeta = Planetas.query.get(nombre_planeta)
    
    if usuario is None or planeta is None:
        return jsonify({"msg": "Usuario o Planeta no encontrado"}), 404
    

    if planeta not in usuario.planetas:
        return jsonify({"msg": "Planeta no está en favoritos"}), 400
    
    usuario.planetas.remove(planeta)
    db.session.commit()
    return jsonify({"msg": "Planeta eliminado de favoritos"}), 200


@app.route('/favorite/people/<nombre_people>/<email_usuario>', methods=['DELETE'])
def delete_favorite_people(nombre_people, email_usuario):
    usuario = Usuario.query.get(email_usuario)
    personaje = Personajes.query.get(nombre_people)
    
    if usuario is None or personaje is None:
        return jsonify({"msg": "Usuario o Personaje no encontrado"}), 404
    

    if personaje not in usuario.personajes:
        return jsonify({"msg": "Personaje no está en favoritos"}), 400
    
    usuario.personajes.remove(personaje)
    db.session.commit()
    return jsonify({"msg": "Personaje eliminado de favoritos"}), 200


@app.route('/create_user', methods=['POST'])
def create_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    fecha_suscripcion = data.get('fecha_suscripcion')
    nombre = data.get('nombre')
    apellido = data.get('apellido')

    if Usuario.query.get(email):
        return jsonify({"msg": "Usuario ya existe"}), 400

    new_user = Usuario(
        email=email,
        password=password,
        fecha_suscripcion=fecha_suscripcion,
        nombre=nombre,
        apellido=apellido
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"msg": "Usuario creado exitosamente"}), 201
@app.route('/create_planet', methods=['POST'])
def create_planet():
    data = request.get_json()
    nombre = data.get('nombre')
    galaxia = data.get('galaxia')
    numero_planetas = data.get('numero_planetas')
    habitable = data.get('habitable')

    if Planetas.query.get(nombre):
        return jsonify({"msg": "Planeta ya existe"}), 400

    new_planet = Planetas(
        nombre=nombre,
        galaxia=galaxia,
        numero_planetas=numero_planetas,
        habitable=habitable
    )
    db.session.add(new_planet)
    db.session.commit()
    return jsonify({"msg": "Planeta creado exitosamente"}), 201
@app.route('/create_personaje', methods=['POST'])
def create_personaje():
    data = request.get_json()
    nombre = data.get('nombre')
    edad = data.get('edad')
    planeta_nombre = data.get('planeta_nombre')

    if Personajes.query.get(nombre):
        return jsonify({"msg": "Personaje ya existe"}), 400

    new_personaje = Personajes(
        nombre=nombre,
        edad=edad,
        planeta_nombre=planeta_nombre
    )
    db.session.add(new_personaje)
    db.session.commit()
    return jsonify({"msg": "Personaje creado exitosamente"}), 201

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
