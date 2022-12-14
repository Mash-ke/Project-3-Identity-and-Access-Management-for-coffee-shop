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
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES

@app.after_request
def after_request(response):
    response.headers.add(
        'Access-Control-Allow-Headers',
        'Content-Type, Authorization,true')
    response.headers.add(
        'Access-Control-Allow-Headers',
        'GET,POST,PATCH,PUT,DELETE,OPTIONS')
    return response

'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
     where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks():
    try:
        list_drinks = Drink.query.order_by('id').all()
        drinks = [drink.short() for drink in list_drinks]
        return jsonify({
            "success": True,
            "drinks": drinks
            })
    except BaseException:
        abort(404)
        return jsonify({
            'Success':False,
            'Message':'Not Found'
        })



'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
     where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def drinks_details(payload):
    try:
        drink_details = Drink.query.order_by('id').all()
        drinks = [drinks.long() for drinks in drink_details]
        return jsonify({
            "success": True, 
            "drinks": drinks
            })
    except BaseException:
        abort(404)
        return jsonify({
            'Success':False,
            'Message':'Not Found'
        })

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
     where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods = ['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
    body = request.get_json()
    
    try:
        new_title = body["title"]
        new_recipe = json.dumps(body["recipe"])

        drink = Drink(
            title = new_title,
            recipe = new_recipe
        )

        drink.insert()
        return jsonify({
            "success": True, 
            "drinks": [drink.long()]
            })

    
    except BaseException:
        abort(422)


'''
curl -H "Content-Type: application/json" -X POST
http://127.0.0.1:5000/drinks 
-d "{"title":"soda","recipe":[{"name": "cola", "color": "dark", "parts": 3}]}"
'''
'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
     where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods = ['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(payload, id):
    
    body = request.get_json()
    
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if 'title' in body:
            drink.title = json.dumps(body["title"])

        if 'recipe' in body:
            drink.recipe = json.dumps(body["recipe"])

        drink.update()
        return jsonify({
            "success": True,
            "drinks": [drink.long()]
            })     
    except BaseException:
        abort(422)
        


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id}
    where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods = ['DELETE'])
@requires_auth('delete:drinks')
def del_drink(payload, id):
    try:
        del_drink = Drink.query.filter(
            Drink.id == id).one_or_none()
        if not del_drink:
            abort(404)
        del_drink.delete()
        return jsonify({
            "success": True, 
            "delete": id
            })
    except BaseException:
        abort(422)

# Error Handling
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
@TODO implement error handlers using the @app.errorhandler(error)
 decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
        }),404

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def not_found(AuthError):
    return jsonify({
        "success": False,
        "error": AuthError.status_code,
        "message": AuthError.error
        }),AuthError.status_code
    
@app.errorhandler(403)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "Forbidden Error"
        }),403
    

