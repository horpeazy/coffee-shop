import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth, PermissionError

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

# ROUTES


@app.route('/drinks')
def get_drinks():
    try:
        drinks = [d.short() for d in Drink.query.all()]
    except Exception:
        abort(404)

    return jsonify({
        "success": True,
        "drinks": drinks
    }), 200


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drink_detail():
    try:
        drinks = [d.long() for d in Drink.query.all()]
    except Exception:
        abort(404)

    return jsonify({
        "success": True,
        "drinks": drinks
    }), 200


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink():
    data = request.get_json()
    title = data.get('title', None)
    recipe = data.get('recipe', None)
    print(title)
    new_recipe = [{"color": recipe["color"],
                   "name": recipe["name"],
                   "parts": recipe["parts"]}]

    try:
        drink = Drink(
            title=title,
            recipe=json.dumps(new_recipe)
        )

        drink.insert()
    except Exception:
        abort(422)

    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    })


@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(id):
    drink = Drink.query.filter_by(id=id).one_or_none()

    if drink is None:
        abort(404)

    try:
        data = request.get_json()
        drink.title = data.get('title', None)
        drink.recipe = json.dumps(data.get('recipe', None))
        drink.update()
    except Exception:
        abort(422)

    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    }), 200


@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(id):
    drink = Drink.query.filter_by(id=id).one_or_none()

    if drink is None:
        abort(404)

    try:
        drink.delete()
    except Exception:
        abort(422)

    return jsonify({
        "success": True,
        "delete": id
    }), 200


# Error Handlingle error handling for unprocessable entity


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Not found"
    }), 404


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error"
    }), 500


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Unauthorized access"
    }), 401


@app.errorhandler(PermissionError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "Permission Denied"
    }), 403


if __name__ == "__main__":
    app.debug = True
    app.run()
