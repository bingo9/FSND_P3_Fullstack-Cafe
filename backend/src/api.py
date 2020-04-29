import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

# SETUP FLASK APP
app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''


db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {'success': True, 'drinks': drinks}
        where drinks is the list of drinks or appropriate status code
        indicating reason for failure
'''


@app.route('/drinks')
def get_drinks():

    # Get the stored list of drinks
    drinks = list(map(Drink.short, Drink.query.all()))

    # Return the result
    result = {
        'success': True,
        'drinks': drinks
    }
    return jsonify(result)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {'success': True, 'drinks': drinks}
        where drinks is the list of drinks or appropriate status code
        indicating reason for failure
'''


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(token):

    # Get the stored list of drinks and their details
    drinks = list(map(Drink.long, Drink.query.all()))

    # Return the result
    result = {
        'success': True,
        'drinks': drinks
    }
    return jsonify(result)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {'success': True, 'drinks': drink}
        where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(token):
    if request.data:

        # Load and deserialize the data
        new_drink = json.loads(request.data.decode('utf-8'))

        # Create new drink
        drink = Drink(title=new_drink['title'], recipe=json.dumps(
            new_drink['recipe']))
        drink.insert()

        # Update the list of drinks to return with newly added
        drinks = list(map(Drink.long, Drink.query.all()))

        # Return the result
        result = {
            'success': True,
            'drinks': drinks
        }
        return jsonify(result)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {'success': True, 'drinks': drink}
        where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks/<drink_id>", methods=['PATCH'])
@requires_auth("patch:drinks")
def edit_drink(token, drink_id):

    # Load and deserialize the data
    new_drink = json.loads(request.data.decode('utf-8'))
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    # If no drink id found abort 404 - resource not found
    if drink is None:
        abort(404)

    # Replace the title of the drink with the new title
    if 'title' in new_drink:
        drink.title = new_drink['title']

    # Replace the recipe of the drink with the new recipe
    if 'recipe' in new_drink:
        drink.recipe = json.dumps(new_drink['recipe'])

    # Update the drink in the database
    drink.update()

    # Update the list of drinks to return with newly modified
    drinks = list(map(Drink.long, Drink.query.all()))

    # Return the result
    result = {
        'success': True,
        'drinks': drinks
    }
    return jsonify(result)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {'success': True, 'delete': id}
        where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(token, drink_id):

    # Find the specified drink to delete
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    # If no drink id found abort 404 - resource not found
    if drink is None:
        abort(404)

    # Delete the drink
    drink.delete()

    # Update the list of drinks to return, after specified deleted
    drinks = list(map(Drink.long, Drink.query.all()))

    # Return the result
    result = {
        'success': True,
        'drinks': drinks
    }
    return jsonify(result)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        'success': False,
        'error': 422,
        'message': 'unprocessable'
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return(with approprate messages):
             jsonify({
                    'success': False,
                    'error': 404,
                    'message': 'resource not found'
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'resource not found'
    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def auth_error(e):
    return jsonify(e.error), e.status_code
