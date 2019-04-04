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
        if response:
            return jsonify(response)
        abort(404)


@app.route('/buyer/<string:buyer_id>', methods=['GET'])
def get_buyer(buyer_id):
    with db_manager.DBManager() as db:
        response = db.get_buyer_by_id(buyer_id)
        if response:
            return jsonify(response)
        abort(404)


if __name__ == '__main__':
    run_app()
