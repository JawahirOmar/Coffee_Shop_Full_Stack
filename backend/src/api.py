import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()


# GET drinks
@app.route('/drinks', methods=['GET'])
def get_drink():
    selection = Drink.query.order_by(Drink.id).all()
    drinks = list(map(Drink.short, selection))
    return jsonify({
        "success": True,
        "drinks": drinks
    })


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detalis():
    selection = Drink.query.order_by(Drink.id).all()
    drinks = list(map(Drink.long, selection))
    return jsonify({
        "success": True,
        "drinks": drinks
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(token):
    if request.data:
        new_drink = json.loads(request.data.decode('utf-8'))
        title = new_drink['title']
        recipe = json.dumps(new_drink['recipe'])
        new_drink = Drink(title=title, recipe=recipe)
        new_drink.insert()
        selection = Drink.query.order_by(Drink.id).all()
        drinks = list(map(Drink.long, selection))
        return jsonify({
            'success': True,
            'drinks': drinks
        })


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks():
    drink = Drink.query.get(id)
    if not drink:
        return abort(404)
    body = request.get_json()
    title = body.get_json('title', None)
    recipe = body.get_json('recipe', None)
    if title:
        drink.title = title
    if recipe:
        drink.recipe = recipe

    drink.update()
    selection = Drink.query.order_by(Drink.id).all()
    drinks = list(map(Drink.long, selection))
    return jsonify({
        'success': True,
        'drinks': drinks
    })


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink():
    drink = Drink.query.get(id)
    if not drink:
        return abort(404)
    drink.delete()
    selection = Drink.query.order_by(Drink.id).all()
    drinks = list(map(Drink.long, selection))
    return jsonify({
        'success': True,
        "delete": drink
    })

# Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def notfound(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource_not_found"
    })


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify(error.error), error.status_code
