import psycopg2
import logging
from psycopg2.extras import RealDictCursor, LoggingConnection

class PGSQL():
    def __init__(self, config):
        self.conn = psycopg2.connect(config["DATABASE_URL"], connection_factory=LoggingConnection)

    def ProductList(self, categoryId, star, discount, priceFrom, priceTo, search, order, sort, limit, offset):
        logging.basicConfig(level=logging.DEBUG)
        logger = logging.getLogger("dev")
        self.conn.initialize(logger)

        filter = "true"
        filterValue = []
        # Handle categoryId
        if categoryId > 0:
            filter += " and p.category_id = %s"
            filterValue.append(categoryId)

        # Handle star
        if star > 0:
            filter += " and p.star = %s"
            filterValue.append(star)

        # Handle discount
        if discount >= 0 and discount <=1:
            filter += " and p.discount = %s"
            filterValue.append(discount)

        # Handle priceFrom
        if priceFrom > 0:
            filter += " and p.price * (1 - p.discount) >= %s"
            filterValue.append(priceFrom)

        # Handle priceTo
        if priceTo > 0:
            filter += " and p.price * (1 - p.discount) <= %s"
            filterValue.append(priceTo)

        # Handle search
        if search != "":
            filter += " and (p.name ilike " + "%s" + " || " + "%s" + " || " + "%s or p.description ilike " + "%s" + " || " + "%s" + " || " + "%s)"
            filterValue.append("%")
            filterValue.append(search)
            filterValue.append("%")
            filterValue.append("%")
            filterValue.append(search)
            filterValue.append("%")

        # Handle order, sort
        filter += " order by " + sort + " " + order

        # Handle limit, offset
        filter += " limit %s offset %s"
        filterValue.append(limit)
        filterValue.append(offset)

        raw = "select p.id, p.name, p.image, p.price::float, p.discount::float, p.price * (1 - p.discount)::float discounted_price, p.star, p.description, p.category_id, count(*) over() total from product p where " + filter
        cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(raw, filterValue)
            return cursor.fetchall(), None
        except psycopg2.Error as e:
            return None, str(e)
        finally:
            cursor.close()        
