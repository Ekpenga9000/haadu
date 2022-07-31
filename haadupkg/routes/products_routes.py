from cmath import log
import random,os
from flask import Flask, render_template, make_response, render_template_string, request, redirect, flash,session
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import values,desc
from haadupkg import app, db,csrf
from haadupkg.models import *
# from haadupkg.forms import 

@app.route('/')
def home():
    log= session.get('user')

    loggedin = User.query.filter(User.userid==log).first()
    
    # return render_template("products/index.html",loggedin=loggedin)
    return redirect("/home")

@app.route('/home')
def shop():
    log= session.get('user')

    loggedin = User.query.filter(User.userid==log).first()

    carty = []
    cart_n = Cart.query.filter(Cart.userid==log).all()
    for i in cart_n:
        carty.append(i.quantity)
    cart_num1 = sum(carty)


    category = Categories.query.all()

    vendy = Vendor.query.all()

    prod = Products.query.join(Categories,Products.categoryid==Categories.categoryid).add_columns(Categories).order_by(desc(Products.productid)).limit(4).all()

    rsp = make_response(render_template("products/shop.html", vendy=vendy,category=category,prod=prod,loggedin=loggedin,cart_num1=cart_num1))
    rsp.set_cookie('newurl','/home')

    return rsp

    

"""shopping by category"""

@app.route("/products/category/<id>")
def product_category(id):
    try:
        log= session.get('user')

        loggedin = User.query.filter(User.userid==log).first()

        category = Categories.query.all()
        vendy = Vendor.query.all()
        prod_cate = Products.query.filter(Products.categoryid == id).all()

        prod_cate2 = Products.query.join(Categories,Products.categoryid==Categories.categoryid).add_columns(Categories).filter(Products.categoryid == id).all()

        for pr,ca in prod_cate2:
            prod_cate1 = ca.category_name
    
        # # prod_cate1 = Products.query.join(Categories,Products.categoryid==Categories.categoryid).add_columns(Categories).filter(Products.categoryid == id).first()
        # prod_cate1 = Categories.query.get(id)

        carty = []
        cart_n = Cart.query.filter(Cart.userid==log).all()
        for i in cart_n:
            carty.append(i.quantity)
        cart_num1 = sum(carty)

        return render_template("products/product_category.html",category=category,prod_cate=prod_cate,vendy=vendy,loggedin=loggedin, cart_num1=cart_num1,prod_cate1=prod_cate1)

    except Exception:
        return render_template("/products/categoryerror.html",category=category,prod_cate=prod_cate,vendy=vendy,loggedin=loggedin, cart_num1=cart_num1)

"""View vendors"""

@app.route("/product/vendor/<id>")
def vendor_shop(id):

    log= session.get('user')

    loggedin = User.query.filter(User.userid==log).first()


    vend_view = Products.query.join(Categories,Products.categoryid==Categories.categoryid).add_columns(Categories).filter(Products.vendorid == id).all()

    vend_view1 = Vendor.query.filter(Vendor.vendorid == id).first()

    

    carty = []
    cart_n = Cart.query.filter(Cart.userid==log).all()
    for i in cart_n:
        carty.append(i.quantity)
    cart_num1 = sum(carty) 

    return render_template("products/vendor_shop.html",vend_view=vend_view,vend_view1=vend_view1,loggedin=loggedin, cart_num1=cart_num1)


"""View product details"""

@app.route("/product/view/<id>")
def product_view(id):

    log= session.get('user')

    loggedin = User.query.filter(User.userid==log).first()


    prod_view = Products.query.join(Categories,Products.categoryid==Categories.categoryid).add_columns(Categories).filter(Products.productid == id).all()

    carty = []
    cart_n = Cart.query.filter(Cart.userid==log).all()
    for i in cart_n:
        carty.append(i.quantity)
    cart_num1 = sum(carty)


    return render_template("products/productdetails.html",loggedin=loggedin,prod_view=prod_view,cart_num1=cart_num1)

def plus(id):
    """This function is to count the quantity of the products added to the cart."""
    return "Done"


@app.route("/product/detail/<id>")
def product_detail(id):

    log= session.get('user')

    if log != None:
        loggedin = User.query.filter(User.userid==log).first()


        prod_view = Products.query.join(Categories,Products.categoryid==Categories.categoryid).add_columns(Categories).filter(Products.productid == id).all()

        cart_deets = Cart.query.filter(Cart.userid==log,Cart.productid==id).all()

        # this is to show the the number of items on the cart for a particular product.
        cart_num2 = [ ]
        for i in cart_deets:
            cart_num2.append(i.cartid)

        cart_num = len(cart_num2)

        carty = []
        cart_n = Cart.query.filter(Cart.userid==log).all()
        for i in cart_n:
            carty.append(i.quantity)
        cart_num1 = sum(carty)

    
        return render_template("products/productadddetails.html",loggedin=loggedin,prod_view=prod_view,cart_num=cart_num,cart_num1=cart_num1)
        # return str(prod_view)
    else:
        return redirect("/user/login")


        
@app.route("//nav//_bar")
def navbar():
    log = session.get('user')

    loggedin = User.query.filter(User.userid==log).first()

    # I am filtering all in the cart only by the user id. 

    carty = []
    cart_n = Cart.query.filter(Cart.userid==log).all()
    for i in cart_n:
        carty.append(i.quantity)
    cart_num1 = sum(carty)

    return render_template("products/navbar.html",loggedin=loggedin,cart_num1=cart_num1)

"""navbar search button"""

@app.route("/search_items", methods=['POST','GET'])
def search_bar():
    log = session.get('user')
    loggedin = User.query.filter(User.userid==log).first()

    carty = []
    cart_n = Cart.query.filter(Cart.userid==log).all()
    for i in cart_n:
        carty.append(i.quantity)
    cart_num1 = sum(carty)
    
    search = request.form.get('searchbar')

    prx = Products.query.filter(Products.product_name.like(f"%{search}%") ).all()

    category = Categories.query.all()

    vendy = Vendor.query.all()

    prod = Products.query.join(Categories,Products.categoryid==Categories.categoryid).add_columns(Categories).order_by(desc(Products.productid)).limit(4).all()

    return render_template("products/searchresults.html",prx=prx,loggedin=loggedin,cart_num1=cart_num1,vendy=vendy,category=category,prod=prod,)
   
    # return render_template("products/navbar.html",prx=prx,loggedin=loggedin,cart_num1=cart_num1)


    # rsp = make_response(render_template("products/shop.html", vendy=vendy,category=category,prod=prod,loggedin=loggedin,cart_num1=cart_num1))
    # rsp.set_cookie('newurl','/home')
