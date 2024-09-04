import uuid
from app.flaskforms import AddProductForm,AddToCartForm,RemoveFromCartForm,UpdateCartForm
from flask import redirect, url_for,render_template,request,session,flash,escape
from app.sql_dependant.sql_read import Select
from app.sql_dependant.sql_tables import Cart, Forum, Order, Product,OrderItem, ProductForum
from app.sql_dependant.sql_connection import sqlconn
from app.sql_dependant.sql_write import Insert,Delete, Update
from . import app
from PIL import Image
from app.views import get_user_info
from app.helpers import *

@app.route('/orders', methods=['GET'])
def orders():
    if "user" in session:
        with sqlconn() as sql:
            user =  get_user_info(sql)
            order_items = sql.session.execute(Select.order_item({"user":session["user"]})).mappings().fetchall()
            order_dict = {}
            for order in order_items:
                if order["order_id"] not in order_dict:
                    order_dict[order["order_id"]] = [order]
                else: order_dict[order["order_id"]].append(order)
            return render_template('orders.html',user=user["username"],picture = profile_photos_dir+user["picture"]["profile_picture"],orders=order_dict,hide_header = request.args.get('hide_header',0,type=int))
    return redirect(url_for('home',hide_header = request.args.get('hide_header',0,type=int))),401

@app.route('/cart', methods=['GET'])
def cart():
    if "user" in session:
        with sqlconn() as sql:
            user =  get_user_info(sql)
            cart_items = sql.session.execute(Select.cart_item({"user":session["user"]})).mappings().fetchall()
            total = 0
            for item in cart_items:
                total += item["quantity"]*item["price"]
            return render_template('cart.html',user=user["username"],picture = profile_photos_dir+user["picture"]["profile_picture"],cart_items=cart_items,total=total,form=RemoveFromCartForm(),form2=UpdateCartForm(),hide_header = request.args.get('hide_header',0,type=int))
    return redirect(url_for('home',hide_header = request.args.get('hide_header',0,type=int))),401

@app.route('/market', methods=['GET'])
def market():
    with sqlconn() as sql:
        form = AddToCartForm()
        products = listify(sql.session.execute(Select.products()).mappings().fetchall())
        for product in products:
            product["image"] = product_photos_dir+product["image"]
        if "user" in session:
            user =  get_user_info(sql)
            return render_template('market.html',products = products,form = form,user=user["username"],picture = profile_photos_dir+user["picture"]["profile_picture"],hide_header = request.args.get('hide_header',0,type=int))
        return render_template('market.html',products = products,form = form,hide_header = request.args.get('hide_header',0,type=int))

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
                return redirect(url_for('cart',hide_header = request.args.get('hide_header',0,type=int)))
    return redirect(url_for('login',hide_header = request.args.get('hide_header',0,type=int)))

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
                return redirect(url_for('cart',hide_header = request.args.get('hide_header',0,type=int)))
    return redirect(url_for('login',hide_header = request.args.get('hide_header',0,type=int)))

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
                return redirect(url_for('cart',hide_header = request.args.get('hide_header',0,type=int)))
    return redirect(url_for('login',hide_header = request.args.get('hide_header',0,type=int)))

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
                name = escape(form.name._value()),
                description = escape(form.description._value()),
                price = form.price._value(),
                image = rand
            )
            sql.session.add(product)
            sql.commit()
            product_id = sql.session.execute(Select.product_id_from_photo({"image":rand})).fetchone()[0]
            check = sql.session.execute(Select.forum_exists(escape("Product: " +form.name._value()))).mappings().fetchall()
            if len(check)>0:
                product_forum_mapping = ProductForum(
                    product_id = product_id,
                    forum_id = check[0]["id"]
                )
                sql.session.add(product_forum_mapping)
                sql.commit()
                flash('Product already has a forum')
            else:
                product_forum = Forum(
                name=escape("Product: " + form.name._value()),
                description=escape(form.description._value()))
                sql.session.add(product_forum)
                sql.commit()
                forumid = sql.session.execute(Select.forum_exists(escape("Product: " + form.name._value()))).fetchone()[0]
                product_forum_mapping = ProductForum(
                    product_id = product_id,
                    forum_id = forumid
                )
                sql.session.add(product_forum_mapping)
                sql.commit()
            flash('Product added successfully!')
            return """<script>window.close();window.opener.location.reload();</script>"""
    return render_template('add-product.html', form=form)

#Not finished yet.
@app.route('/checkout', methods=['GET'])
def checkout():
    if "user" not in session:
        return redirect(url_for('login',hide_header = request.args.get('hide_header',0,type=int)))
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
        for item in cart_items:
            total += item["quantity"]*item["price"]
    flash(f'We got your order, total price is:{total}')
    return redirect(url_for('orders',hide_header = request.args.get('hide_header',0,type=int)))


def listify(map):
    templist = []
    for row in map:
        dicx = {}
        for key,val in row.items():
            dicx[key] = val
        templist.append(dicx)
    return templist