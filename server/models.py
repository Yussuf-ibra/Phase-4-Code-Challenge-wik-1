from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData()

db = SQLAlchemy(metadata=metadata)


class Hero(db.Model, SerializerMixin):
    __tablename__ = 'heroes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    super_name = db.Column(db.String)

    powers = association_proxy('hero_powers', 'power', creator=lambda power_obj: HeroPower(power=power_obj))
    hero_powers = db.relationship('HeroPower', back_populates='hero', cascade='all, delete-orphan')

    serialize_rules = ('-hero_powers.hero', '-hero_powers.power')

    def __repr__(self):
        return f'<Hero {self.id} - {self.name}>'


class Power(db.Model, SerializerMixin):
    __tablename__ = 'powers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)

    hero_powers = db.relationship('HeroPower', back_populates='power', cascade='all, delete-orphan')
    heroes = association_proxy('hero_powers', 'hero', creator=lambda hero_obj: HeroPower(hero=hero_obj))

    serialize_rules = ('-hero_powers.power',)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.validate_length()

    def validate_length(self):
        if len(self.description) < 20:
            raise ValueError('Description must be at least 20 characters long')

    

    def __repr__(self):
        return f'<Power {self.id} - {self.name}>'


class HeroPower(db.Model, SerializerMixin):
    __tablename__ = 'hero_powers'

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String, nullable=False)
    hero_id = db.Column(db.Integer, db.ForeignKey('heroes.id'), nullable=False)
    power_id = db.Column(db.Integer, db.ForeignKey('powers.id'), nullable=False)

    hero = db.relationship('Hero', back_populates='hero_powers')
    power = db.relationship('Power', back_populates='hero_powers')

    serialize_rules = ('-hero.hero_powers', 'power.hero_powers')
    VALID_STRENGTHS = ['Strong', 'Weak', 'Average']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.validate_strength()

    def validate_strength(self):
        if self.strength not in self.VALID_STRENGTHS:
            raise ValueError('Strength is not a valid option')
        
    def __repr__(self):
        return f'<HeroPower {self.id} - Strength: {self.strength}>'