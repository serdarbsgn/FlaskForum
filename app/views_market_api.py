from decimal import Decimal
from html import escape
from typing import Dict, List
import uuid

from fastapi import File, HTTPException, Request, UploadFile
from pydantic import BaseModel
from sql_dependant.sql_read import Select
from sql_dependant.sql_tables import Cart, Forum, Order, Product,OrderItem, ProductForum
from sql_dependant.sql_connection import sqlconn
from sql_dependant.sql_write import Insert,Delete, Update
from views_api import MsgResponse, check_auth
from main import app
from PIL import Image
from helpers import *

class OrderResponse(BaseModel):
    id : int
    order_id: int
    product_id : int
    quantity : int
    name : str
    price : Decimal

class OrdersResponse(BaseModel):
    orders: Dict[int, List[OrderResponse]]

@app.get('/api/orders',responses={
        200: {
            "description": "Success response",
            "model": OrdersResponse
        }})
def api_orders(request:Request):
    auth_check = check_auth(request)

    with sqlconn() as sql:
        order_items = listify(sql.session.execute(Select.order_item({"user":auth_check["user"]})).mappings().fetchall())
        order_dict = {}
        for order in order_items:
            if order["order_id"] not in order_dict:
                order_dict[order["order_id"]] = [order]
            else: order_dict[order["order_id"]].append(order)
        return OrdersResponse(orders=order_dict)

class CartItemResponse(BaseModel):
    id : int
    cart_id : int
    product_id : int
    quantity : int
    name : str
    price : Decimal

class CartResponse(BaseModel):
    cart_items: List[CartItemResponse]
    total : Decimal

@app.get('/api/cart',responses={
        200: {
            "description": "Success response",
            "model": CartResponse
        }})
def api_cart(request:Request):
    auth_check = check_auth(request)
    with sqlconn() as sql:
        cart_items = sql.session.execute(Select.cart_item({"user":auth_check["user"]})).mappings().fetchall()
        total = 0
        for item in cart_items:
            total += item["quantity"]*item["price"]
        return CartResponse(cart_items=cart_items,total=total)

class ProductResponse(BaseModel):
    id : int
    name : str
    description : str
    price : Decimal
    image : str
    forum_id : int
    
class ProductsResponse(BaseModel):
    products: List[ProductResponse]

@app.get('/api/market',responses={
        200: {
            "description": "Success response",
            "model": ProductsResponse
        }})
def api_market():
    with sqlconn() as sql:
        products = listify(sql.session.execute(Select.products()).mappings().fetchall())
        for product in products:
            product["image"] = os.path.join(product_photos_dir,product["image"])
        return ProductsResponse(products=products)

class ARCartInfo(BaseModel):
    product_id : int

@app.post('/api/add-to-cart')
def api_add_to_cart(request:Request,add_to_cart_info:ARCartInfo):
    auth_check = check_auth(request)
    
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
        sql.execute(Insert.cart_item({"cart_id":check[0]["id"],"product_id":add_to_cart_info.product_id}))
        sql.session.commit()
        return MsgResponse(msg="Product added to your cart successfully!")


@app.post('/api/remove-from-cart')
def api_remove_from_cart(request:Request,remove_from_cart_info:ARCartInfo):
    auth_check = check_auth(request)
    with sqlconn() as sql:
        user =  auth_check["user"]
        check = sql.session.execute(Select.cart({"user":user})).fetchall()
        if len(check)==0:
            return "This is wrong and its all your fault",400 
        sql.execute(Delete.cart_item({"cart_id":check[0]["id"],"product_id":remove_from_cart_info.product_id}))
        sql.session.commit()
        return MsgResponse(msg="Product removed from your cart successfully!")
    
class UpdateCartInfo(BaseModel):
    product_id : int
    quantity : int

@app.post('/api/update-cart')
def api_update_cart(request:Request,update_cart_info:UpdateCartInfo):
    auth_check = check_auth(request)

    with sqlconn() as sql:
        user =  auth_check["user"]
        check = sql.session.execute(Select.cart({"user":user})).fetchall()
        if len(check)==0:
            raise HTTPException(status_code=400, detail="Something went wrong, have you removed your account and still trying to use the site?")
        if sql.execute(Update.cart_item({"cart_id":check[0]["id"],"product_id":update_cart_info.product_id,"quantity":update_cart_info.quantity})):
            sql.session.commit()
        return MsgResponse(msg="Updated your cart succesffully")
    
class AddProductInfo(BaseModel):
    name : str
    description : str
    price : Decimal

@app.post('/api/add-product')
async def api_add_product(request:Request,add_product_info:AddProductInfo,file: UploadFile = File(...)):
    check_auth(request)

    with sqlconn() as sql:
        rand= "p-"+str(uuid.uuid4())+".jpg"
        filepath = os.path.join(project_dir,"static",product_photos_dir,rand)
        file = request.files['file']
        with open(filepath, "wb") as buffer:
            buffer.write(await file.read())
        try:
            img = Image.open(filepath)
            img.verify()
            img.close()
        except:
            os.remove(filepath)
            raise HTTPException(status_code=400, detail="This is not a valid image")
        product = Product(
            name = escape(add_product_info.name),
            description = escape(add_product_info.description),
            price = Decimal(escape(add_product_info.price)),
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
            return MsgResponse(msg="Product already has a forum and product added successfully")
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
        return MsgResponse(msg="Product and its forum added successfully!")

#Not finished yet.
@app.get('/api/checkout')
def api_checkout(request:Request):
    auth_check = check_auth(request)
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
    return MsgResponse(msg=f"We got your order, total price is:{total}")

def listify(map):
    templist = []
    for row in map:
        dicx = {}
        for key,val in row.items():
            dicx[key] = val
        templist.append(dicx)
    return templist