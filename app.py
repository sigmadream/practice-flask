from flask import Flask, jsonify, request
from flask_restful import Resource, Api, reqparse
from flask_jwt_extended import JWTManager, create_access_token, jwt_required


app = Flask(__name__)
app.secret_key = "sangkon"
api = Api(app)

jwt = JWTManager(app)

items = []


@app.route("/login", methods=["POST"])
def login():
    from security import authenticate

    username = request.json.get("username", None)
    password = request.json.get("password", None)
    user = authenticate(username, password)
    if not user or not user.password == password:
        return jsonify("Wrong username or password"), 401
    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token)


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "price", type=float, required=True, help="This field cannot be left blank!"
    )

    @jwt_required()
    def get(self, name):
        item = next(filter(lambda x: x["name"] == name, items), None)
        return {"item": item}, 200 if items else 404

    def post(self, name):
        if next(filter(lambda x: x["name"] == name, items), None):
            return {"message": f"An item with name {name} already exists."}, 400

        data = Item.parser.parse_args()

        item = {"name": name, "price": data["price"]}
        items.append(item)
        return item, 201

    @jwt_required()
    def delete(self, name):
        global items
        items = list(filter(lambda x: x["name"] != name, items))
        return {"message": "Item deleted"}

    def put(self, name):
        data = Item.parser.parse_args()
        item = next(filter(lambda x: x["name"] == name, items), None)

        if item is None:
            item = {"name": name, "price": data["price"]}
            items.append(item)
        else:
            items.update(data)
        return item


class ItemList(Resource):
    def get(self):
        return {"items": items}


api.add_resource(Item, "/item/<string:name>")
api.add_resource(ItemList, "/items")

if __name__ == "__main__":
    app.run(debug=True)
