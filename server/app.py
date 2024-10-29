#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_migrate import Migrate
from models import db, Hero, Power, HeroPower


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

@app.route('/heroes', methods = ['GET'])
def get_all_heroes():
    heroes = Hero.query.all()
    
    response = [{
        'id':hero.id,
        'name':hero.name,
        'super_name':hero.super_name
    } for hero in heroes]

    return make_response(response, 200) 

@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero_by_id(id):
    hero = Hero.query.filter(Hero.id == id).first()
    
    if hero:
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
        return make_response(response, 200)
    else:
        return make_response({'error': 'Hero not found'}, 404)


@app.route('/powers', methods = ['GET'])
def get_all_powers():
    response = [ {
        'description': power.description,
        'id': power.id,
        'name': power.name
    } for power in Power.query.all()]

    return make_response(response, 200)

@app.route('/powers/<int:id>', methods=['PATCH', 'GET'])
def get_power_by_id(id):
    power = Power.query.filter(Power.id == id).first()

    if request.method == 'GET':
        if power:
            response = {
                'description': power.description,
                'id': power.id,
                'name': power.name
            }
            return make_response(response, 200)
        else:
            response = {
                'error': 'Power not found'
            }
            return make_response(response, 404)

    elif request.method == 'PATCH':
        if not request.is_json:
            response = {
                'error': 'Invalid request. Content-Type must be application/json.'
            }
            return make_response(response, 400)
        else:
            if power:
                data = request.get_json()
                if len(data['description']) < 20:
                    response = {
                        'errors' : ["validation errors"]
                    }

                    return make_response(response, 400)
                else:
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
                response = {
                    'error': 'Power not found'
                }

                return make_response(response, 404)
        ...


    
@app.route('/hero_powers', methods = ['POST'])
def get_hero_powers():
    data = request.get_json()

    if data['strength'] not in ['Strong', 'Weak', 'Average']:
        response = {
            'errors': ['validation errors']
        }

        return make_response(response, 400)
    else:
        hero = HeroPower(
            strength = data['strength'],
            power_id = data['power_id'],
            hero_id   =  data['hero_id']
        )

        db.session.add(hero)
        db.session.commit()


    if hero:
        response = {
                'id' : hero.id,
                'hero_id' : hero.hero_id,
                'power_id' : hero.power_id,
                'strength' : hero.strength,
                'hero': {
                        'id': hero.hero.id,
                        'name': hero.hero.name,
                        'super_name':hero.hero.super_name
                    },
                'power': {
                        'description': hero.power.description,
                        'id' : hero.power.id,
                        'name': hero.power.name
                    }
                }
    
        return make_response(response, 200)

    


        


if __name__ == '__main__':
    app.run(port=5550, debug=True)