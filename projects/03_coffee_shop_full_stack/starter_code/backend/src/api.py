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

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def all_drinks():
    drinks = Drink.query.all()

    if len(drinks) == 0:
        abort(404)

    try:
        formatted_drinks = [drink.short() for drink in drinks]

        return jsonify({
           "success": True,
            "drinks": formatted_drinks
        }), 200

    except Exception:
        abort(422)

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def all_drinks_with_detail(payload):
    drinks = Drink.query.all()

    if drinks == 0:
        abort(404)

    try:
        formatted_drinks = [drink.long() for drink in drinks]

        return jsonify({
           "success": True,
            "drinks": formatted_drinks
        }), 200

    except Exception:
        abort(422)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_new_drinks(payload):
    body = request.get_json()

    new_title = body.get('title')
    count_title = len(new_title)

    if count_title == 0:
        abort(422)

    new_recipe = json.dumps(body.get('recipe'))

    try:
        drink = Drink(title = new_title, recipe = new_recipe)
        drink.insert()

        return jsonify({
            "success": True,
             "drinks": drink.long()
        }), 200

    except Exception:
        abort(500)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drinks(payload, id):
    body = request.get_json()

    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if drink is None:
        abort(404)

    try:
        if body.get('title'): 
            drink.title = body.get('title', None)
        
        if body.get('recipe'):
            drink.recipe = json.dumps(body.get('recipe', None))

        drink.update()

        return jsonify({
            "success": True,
            "drink": drink.long()
        }), 200

    except Exception:
        abort(422)

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if drink is None:
        abort(404)

    try:
        drink.delete()

        return jsonify({
            "success": True,
             "delete": drink.id
        }), 200

    except Exception:
        abort(422)

## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False, 
        "error": 422,
        "message": "unprocessable"
    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False, 
        "error": 500,
        "message": "Internal Server Error"
    }), 500
'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "resource not found"
    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response
