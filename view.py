from flask import Flask, render_template, request

import db

app = Flask(__name__)


@app.route('/')
def main():
    location = request.args.get('location')
    price = request.args.get('price')
    bedrooms = request.args.get('bedrooms')
    meters = request.args.get('meters')
    is_ready = request.args.get('is_ready')
    apart_type = request.args.get('apart_type')
    offers = db.get_apartment_offers(location, price, bedrooms, meters, is_ready, apart_type)
    return render_template('index.html', offers=offers['obj'])


if __name__ == '__main__':
    app.run()
