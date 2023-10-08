import os
import dotenv
import psycopg2


def get_apartment_offers(location, price, bedrooms, meters, is_ready, apart_type):
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM items WHERE price<=%s AND bedrooms>=%s AND meters>=%s AND type=%s AND location LIKE %s",
        (price, bedrooms, meters, apart_type, location))
    elements = cur.fetchall()
    conn.close()
    return {'is_ok': True, 'obj': elements}
