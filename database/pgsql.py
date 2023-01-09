import psycopg2
from psycopg2.extras import RealDictCursor, LoggingConnection
from psycopg2 import pool

class PGSQL():
    """
    Thực hiện các truy vấn đến cơ sở dữ liệu PostgreSQL
    Attribute
        pool: để lưu trữ kết nối với cơ sở dữ liệu để có thể tái sử dụng
    """
    def __init__(self, config):
        """
        Khởi tạo class 
        Input:
	        config (flask.Config): thông tin cấu hình
        Output:
            None
        """
        try: 
            self.pool = pool.ThreadedConnectionPool(1, 50, config["DATABASE_URL"])
            if self.pool :
                print("Connection pool created successfully using ThreadedConnectionPool")
        except (Exception, psycopg2.DatabaseError) as error:
                print("Error while connecting to PostgreSQL", error)

    def ProductList(self, category, star, discount, priceFrom, priceTo, search, order, sort, limit, offset):
        """
        Truy vấn lấy danh sách sản phẩm
        Input:
            category (int): id của danh mục sản phẩm
	        star (int): sao của sản phẩm
	        discount (bool): có giảm giá hay không
	        priceFrom (float): có mức giá từ
	        priceTo (float): có mức giá đến
	        search (string): từ khóa tìm kiếm
	        order (string): trật tự sắp xếp
        Output:
	        error: lỗi phát sinh
	        array dictionary: danh sách sản phẩm
        """
        filter = "true"
        filterValue = []
        # Handle categoryId
        if category != None:
            category = str(category).replace('_', ' ')
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
        """
        Truy vấn lấy danh sách danh mục sản phẩm
        Input:
        Output:
	        error: lỗi phát sinh
	        array dictionary: danh sách danh mục sản phẩm
        """
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
        """
        Truy vấn lấy thông tin sản phẩm theo id
        Input:
	        id (int): id của danh mục sản phẩm
        Output:
            error: lỗi phát sinh
            dictionary: danh mục sản phẩm 
        """
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
        """
        Truy vấn lấy thông tin tài khoản người dùng theo username
        Input:
	        username (string): tên của người dùng
        Output:
	        error: lỗi phát sinh
	        dictionary: người dùng
        """
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
        """
        Truy vấn tạo mới tài khoản người dùng
        Input:
        	values (list): các thông tin của người dùng
        Output:
            error: lỗi phát sinh
        """
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
        """
        Truy vấn lấy thông tin tài khoản người dùng theo id
        Input:
            id (int): id của người dùng
        Output:
	        error: lỗi phát sinh
	        dictionary: người dùng
        """
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
        """
        Truy vấn cập nhật thông tin tài khoản người dùng
        Input:
        	user (dictionary): các thông tin của người dùng
        Output:
            error: lỗi phát sinh
        """
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
        """
        Truy vấn lấy danh mục sản phẩm theo name
        Input:
            name (string): tên của danh mục sản phẩm
        Output:
            error: lỗi phát sinh
	        dictionary: danh mục sản phẩm
        """
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
        """
        Truy vấn tạo mới danh mục sản phẩm
        Input:
            values (list): các thông tin của danh mục sản phẩm 
        Output:
            error: lỗi phát sinh
        """
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
        """
        Truy vấn lấy thông tin sản phẩm theo name
        Input:
            name (string): tên của sản phẩm
        Output:
            error: lỗi phát sinh
	        dictionary: sản phẩm
        """
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
        """
        Truy vấn tạo mới sản phẩm
        Input:
            values (list): các thông tin của sản phẩm 
        Output:
            error: lỗi phát sinh
        """
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
        """
        Truy vấn cập nhật thông tin sản phẩm
        Input:
            product (dictionary): các thông tin của sản phẩm
        Output:
            error: lỗi phát sinh
        """
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
        """
        Truy vấn xóa sản phẩm
        Input:
            id (int): id của sản phẩm
        Output:
            error: lỗi phát sinh
        """
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
        """
        Truy vấn lấy danh mục sản phẩm theo id
        Input:
            id (int): id của danh mục sản phẩm
        Output:
            error: lỗi phát sinh
	        dictionary: danh mục sản phẩm 
        """
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
        """
        Truy vấn đếm số sản phẩm có trong danh mục sản phẩm
        Input:
            id (int): id của danh mục sản phẩm
        Output:
            error: lỗi phát sinh
            dictionary: chứa số lượng sản phẩm
        """
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
        """
        Truy vấn cập nhật danh mục sản phẩm
        Input:
            category (dictionary): các thông tin của danh mục sản phẩm
        Output:
            error: lỗi phát sinh
        """
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
        """
        Truy vấn xóa danh mục sản phẩm
        Input:
            id (int): id của danh mục sản phẩm
        Output:
            error: lỗi phát sinh
        """
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
        """
        Truy vấn lấy thông tin giảm giá theo mã
        Input:
            code (string): mã giảm giá
        Output:
            dictionary: thông tin giảm giá
        """
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
        """
        Truy vấn thêm mới thông tin giỏ hàng
        Input:
            data (dictionary): các thông tin của giỏ hàng
        Output:
            error: lỗi phát sinh
        """
        raw = 'insert into cart (user_id, status, customer, delivery_address, total_price, total_quantity) VALUES (%s, %s, %s, %s, %s, %s) returning id'
        values = [data["user_id"], 1, data["customer_name"], data["customer_address"], data["detail"]["total_price"], data["detail"]["total_quantity"]]
        conn = self.pool.getconn()
        # conn.autocommit = True
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute(raw, values)
            id = cursor.fetchone()
            for value in data["detail"]["data"]:
                raw = 'insert into cart_detail (product_id, cart_id, quantity) values(%s, %s, %s)'
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



