import psycopg2
# import logging
from psycopg2.extras import RealDictCursor, LoggingConnection
from psycopg2 import pool

class PGSQL():
    def __init__(self, config):
        # self.conn = psycopg2.connect(config["DATABASE_URL"], connection_factory=LoggingConnection)
        try: 
            self.pool = pool.ThreadedConnectionPool(1, 50, config["DATABASE_URL"])
            if self.pool :
                print("Connection pool created successfully using ThreadedConnectionPool")
        except (Exception, psycopg2.DatabaseError) as error:
                print("Error while connecting to PostgreSQL", error)
        # self.conn = psycopg2.connect(config["DATABASE_URL"])
        # self.conn.autocommit = True
        # self.conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    def ProductList(self, category, star, discount, priceFrom, priceTo, search, order, sort, limit, offset):
        # logging.basicConfig(level=logging.DEBUG)
        # logger = logging.getLogger("dev")
        # self.conn.initialize(logger)

        filter = "true"
        filterValue = []
        # Handle categoryId
        if category != None:
            filter += " and c.name = %s"
            filterValue.append(category)

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
        conn = self.pool.getconn()
        # conn.autocommit = True
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(raw, filterValue)
            return cursor.fetchall(), None
        except psycopg2.Error as e:
            return None, str(e)
        finally:
            cursor.close()
            self.pool.putconn(conn)        

    def CategoryList(self):
        raw = "select c.id, c.name, count(p.category_id) total from category c left join product p on c.id = p.category_id group by p.category_id, c.id, c.name"
        conn = self.pool.getconn()
        # conn.autocommit = True
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(raw)
            return cursor.fetchall(), None
        except psycopg2.Error as e:
            return None, str(e)
        finally:
            cursor.close()
            self.pool.putconn(conn)

    def GetProductById(self, id):
        raw = "select p.id, p.name, p.image, p.price::float, p.discount::float, p.price * (1 - p.discount)::float discounted_price, p.star, p.description, p.category_id from product p where id = %s"
        value = []
        value.append(id)
        conn = self.pool.getconn()
        # conn.autocommit = True
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(raw, value)
            return cursor.fetchone(), None
        except psycopg2.Error as e:
            return None, str(e)
        finally:
            cursor.close()
            self.pool.putconn(conn)

    def GetUserByUsername(self, username):
        raw = 'select * from "user" where username = %s'
        value = [username]
        conn = self.pool.getconn()
        conn.autocommit = True
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(raw, value)
            return cursor.fetchone(), None
        except psycopg2.Error as e:
            return None, str(e)
        finally:
            cursor.close()
            self.pool.putconn(conn)

    def InsertNewUser(self, values):
        raw = 'insert into "user" (username, password, phone, email, image, role) VALUES (%s, %s, %s, %s, %s, %s)'
        conn = self.pool.getconn()
        # conn.autocommit = True
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(raw, values)
            conn.commit()
            return None
        except psycopg2.Error as e:
            return str(e)
        finally:
            cursor.close()
            self.pool.putconn(conn)

    def GetUserById(self, id):
        raw = 'select * from "user" where id = %s'
        value = [id]
        conn = self.pool.getconn()
        conn.autocommit = True
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(raw, value)
            return cursor.fetchone(), None
        except psycopg2.Error as e:
            return None, str(e)
        finally:
            cursor.close()
            self.pool.putconn(conn)

    def UpdateUser(self, user):
        raw = 'update "user" set username = %s, phone = %s, email = %s, image = %s, role = %s where id = %s'
        values = [user["username"], user["phone"], user["email"], user["image"], user["role"], user["id"]]
        conn = self.pool.getconn()
        # conn.autocommit = True
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(raw, values)
            conn.commit()
            return None
        except psycopg2.Error as e:
            return str(e)
        finally:
            cursor.close()
            self.pool.putconn(conn)

    def GetCategoryByName(self, name):
        raw = 'select * from category where name = %s'
        value = [name]
        conn = self.pool.getconn()
        # conn.autocommit = True
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(raw, value)
            return cursor.fetchone(), None
        except psycopg2.Error as e:
            return None, str(e)
        finally:
            cursor.close()
            self.pool.putconn(conn)

    def InsertNewCategory(self, values):
        raw = 'insert into category (name) VALUES (%s)'
        conn = self.pool.getconn()
        # conn.autocommit = True
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(raw, values)
            conn.commit()
            return None
        except psycopg2.Error as e:
            return str(e)
        finally:
            cursor.close()
            self.pool.putconn(conn)

    def GetProductByName(self, name):
        raw = 'select * from product where name = %s'
        value = [name]
        conn = self.pool.getconn()
        conn.autocommit = True
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(raw, value)
            return cursor.fetchone(), None
        except psycopg2.Error as e:
            return None, str(e)
        finally:
            cursor.close()
            self.pool.putconn(conn)

    def InsertNewProduct(self, values):
        raw = 'insert into product (name, price, star, description, discount, category_id, image) VALUES (%s, %s, %s, %s, %s, %s, %s)'
        conn = self.pool.getconn()
        # conn.autocommit = True
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(raw, values)
            conn.commit()
            return None
        except psycopg2.Error as e:
            return str(e)
        finally:
            cursor.close()
            self.pool.putconn(conn)

    def UpdateProduct(self, product):
        raw = 'update product set name = %s, image = %s, price = %s, discount = %s, star = %s, description = %s, category_id = %s where id = %s'
        values = [product["name"], product["image"], product["price"], product["discount"], product["star"], product["description"], product["category_id"], product["id"]]
        conn = self.pool.getconn()
        # conn.autocommit = True
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(raw, values)
            conn.commit()
            return None
        except psycopg2.Error as e:
            return str(e)
        finally:
            cursor.close()
            self.pool.putconn(conn)

    def DeleteProduct(self, id):
        raw = 'delete from product where id = %s'
        value = [id]
        conn = self.pool.getconn()
        # conn.autocommit = True
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(raw, value)
            conn.commit()
            return None
        except psycopg2.Error as e:
            return str(e)
        finally:
            cursor.close()
            self.pool.putconn(conn)

    def GetCategoryById(self, id):
        raw = 'select * from category where id = %s'
        value = [id]
        conn = self.pool.getconn()
        # conn.autocommit = True
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(raw, value)
            return cursor.fetchone(), None
        except psycopg2.Error as e:
            return None, str(e)
        finally:
            cursor.close()
            self.pool.putconn(conn)

    def CountProductsLinkWithCategory(self, id):
        raw = "select count(*) from product where category_id = %s"
        value = [id]
        conn = self.pool.getconn()
        # conn.autocommit = True
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(raw, value)
            return cursor.fetchone(), None
        except psycopg2.Error as e:
            return None, str(e)
        finally:
            cursor.close()
            self.pool.putconn(conn)
    
    def UpdateCategory(self, category):
        raw = 'update category set name = %s where id = %s'
        values = [category["name"], category["id"]]
        conn = self.pool.getconn()
        # conn.autocommit = True
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(raw, values)
            conn.commit()
            return None
        except psycopg2.Error as e:
            return str(e)
        finally:
            cursor.close()
            self.pool.putconn(conn)

    def DeleteCategory(self, id):
        raw = 'delete from category where id = %s'
        value = [id]
        conn = self.pool.getconn()
        # conn.autocommit = True
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(raw, value)
            conn.commit()
            return None
        except psycopg2.Error as e:
            return str(e)
        finally:
            cursor.close()
            self.pool.putconn(conn)

    def GetCouponByCode(self, code):
        raw = 'select id, code, discount::float, valid_from, valid_to from coupon where code = %s'
        value = [code]
        conn = self.pool.getconn()
        # conn.autocommit = True
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(raw, value)
            return cursor.fetchone(), None
        except psycopg2.Error as e:
            return None, str(e)
        finally:
            cursor.close()
            self.pool.putconn(conn)

    def CartStore(self, data):
        raw = 'insert into "order" (user_id, status, customer, delivery_address, total_price, total_quantity) VALUES (%s, %s, %s, %s, %s, %s) returning id'
        values = [data["user_id"], 1, data["customer_name"], data["customer_address"], data["detail"]["total_price"], data["detail"]["total_quantity"]]
        conn = self.pool.getconn()
        # conn.autocommit = True
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(raw, values)
            id = cursor.fetchone()
            for value in data["detail"]["data"]:
                raw = 'insert into order_detail (product_id, order_id, quantity) values(%s, %s, %s)'
                values = [value["id"], id["id"], value["quantity"]]
                try:
                    cursor.execute(raw, values)
                except psycopg2.Error as e:
                    return str(e)
            conn.commit()

            return None
        except psycopg2.Error as e:
            return str(e)
        finally:
            cursor.close()
            self.pool.putconn(conn)



