from flask import Flask, jsonify, request, abort

import db_manager

app = Flask(__name__)


def run_app():
    app.run(debug=False)


@app.route('/orders', methods=['GET'])
def get_orders():
    limit = 100
    with db_manager.DBManager() as db:
        if 'limit' in request.args and 'from' in request.args:
            limit = request.args['limit']
            from_date = request.args['from']
            return jsonify(db.get_orders_from(from_date, limit))
        elif 'limit' in request.args:
            limit = request.args['limit']
            return jsonify(db.get_last_orders(limit))
        elif 'from' and 'to' in request.args:
            from_date = request.args['from']
            to_date = request.args['to']
            return jsonify(db.get_orders_from_to(from_date, to_date))
        elif 'from' in request.args:
            from_date = request.args['from']
            return jsonify(db.get_orders_from(from_date, limit))

        return jsonify(db.get_last_orders(limit))


@app.route('/order/<string:order_id>', methods=['GET'])
def get_order(order_id):
    with db_manager.DBManager() as db:
        response = db.get_order_by_id(order_id)
        return jsonify(response) if response else abort(404)


@app.route('/buyers', methods=['GET'])
def get_buyers():
    limit = 100
    with db_manager.DBManager() as db:
        if 'limit' in request.args and 'from' in request.args:
            limit = request.args['limit']
            from_date = request.args['from']
            return jsonify(db.get_buyers_from(from_date, limit))
        elif 'limit' in request.args:
            limit = request.args['limit']
            return jsonify(db.get_last_buyers(limit))
        elif 'from' and 'to' in request.args:
            from_date = request.args['from']
            to_date = request.args['to']
            return jsonify(db.get_buyers_from_to(from_date, to_date))
        elif 'from' in request.args:
            from_date = request.args['from']
            return jsonify(db.get_buyers_from(from_date, limit))

        return jsonify(db.get_last_buyers(limit))


@app.route('/buyer/<string:buyer_id>', methods=['GET'])
def get_buyer(buyer_id):
    with db_manager.DBManager() as db:
        response = db.get_buyer_by_id(buyer_id)
        return jsonify(response) if response else abort(404)


@app.route('/buyer/orders/<string:buyer_id>', methods=["GET"])
def get_buyer_orders(buyer_id):
    with db_manager.DBManager() as db:
        response = db.get_buyer_orders(buyer_id)
        return jsonify(response) if response else abort(404)


@app.route('/delivery/<string:buyer_id>', methods=['GET'])
def get_delivery_address(buyer_id):
    with db_manager.DBManager() as db:
        data = db.get_buyer_delivery_addresses(buyer_id)
        return jsonify(data) if data else abort(404)


@app.route('/items/<string:order_id>', methods=['GET'])
def get_order_items(order_id):
    with db_manager.DBManager() as db:
        data = db.get_order_items(order_id)
        return jsonify(data) if data else abort(404)


if __name__ == '__main__':
    run_app()
