import uuid
from app.flaskforms import AddProductForm,AddToCartForm,RemoveFromCartForm,UpdateCartForm
from flask import redirect, url_for,render_template,request,session,flash,jsonify
from app.sql_dependant.sql_read import Select
from app.sql_dependant.sql_tables import Cart, Order, Product,OrderItem
from app.sql_dependant.sql_connection import sqlconn
from app.sql_dependant.sql_write import Insert,Delete, Update
from . import app
from PIL import Image
from app.views import get_user_info
from app.helpers import *

@app.route('/cart', methods=['GET'])
def cart():
    if "user" in session:
        with sqlconn() as sql:
            user =  get_user_info(sql)
            cart_items = sql.session.execute(Select.cart_item({"user":session["user"]})).mappings().fetchall()
            total = 0
            for item in cart_items:
                total += item["quantity"]*item["price"]
            return render_template('cart.html',user=user["username"],picture = profile_photos_dir+user["picture"]["profile_picture"],cart_items=cart_items,total=total,form=RemoveFromCartForm(),form2=UpdateCartForm())
    return redirect(url_for('home')),401

@app.route('/market', methods=['GET'])
def market():
    with sqlconn() as sql:
        form = AddToCartForm()
        products = listify(sql.session.execute(Select.products()).mappings().fetchall())
        for product in products:
            product["image"] = product_photos_dir+product["image"]
        if "user" in session:
            user =  get_user_info(sql)
            return render_template('market.html',products = products,form = form,user=user["username"],picture = profile_photos_dir+user["picture"]["profile_picture"])
        return render_template('market.html',products = products,form = form)

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    if "product_id" in request.form:
        form = AddToCartForm(product_id =request.form["product_id"])
    if form.validate_on_submit():
        if "user" in session:
            with sqlconn() as sql:
                user =  session["user"]
                check = sql.session.execute(Select.cart({"user":user})).fetchall()
                if len(check)==0:
                    cart = Cart(
                        user_id = user
                    )
                    sql.session.add(cart)
                    sql.session.commit()
                check = sql.session.execute(Select.cart({"user":user})).fetchall()
                sql.execute(Insert.cart_item({"cart_id":check[0]["id"],"product_id":form.product_id._value()}))
                sql.session.commit()
                return redirect(url_for('cart'))
    return redirect(url_for('login'))

@app.route('/remove-from-cart',methods=['POST'])
def remove_from_cart():
    if "product_id" in request.form:
        form = RemoveFromCartForm(product_id = request.form["product_id"])
    if form.validate_on_submit():
        if "user" in session:
            with sqlconn() as sql:
                user =  session["user"]
                check = sql.session.execute(Select.cart({"user":user})).fetchall()
                if len(check)==0:
                    return "This is wrong and its all your fault",400 
                sql.execute(Delete.cart_item({"cart_id":check[0]["id"],"product_id":form.product_id._value()}))
                sql.session.commit()
                return redirect(url_for('cart'))
    return redirect(url_for('login'))

@app.route('/update-cart',methods=['POST'])
def update_cart():
    if "product_id" in request.form:
        form = UpdateCartForm(product_id = request.form["product_id"],quantity = request.form["quantity"])
    if form.validate_on_submit():
        if "user" in session:
            with sqlconn() as sql:
                user =  session["user"]
                check = sql.session.execute(Select.cart({"user":user})).fetchall()
                if len(check)==0:
                    return "This is wrong and its all your fault",400 
                if sql.execute(Update.cart_item({"cart_id":check[0]["id"],"product_id":form.product_id._value(),"quantity":form.quantity._value()})):
                    sql.session.commit()
                return redirect(url_for('cart'))
    return redirect(url_for('login'))

@app.route('/add-product', methods=['GET', 'POST'])
def add_product():
    form = AddProductForm()
    if form.validate_on_submit():
        if "user" not in session:
            return redirect(url_for('login'))
        with sqlconn() as sql:
            rand= "p-"+str(uuid.uuid4())+".jpg"
            filepath = project_dir+"/static/"+product_photos_dir+rand
            form.photo.data.save(filepath)
            try:
                img = Image.open(filepath)
                img.verify()
                img.close()
            except:
                os.remove(filepath)
                flash("This is not an image")
                return """<script>window.close();</script>""",400
            product = Product(
                name = form.name._value(),
                description = form.description._value(),
                price = form.price._value(),
                image = str(rand)
            )
            sql.session.add(product)
            sql.commit()
            flash('Product added successfully!')
            return """<script>window.close();window.opener.location.reload();</script>"""
    return render_template('add-product.html', form=form)

#Not finished yet.
@app.route('/checkout', methods=['GET'])
def checkout():
    if "user" not in session:
        return redirect(url_for('login'))
    user =  session["user"]
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
        itemlist = []
        for item in cart_items:
            for i in range(item["quantity"]):
                itemlist.append({"id":str(item["product_id"]),"name":str(item["name"]),"price":str(item["price"]),"itemType":"VIRTUAL",'category1': 'Game'})
            total += item["quantity"]*item["price"]

    return jsonify(itemlist,total)


def listify(map):
    templist = []
    for row in map:
        dicx = {}
        for key,val in row.items():
            dicx[key] = val
        templist.append(dicx)
    return templist