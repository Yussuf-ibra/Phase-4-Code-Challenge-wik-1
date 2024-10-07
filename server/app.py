#!/usr/bin/env python3

# Import necessary libraries,
from flask import Flask, request, make_response
from flask_migrate import Migrate
from models import db, Hero, Power, HeroPower

# Create a Flask application instance
app = Flask(__name__)

# Configure the application to use a SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable track modifications for performance
app.json.compact = False  # Disable compact JSON formatting

# Initialize Flask-Migrate for handling database migrations
migrate = Migrate(app, db)

# Initialize the database with the application
db.init_app(app)

@app.route('/')
def index():
    # Define the index route, returning a simple HTML message
    return '<h1>Code challenge</h1>'

@app.route('/heroes', methods=['GET'])
def get_all_heroes():
    # Retrieve all heroes from the database
    heroes = Hero.query.all()
    
    # Create a response containing the list of heroes
    response = [{
        'id': hero.id,
        'name': hero.name,
        'super_name': hero.super_name
    } for hero in heroes]

    # Return the response with a 200 OK status
    return make_response(response, 200) 

@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero_by_id(id):
    # Retrieve a hero by its ID
    hero = Hero.query.filter(Hero.id == id).first()
    
    if hero:
        # Create a response with hero details and associated powers
        response = {
            'id': hero.id,
            'name': hero.name,
            'super_name': hero.super_name,
            'hero_powers': [{
                'hero_id': hp.hero_id,
                'id': hp.id,
                'power': {
                    'description': power.description,
                    'id': power.id,
                    'name': power.name
                },  
                'power_id': hp.power_id,
                'strength': hp.strength
            } for hp in hero.hero_powers for power in hero.powers if power.id == hp.power_id]  
        }
        # Return the hero response with a 200 OK status
        return make_response(response, 200)
    else:
        # Return an error response if the hero is not found
        return make_response({'error': 'Hero not found'}, 404)

@app.route('/powers', methods=['GET'])
def get_all_powers():
    # Retrieve all powers from the database
    response = [{
        'description': power.description,
        'id': power.id,
        'name': power.name
    } for power in Power.query.all()]

    # Return the powers response with a 200 OK status
    return make_response(response, 200)

@app.route('/powers/<int:id>', methods=['PATCH', 'GET'])
def get_power_by_id(id):
    # Retrieve a power by its ID
    power = Power.query.filter(Power.id == id).first()

    if request.method == 'GET':
        if power:
            # Return the power details with a 200 OK status
            response = {
                'description': power.description,
                'id': power.id,
                'name': power.name
            }
            return make_response(response, 200)
        else:
            # Return an error response if the power is not found
            response = {
                'error': 'Power not found'
            }
            return make_response(response, 404)

    elif request.method == 'PATCH':
        # Check if the request is JSON
        if not request.is_json:
            response = {
                'error': 'Invalid request. Content-Type must be application/json.'
            }
            return make_response(response, 400)
        else:
            if power:
                # Validate the incoming data for updating the power description
                data = request.get_json()
                if len(data['description']) < 20:
                    response = {
                        'errors': ["validation errors"]
                    }
                    return make_response(response, 400)
                else:
                    # Update the power's description and commit to the database
                    power.description = data['description']
                    db.session.add(power)
                    db.session.commit()

                    response = {
                        'description': power.description,
                        'id': power.id,
                        'name': power.name
                    }

                    return make_response(response, 200)
            else:
                # Return an error response if the power is not found
                response = {
                    'error': 'Power not found'
                }
                return make_response(response, 404)

@app.route('/hero_powers', methods=['POST'])
def get_hero_powers():
    # Get the data from the request
    data = request.get_json()

    # Validate the strength value
    if data['strength'] not in ['Strong', 'Weak', 'Average']:
        response = {
            'errors': ['validation errors']
        }
        return make_response(response, 400)
    else:
        # Create a new HeroPower instance and save it to the database
        hero = HeroPower(
            strength=data['strength'],
            power_id=data['power_id'],
            hero_id=data['hero_id']
        )

        db.session.add(hero)
        db.session.commit()

    if hero:
        # Create and return the response for the newly created hero power
        response = {
            'id': hero.id,
            'hero_id': hero.hero_id,
            'power_id': hero.power_id,
            'strength': hero.strength,
            'hero': {
                'id': hero.hero.id,
                'name': hero.hero.name,
                'super_name': hero.hero.super_name
            },
            'power': {
                'description': hero.power.description,
                'id': hero.power.id,
                'name': hero.power.name
            }
        }

        return make_response(response, 200)

# Run the application
if __name__ == '__main__':
    app.run(port=5550, debug=True)
