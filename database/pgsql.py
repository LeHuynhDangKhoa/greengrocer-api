import psycopg2
# import logging
from psycopg2.extras import RealDictCursor, LoggingConnection

class PGSQL():
    def __init__(self, config):
        # self.conn = psycopg2.connect(config["DATABASE_URL"], connection_factory=LoggingConnection)
        self.conn = psycopg2.connect(config["DATABASE_URL"])

    def ProductList(self, categoryId, star, discount, priceFrom, priceTo, search, order, sort, limit, offset):
        # logging.basicConfig(level=logging.DEBUG)
        # logger = logging.getLogger("dev")
        # self.conn.initialize(logger)

        filter = "true"
        filterValue = []
        # Handle categoryId
        if categoryId != None:
            filter += " and c.name = %s"
            filterValue.append(categoryId)

        # Handle star
        if star != None:
            filter += " and p.star = %s"
            filterValue.append(star)

        # Handle discount
        if discount != None:
            if discount == 1:
                filter += " and p.discount > %s"
                filterValue.append(0)

        # Handle priceFrom
        if priceFrom != None:
            filter += " and p.price * (1 - p.discount) >= %s"
            filterValue.append(priceFrom)

        # Handle priceTo
        if priceTo != None:
            filter += " and p.price * (1 - p.discount) <= %s"
            filterValue.append(priceTo)

        # Handle search
        if search != None:
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

        raw = "select p.id, p.name, p.image, p.price::float, p.discount::float, p.price * (1 - p.discount)::float discounted_price, p.star, p.description, p.category_id, count(*) over() total from product p left join category c on c.id = p.category_id where " + filter
        cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(raw, filterValue)
            return cursor.fetchall(), None
        except psycopg2.Error as e:
            return None, str(e)
        finally:
            cursor.close()        

    def CategoryList(self):
        raw = "select c.id, c.name, count(p.category_id) total from category c left join product p on c.id = p.category_id group by p.category_id, c.id, c.name"
        cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(raw)
            return cursor.fetchall(), None
        except psycopg2.Error as e:
            return None, str(e)
        finally:
            cursor.close()

    def GetProductById(self, id):
        raw = "select p.id, p.name, p.image, p.price::float, p.discount::float, p.price * (1 - p.discount)::float discounted_price, p.star, p.description, p.category_id from product p where id = %s"
        value = []
        value.append(id)
        cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(raw, value)
            return cursor.fetchone(), None
        except psycopg2.Error as e:
            return None, str(e)
        finally:
            cursor.close()

    def GetUserByUsername(self, username):
        raw = 'select * from "user" where username = %s'
        value = [username]
        cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(raw, value)
            return cursor.fetchone(), None
        except psycopg2.Error as e:
            return None, str(e)
        finally:
            cursor.close()

    def InsertNewUser(self, values):
        raw = 'insert into "user" (username, password, phone, email, image, role) VALUES (%s, %s, %s, %s, %s, %s)'
        cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(raw, values)
            self.conn.commit()
            return None
        except psycopg2.Error as e:
            return str(e)
        finally:
            cursor.close()