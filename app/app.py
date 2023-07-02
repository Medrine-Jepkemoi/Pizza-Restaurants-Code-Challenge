#!/usr/bin/env python3

from flask import Flask, make_response, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource

from models import db, Restaurant, Pizza, RestaurantPizza

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route('/')
def home():
    return ''


class RestaurantResource(Resource):
    def get(self):


        restaurants = Restaurant.query.all()
        serialized_restaurants = [
            {
                'id': restaurant.id,
                'name': restaurant.name,
                'address': restaurant.address
            }
            for restaurant in restaurants
        ]
        response = make_response(jsonify(serialized_restaurants))
        response.headers['Content-Type'] = 'application/json'
        return response


api.add_resource(RestaurantResource, '/restaurants')


# @app.route('/restaurants', methods=['GET'])
# def get_restaurants():
#     restaurants = Restaurant.query.all()
#     return jsonify([{
#         "id": restaurant.id,
#         "name": restaurant.name,
#         "address": restaurant.address,
#     } for restaurant in restaurants])


class RestaurantResource(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            response = make_response(jsonify({"error": "Restaurant not found"}), 404)
        else:
            serialized_restaurant = {
                'id': restaurant.id,
                'name': restaurant.name,
                'address': restaurant.address,
                'pizzas': [
                    {
                        'id': pizza.id,
                        'name': pizza.name,
                        'ingredients': pizza.ingredients
                    }
                    for pizza in restaurant.pizzas
                ]
            }
            response = make_response(jsonify(serialized_restaurant))
        response.headers['Content-Type'] = 'application/json'
        return response
    
    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            response = make_response(jsonify({"error": "Restaurant not found"}), 404)
        else:
            RestaurantPizza.query.filter_by(restaurant_id=id).delete()
            db.session.delete(restaurant)
            db.session.commit()
            response = make_response('', 204)
        return response


api.add_resource(RestaurantResource, '/restaurants/<int:id>')


# @app.route('/restaurants/<int:id>', methods=['GET'])
# def get_restaurant(id):
#     restaurant = Restaurant.query.get(id)
#     if not restaurant:
#         return jsonify({"error": "Restaurant not found"}), 404

#     return jsonify({
#         "id": restaurant.id,
#         "name": restaurant.name,
#         "address": restaurant.address,
#         "pizzas": [{
#             "id": pizza.id,
#             "name": pizza.name,
#             "ingredients": pizza.ingredients,
#         } for pizza in restaurant.pizzas]
#     })



# @app.route('/restaurants/<int:id>', methods=['DELETE'])
# def delete_restaurant(id):
#     restaurant = Restaurant.query.get(id)
#     if not restaurant:
#         return jsonify({"error": "Restaurant not found"}), 404

#     RestaurantPizza.query.filter_by(restaurant_id=id).delete()
#     db.session.delete(restaurant)
#     db.session.commit()

#     return '', 204


class PizzaResource(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        serialized_pizzas = [
            {
                "id": pizza.id,
                "name": pizza.name,
                "ingredients": pizza.ingredients,
            }
            for pizza in pizzas
        ]
        response = make_response(jsonify(serialized_pizzas), 200)
        return response


api.add_resource(PizzaResource, '/pizzas')


# @app.route('/pizzas', methods=['GET'])
# def get_pizzas():
#     pizzas = Pizza.query.all()
#     return jsonify([{
#         "id": pizza.id,
#         "name": pizza.name,
#         "ingredients": pizza.ingredients,
#     } for pizza in pizzas])


class RestaurantPizzaResource(Resource):
    def post(self):
        data = request.get_json()
        price = data.get('price')
        pizza_id = data.get('pizza_id')
        restaurant_id = data.get('restaurant_id')

        if not price or not pizza_id or not restaurant_id:
            response = make_response(jsonify({"errors": ["Missing required fields"]}), 400)
            return response

        pizza = Pizza.query.get(pizza_id)
        restaurant = Restaurant.query.get(restaurant_id)

        if not pizza or not restaurant:
            response = make_response(jsonify({"errors": ["Pizza or restaurant not found"]}), 404)
            return response

        restaurant_pizza = RestaurantPizza(price=price, pizza=pizza, restaurant=restaurant)
        db.session.add(restaurant_pizza)
        db.session.commit()

        serialized_pizza = {
            "id": pizza.id,
            "name": pizza.name,
            "ingredients": pizza.ingredients,
        }

        response = make_response(jsonify(serialized_pizza), 201)
        return response


api.add_resource(RestaurantPizzaResource, '/restaurant_pizzas')

# @app.route('/restaurant_pizzas', methods=['POST'])
# def create_restaurant_pizza():
#     data = request.get_json()
#     price = data.get('price')
#     pizza_id = data.get('pizza_id')
#     restaurant_id = data.get('restaurant_id')

#     if not price or not pizza_id or not restaurant_id:
#         return jsonify({"errors": ["Missing required fields"]}), 400

#     pizza = Pizza.query.get(pizza_id)
#     restaurant = Restaurant.query.get(restaurant_id)

#     if not pizza or not restaurant:
#         return jsonify({"errors": ["Pizza or restaurant not found"]}), 404

#     restaurant_pizza = RestaurantPizza(price=price, pizza=pizza, restaurant=restaurant)
#     db.session.add(restaurant_pizza)
#     db.session.commit()

#     return jsonify({
#         "id": pizza.id,
#         "name": pizza.name,
#         "ingredients": pizza.ingredients,
#     }), 201


if __name__ == '__main__':
    app.run(port=5555)
