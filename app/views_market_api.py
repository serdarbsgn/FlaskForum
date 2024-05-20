import uuid
from flask import request,jsonify,escape
from app.sql_dependant.sql_read import Select
from app.sql_dependant.sql_tables import Cart, Forum, Order, Product,OrderItem, ProductForum
from app.sql_dependant.sql_connection import sqlconn
from app.sql_dependant.sql_write import Insert,Delete, Update
from app.views_api import check_auth
from . import app
from PIL import Image
from app.helpers import *

@app.route('/api/orders', methods=['GET'])
def api_orders():
    auth_check = check_auth()
    if not auth_check:
        return jsonify({"msg":"Can't get the user because token is expired or wrong."}),401

    with sqlconn() as sql:
        order_items = sql.session.execute(Select.order_item({"user":auth_check["user"]})).mappings().fetchall()
        order_dict = {}
        for order in order_items:
            if order["order_id"] not in order_dict:
                order_dict[order["order_id"]] = [order]
            else: order_dict[order["order_id"]].append(order)
        return jsonify({"orders":order_dict}),200

@app.route('/api/cart', methods=['GET'])
def api_cart():
    auth_check = check_auth()
    if not auth_check:
        return jsonify({"msg":"Can't get the user because token is expired or wrong."}),401
    with sqlconn() as sql:
        cart_items = sql.session.execute(Select.cart_item({"user":auth_check["user"]})).mappings().fetchall()
        total = 0
        for item in cart_items:
            total += item["quantity"]*item["price"]
        return jsonify({"cart_items":cart_items,"total":total}),200

@app.route('/api/market', methods=['GET'])
def api_market():
    with sqlconn() as sql:
        products = listify(sql.session.execute(Select.products()).mappings().fetchall())
        for product in products:
            product["image"] = product_photos_dir+product["image"]
        return jsonify({"products":products}),200

@app.route('/api/add-to-cart', methods=['POST'])
def api_add_to_cart():
    auth_check = check_auth()
    if not auth_check:
        return jsonify({"msg":"Can't get the user because token is expired or wrong."}),401
    
    if "product_id" not in request.json:
        return jsonify({"msg":"Crucial information about this function is missing."}),400
    
    with sqlconn() as sql:
        user =  auth_check["user"]
        check = sql.session.execute(Select.cart({"user":user})).fetchall()
        if len(check)==0:
            cart = Cart(
                user_id = user
            )
            sql.session.add(cart)
            sql.session.commit()
        check = sql.session.execute(Select.cart({"user":user})).fetchall()
        sql.execute(Insert.cart_item({"cart_id":check[0]["id"],"product_id":escape(request.json["product_id"])}))
        sql.session.commit()
        return jsonify({"msg":"Product added to your cart successfully!"}),200


@app.route('/api/remove-from-cart',methods=['POST'])
def api_remove_from_cart():
    auth_check = check_auth()
    if not auth_check:
        return jsonify({"msg":"Can't get the user because token is expired or wrong."}),401
    
    if "product_id" not in request.json:
        return jsonify({"msg":"Crucial information about this function is missing."}),400
    
    with sqlconn() as sql:
        user =  auth_check["user"]
        check = sql.session.execute(Select.cart({"user":user})).fetchall()
        if len(check)==0:
            return "This is wrong and its all your fault",400 
        sql.execute(Delete.cart_item({"cart_id":check[0]["id"],"product_id":escape(request.json["product_id"])}))
        sql.session.commit()
        return jsonify({"msg":"Product removed from your cart successfully!"}),200

@app.route('/api/update-cart',methods=['POST'])
def api_update_cart():
    auth_check = check_auth()
    if not auth_check:
        return jsonify({"msg":"Can't get the user because token is expired or wrong."}),401
    
    if not set(["product_id","quantity"]).issubset(set(request.json.keys())):
        return jsonify({"msg":"Crucial information about this function is missing."}),400
    
    with sqlconn() as sql:
        user =  auth_check["user"]
        check = sql.session.execute(Select.cart({"user":user})).fetchall()
        if len(check)==0:
            return jsonify({"msg":"Something went wrong, have you removed your account and still trying to use the site?"}),400
        if sql.execute(Update.cart_item({"cart_id":check[0]["id"],"product_id":escape(request.json["product_id"]),"quantity":escape(request.json["quantity"])})):
            sql.session.commit()
        return jsonify({"msg":"Updated your cart succesffully"}),200
    
@app.route('/api/add-product', methods=['GET', 'POST'])
def api_add_product():
    auth_check = check_auth()
    if not auth_check:
        return jsonify({"msg":"Can't get the user because token is expired or wrong."}),401
    
    if not set(["name","description","price"]).issubset(set(request.form.keys())):
        return jsonify({"msg":"Crucial information about this function is missing."}),400
    
    if 'file' not in request.files:
        return jsonify({"msg":"No file"}),400

    with sqlconn() as sql:
        rand= "p-"+str(uuid.uuid4())+".jpg"
        filepath = project_dir+"/static/"+product_photos_dir+rand
        file = request.files['file']
        file.save(filepath)
        try:
            img = Image.open(filepath)
            img.verify()
            img.close()
        except:
            os.remove(filepath)
            return jsonify({"msg":"This is not an image"}),400
        product = Product(
            name = escape(request.form["name"]),
            description = escape(request.form["description"]),
            price = int(escape(request.form["price"])),
            image = rand
        )
        sql.session.add(product)
        sql.commit()
        product_id = sql.session.execute(Select.product_id_from_photo({"image":rand})).fetchone()[0]
        check = sql.session.execute(Select.forum_exists(escape("Product: " + request.form["name"]))).mappings().fetchall()
        if len(check)>0:
            product_forum_mapping = ProductForum(
                product_id = product_id,
                forum_id = check[0]["id"]
            )
            sql.session.add(product_forum_mapping)
            sql.commit()
            return jsonify({"msg":"Product already has a forum and product added successfully"}),200
        else:
            product_forum = Forum(
            name=escape("Product: " + request.form["name"]),
            description=escape(request.form["description"]))
            sql.session.add(product_forum)
            sql.commit()
            forumid = sql.session.execute(Select.forum_exists(escape("Product: " + request.form["name"]))).fetchone()[0]
            product_forum_mapping = ProductForum(
                product_id = product_id,
                forum_id = forumid
            )
            sql.session.add(product_forum_mapping)
            sql.commit()
        return jsonify({"msg":"Product and its forum added successfully!"}),200

#Not finished yet.
@app.route('/api/checkout', methods=['GET'])
def api_checkout():
    auth_check = check_auth()
    if not auth_check:
        return jsonify({"msg":"Can't get the user because token is expired or wrong."}),401
    user =  auth_check["user"]
    with sqlconn() as sql:
        cart_items = sql.session.execute(Select.cart_item({"user":user})).mappings().fetchall()
        sql.session.execute(Delete.cart({"user":user}))
        sql.session.commit()

        order = Order(
                        id = cart_items[0]["cart_id"],
                        user_id = user
                    )
        sql.session.add(order)
        sql.session.commit()

        order_items = [OrderItem(
            order_id = item["cart_id"],
            product_id = item["product_id"],
            quantity = item["quantity"]
        ) for item in cart_items]

        for ordered_item in order_items:
            sql.session.add(ordered_item)
        sql.session.commit()

        total= 0
        for item in cart_items:
            total += item["quantity"]*item["price"]
    return jsonify({"msg":f"We got your order, total price is:{total}"}),200


def listify(map):
    templist = []
    for row in map:
        dicx = {}
        for key,val in row.items():
            dicx[key] = val
        templist.append(dicx)
    return templist