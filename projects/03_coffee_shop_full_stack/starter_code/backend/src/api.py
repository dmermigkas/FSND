import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
cors = CORS(app, resources={r"*": {"origins": "*"}})

#https://fsndcoffee.eu.auth0.com/authorize?audience=Coffee&response_type=token&client_id=wX2tfu7Z2F3ew0o8SbQKvC0l7mlnFF6K&redirect_uri=http://localhost:5000/results
# https://fsndcoffee.eu.auth0.com/login?state=g6Fo2SBubEt3ZGkzMC1zWWQ3eDdUZ1R3d2RBcnRTRXJ1LXduZaN0aWTZIGRSb20tLUZqUHVuZW84WUVzWk5EVm9CVTd6WkJWYm9ko2NpZNkgd1gydGZ1N1oyRjNldzBvOFNiUUt2QzBsN21sbkZGNks&client=wX2tfu7Z2F3ew0o8SbQKvC0l7mlnFF6K&protocol=oauth2&audience=Coffee&response_type=token&redirect_uri=http%3A%2F%2Flocalhost%3A8100%2Ftabs%2Fuser-page

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES

@app.route('/drinks')
def get_drinks():
    try:
        all_drinks = Drink.query.all()
        drinks = [drink.short() for drink in all_drinks]
        if len(drinks) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'drinks': drinks
        })
    except ValueError:
        abort(400)

'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    try:
        all_drinks = Drink.query.all()
        drinks = [drink.short() for drink in all_drinks]
        if len(drinks) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'drinks': drinks
        })
    except ValueError:
        abort(400)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(jwt):

    body = request.get_json()
    try:
        drink = Drink(title=body.get('title'), recipe=json.dumps(body.get('recipe')))
        drink.insert()
        print(drink.long(), 'my drinkkkk')
        return jsonify({
            'success': True,
            'drinks': drink.long()
        })
    except ValueError:
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

@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(jwt, id):
    
    body = request.get_json()
    drink = Drink.query.filter(Drink.id == id).one()

    try:
      drink.title = body.get('title')
      drink.recipe = json.dumps(body.get('recipe'))
      drink.update()
      return jsonify({
        'success': True,
        'drinks': [drink.long()]
      })
    except e as Exception:
      abort(404)

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

@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(jwt, id):
    
    drink = Drink.query.filter(Drink.id == id).one()

    try:
      drink.delete()
      return jsonify({
        'success': True,
        'delete': id
      })
    except e as Exception:
      abort(404)

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


## Error Handling
'''
Example error handling for unprocessable entity
'''

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''

@app.errorhandler(400)
def not_found(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'Bad Request'
    }), 400

@app.errorhandler(401)
def not_authorized(error):
    return jsonify({
      'success': False,
      'error': 401,
      'message': 'Not Authorized'
    }), 401

@app.errorhandler(404)
def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'Not found'
    }), 404

@app.errorhandler(422)
def unproccessable(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'Unprocessable Entity'
    }), 422

@app.errorhandler(500)
def unproccessable(error):
    return jsonify({
      'success': False,
      'error': 500,
      'message': 'Internal Server Error'
    }), 500
