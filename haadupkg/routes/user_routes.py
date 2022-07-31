import random,os,requests,json
from weakref import ref
from functools import wraps
from flask import Flask, jsonify, render_template, make_response, render_template_string, request, redirect, flash,session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import values,or_,desc
import pdfkit
from haadupkg import app, db,csrf
from haadupkg.models import *
from haadupkg.forms import *


# path_wkhtmltopdf = 'C:\Users\chigo\OneDrive\Desktop\haadu\wkhtmltopdf\bin\wkhtmltopdf.exe'
# config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
# pdfkit.from_url("http://google.com", "out.pdf", configuration=config)

def sessionauth(func): #This is for the session get to secure the page.
    @wraps
    def wrapper(*args,**kwargs):
        if session.get('guest') != None:
            return func(*args,**kwargs)
        else:
            return redirect('user/login')
    return wrapper

"""getting the number for the cart """



@app.route('/user/registration_complete')
def congratulations():

    return render_template("user/congratulations.html")

@app.route('/user/signup', methods=['POST','GET'])
def user_signup():

    regform = Userregistration()

    if request.method == 'GET':
        
        return render_template('user/userreg.html',regform=regform)
    else:
        if regform.validate_on_submit():

            firstname = request.form.get('firstname')
            lastname = request.form.get('lastname')
            email_addy = request.form.get('email_addy')
            phone = request.form.get('phone')
            username = request.form.get('username')
            password = request.form.get('password')
            
            hashed = generate_password_hash(password)

            user = User(firstname=firstname,lastname=lastname,email=email_addy, phone=phone,username=username,password=hashed)

            db.session.add(user)
            db.session.commit()
            
            return redirect("/user/login")

        else:
            flash("Please ensure that your details have been inputted properly")
            return render_template('user/userreg.html',regform=regform)


"""User login """

@app.route("/user/login", methods=['POST','GET'])
def user_login():

    if request.method == 'GET':

        login_form = Userlogin()

        return render_template('user/user_login.html',login_form = login_form)

    else:
        username = request.form.get('username')
        password = request.form.get('password')

        customer_deets = User.query.filter(User.username==username).first()
        if customer_deets and check_password_hash(customer_deets.password,password):
            customer_id = customer_deets.userid 
            session["user"] = customer_id
            return redirect("/home")
        else:
            flash("Invalid credentials")
            return redirect("/user/login")

"""User profile view"""

@app.route("/user/profile/")
def user_profile():
    log = session.get('user')

    log1 = User.query.filter(User.userid == log).first()

    ord1 = Orders.query.filter(Orders.userid==log).filter(or_(Orders.orderstatus=="Pending",Orders.orderstatus=="Processing")).count()
    ord2 = Orders.query.filter(Orders.userid==log, Orders.orderstatus=="Completed").count()
    ord = Orders.query.filter(Orders.userid==log).all()

    

    ord3 = Orders.query.filter(Orders.userid==log).count()

    loggedin = log1.firstname

    return render_template('user/useraccount.html',loggedin=loggedin,ord1=ord1,ord2=ord2)

"""The user editing his account"""

@app.route("/user/profile/edit")

def user_edit():
    log = session.get('user')

    log1 = User.query.filter(User.userid == log).first()

    log2 = User.query.filter(User.userid == log).all()

    
    ord = Orders.query.filter(Orders.userid==log).all()

    ord1 = Orders.query.filter(Orders.userid==log).filter(or_(Orders.orderstatus=="Processing",Orders.orderstatus=="Pending")).count()
    ord2 = Orders.query.filter(Orders.userid==log).filter(or_(Orders.orderstatus=="Completed",Orders.orderstatus=="Cancelled")).count()

    ord3 = Orders.query.filter(Orders.userid==log).count()

    state = State.query.all()

    loggedin = log1.firstname

    ur = Userregistration()

    return render_template('user/useraccountedit.html',loggedin=loggedin,ord1=ord1,log2=log2,ur=ur,state=state,ord3=ord3,ord=ord,ord2=ord2)


@app.route("/user/profile/update",methods=['POST'])
def user_profile_update():
    log = session.get('user')

    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    email = request.form.get('email_addy')
    address = request.form.get('address')
    phone = request.form.get('phone')
    state = request.form.get('state')


    if log != None:
        
        user_update = User.query.filter(User.userid==log).all()

        if firstname != None and lastname != None and email != None and address != None and phone != None and state != None:

            for i in user_update:

                i.firstname = firstname
                i.lastname = lastname
                i.email = email
                i.address = address
                i.phone = phone
                i.stateid = state
            
            db.session.commit()

            flash('Your details have been updated successfully.')
            return redirect("/user/profile/edit") 

        else:
            flash('Please ensure the fields are properly filled.')
            return redirect("/user/profile/edit") 
    else:
        return redirect('/user/login')


"""Navbar to show the name of the logged in user."""

@app.route("/nav/bar")
def nav_bar():

    loggedin = session.get('user')
    return render_template('products/navbar.html',loggedin=loggedin)


"""This is to show the cart details, this is the checkout page."""

@app.route("/user/pending_order/view")
def pending_order():
    log = session.get('user')

    #The aim of route is to provide the products that have been added to cart. There will be a modify button on each product to take them back to the product details page. 
    
    if log != None:
         
        log1 = User.query.filter(User.userid == log).first()

        ord1 = Orders.query.filter(Orders.userid==log).filter(or_(Orders.orderstatus=="Processing",Orders.orderstatus=="Pending")).count()
        ord2 = Orders.query.filter(Orders.userid==log).filter(or_(Orders.orderstatus=="Completed",Orders.orderstatus=="Cancelled")).count()
        ord3 = Orders.query.filter(Orders.userid==log).count()

        loggedin = log1.firstname

        #spooling the name of the details of the products from the cart.
        cart_deets = Cart.query.join(Products,Cart.productid==Products.productid).filter(Cart.userid==log).add_columns(Products).all()

        amt1 = []
        
        for i,j in cart_deets:
            amt1.append(i.amount)

        amt = sum(amt1)

        total = int(amt) + 500

        user_deets = User.query.filter(User.userid == log).all()

        state = State.query.all()

        return render_template("user/user_orderview.html", ord1=ord1,loggedin=loggedin,ord2=ord2,cart_deets=cart_deets,amt=amt,user_deets=user_deets,state=state,total=total,ord3=ord3)

    else:
        return redirect("/user/login")


"""This is to show the completed order details"""

@app.route("/user/completed_order/view")
def completed_order():
    # We will check the page.
    log = session.get('user')

    if log != None:  
        #retrieve the order list
        log1 = User.query.filter(User.userid==log).first()

        loggedin = log1.firstname
        
        ord = Orders.query.filter(Orders.userid==log).all()

        ord1 = Orders.query.filter(Orders.userid==log).filter(or_(Orders.orderstatus=="Processing",Orders.orderstatus=="Pending")).count()
        ord2 = Orders.query.filter(Orders.userid==log).filter(or_(Orders.orderstatus=="Completed",Orders.orderstatus=="Cancelled")).count()

        ord3 = Orders.query.filter(Orders.userid==log).count()

        order = Orders.query.join(Order_details,Orders.orderid==Order_details.orderid).join(Products,Order_details.productid == Products.productid).join(Payments,Orders.orderid==Payments.orderid).add_columns(Order_details,Products,Payments).filter(Orders.userid==log).filter(or_(Orders.orderstatus=="Cancelled",Orders.orderstatus=="Completed")).order_by(desc(Orders.orderdate)).all()

        return render_template("user/user_completedorderview.html",ord=ord,loggedin=loggedin,ord1=ord1,ord2=ord2,order=order,ord3=ord3)
    else:
        return redirect("/user/login")


"""This is for the user to recieve messages frorm the admin, We would use Ajax for this"""
@app.route("/user/inbox/")

def user_inbox():
    return "Done"

"""This is for the customer to input and edit the shipping address, the default value will be the address on the account"""
@app.route("/user/shipping/address")
def user_address():
    return "This is the shipping address"

"""This is to enable the user to change his password."""

@app.route("/user/password/change")
def change_password():
    return "Your password will be changed shortly."

"""This is the page for the cart"""

@app.route("/user/cart/view")
def cart_view():
    log = session.get('user')

    #The aim of route is to provide the products that have been added to cart. There will be a modify button on each product to take them back to the product details page. 
    
    if log != None:
         
        log1 = User.query.filter(User.userid == log).first()

        ord1 = Orders.query.filter(Orders.userid==log).filter(or_(Orders.orderstatus=="Processing",Orders.orderstatus=="Pending")).count()
        ord2 = Orders.query.filter(Orders.userid==log).filter(or_(Orders.orderstatus=="Completed",Orders.orderstatus=="Cancelled")).count()

        loggedin = log1.firstname

        #spooling the name of the details of the products from the cart.
        cart_deets = Cart.query.filter(Cart.userid==log).all()

        amt1 = []
        
        for i in cart_deets:
            amt1.append(i.amount)

        amt = sum(amt1)

        return render_template("user/cartview.html", ord1=ord1,loggedin=loggedin,ord2=ord2,cart_deets=cart_deets,amt=amt)

    else:
        return redirect("/user/login")

"""I am adding to cart"""

@app.route("/addcart", methods=['POST'])
def add2_cart():
    product = request.form.get('product')
    price = request.form.get('price')
    qty=1

    log = session.get('user')

    if log != None:
            #I am going to check if the user has this product in the cart. 

        cart_check = Cart.query.filter(Cart.userid==log, Cart.productid==product).all()

            # I am going to redirect to the http://127.0.0.1:7777/product/detail/6 if the product is already there. Else I will create a new cart for the customer. 

        if cart_check == []:

            amt=int(qty)*int(price)
            addCart = Cart(userid=log, productid=product, quantity=qty, amount=amt)

            db.session.add(addCart)
            db.session.commit()
            # num = []
            # carty = Cart.query.filter(Cart.userid).all()
                
            # for i in carty:
            #     num.append(i.quantity)
            #     # I am adding the session for the qty 
            # session['cart'] = {int(log):num}
           
                
            return redirect(f"/product/detail/{product}")
        else:
            return redirect(f"/product/detail/{product}")
    else:
        return redirect("/user/login")
    # except Exception:

# @app.route("/qty")
# def qty():
#     return str(session.get('cart'))

@app.route("/addtocart")
def add_cart():
    # try:
        # Let us get the session to check the page and also get the user id
    log = session.get('user')
    product = request.args.get('productid')
    qty = request.args.get("quantity")
    price = request.args.get('price')

        # It is time to check it 

    if log != None:
            #I am going to check if the user has this product in the cart. 

        cart_check = Cart.query.filter(Cart.userid==log, Cart.productid==product).all()

            # I am going to redirect to the http://127.0.0.1:7777/product/detail/6 if the product is already there. Else I will create a new cart for the customer. 
        
        if cart_check == []:
            
            amt=int(qty)*int(price)
            addCart = Cart(userid=log, productid=product, quantity=qty, amount=amt)

            db.session.add(addCart)
            db.session.commit()

            # num = []
            # carty = Cart.query.filter(Cart.userid).all()
                
            # for i in carty:
            #     num.append(i.quantity)
                # I am adding the session for the qty 
            
        
                # I am adding the session for the qty 
            carty = []
            cart_n = Cart.query.filter(Cart.userid==log).all()
            for i in cart_n:
                carty.append(i.quantity)
            cart_num1 = sum(carty)

            cart_num == int(qty)

            feedback = "A product has been added to your cart"

            return jsonify(cart_num1=cart_num1,cart_num=cart_num,feedback=feedback)

        else:
            for i in cart_check:
                i.quantity = qty
                i.amount = int(qty) * int(price)

            db.session.commit()

            carty = []
            cart_n = Cart.query.filter(Cart.userid==log).all()
            for i in cart_n:
                carty.append(i.quantity)
            cart_num1 = sum(carty)

            cart_num = int(qty)

            feedback = "A product's quantity has been updated on your cart"

            return jsonify(cart_num1=cart_num1,cart_num=cart_num,feedback=feedback)
    else:
        return redirect("/user/login")
    # except Exception:
    #     return "Oops something went wrong"

"""Deleting from the cart"""

@app.route("/product/cart_delete/<id>")
def delete_from_cart(id):
    log = session.get("user")

    if log != None:

        cart_del = Cart.query.filter(Cart.userid==log,Cart.productid==id).all()

        for i in cart_del:
            db.session.delete(i)
        db.session.commit()
        
        flash("Item has been deleted from your cart")
        return redirect("/user/cart/view")
    
    else:
        return redirect("/user/login")

"""Empty cart"""  

@app.route("/cart/empty")
def empty_from_cart():
    try:
        log = session.get("user")

        session.pop('cart',None)

        if log != None:

            db.session.execute(f"DELETE from cart WHERE userid='{log}'")
            
            db.session.commit()

            flash("Cart has been emptied")
            return redirect("/user/cart/view")
        
        else:
            return redirect("/user/login")
    except Exception:
        return redirect("/user/cart/view")


"""View the open orders."""
@app.route("/user/order/view")
def open_orders():
    log =session.get('user')

    if log != None:
       

        ord1 = Orders.query.filter(Orders.userid==log).filter(or_(Orders.orderstatus=="Processing",Orders.orderstatus=="Pending")).count()
        ord2 = Orders.query.filter(Orders.userid==log).filter(or_(Orders.orderstatus=="Completed",Orders.orderstatus=="Cancelled")).count()

        ord3 = Orders.query.filter(Orders.userid==log).count()

        log1 = User.query.filter(User.userid==log).first()

        loggedin = log1.firstname

        order = Orders.query.join(Order_details,Orders.orderid==Order_details.orderid).join(Products,Order_details.productid == Products.productid).join(Payments,Orders.orderid==Payments.orderid).add_columns(Order_details,Products,Payments).filter(Orders.userid==log).filter(or_(Orders.orderstatus=="Processing",Orders.orderstatus=="Pending")).order_by(desc(Orders.orderdate)).all()

        return render_template("user/useropen_orders.html", order=order,ord1=ord1,ord2=ord2,loggedin=loggedin,ord3=ord3)
    else:
        return redirect("/user/login")

'''We are going to generate the ref number for the orders. This will be important for consuming the web service.'''

def generate_ref(): #This is was will be added as the order session and the order ref.
    """This is the generate a random string of numbers"""
    ref = random.random() * 1000000
    return int(ref) 

def get_product(itemid):
    """Given an id, it fetches the id of the product"""
    deets = Cart.query.get(itemid)
    if deets != None:
        return deets.productid
    else:
        return 0

def get_quantity(itemid):
    """Given an id, it fetches the quantity"""
    deets = Cart.query.filter(Cart.productid==itemid).first()
    if deets != None:
        return deets.quantity
    else:
        return 0


def get_amount(itemid):
    """Given an id, it fetches the amount"""
    deets = Products.query.get(itemid)
    if deets != None:
        return deets.price
    else:
        return 0

"""This is where we are adding to the orders table, orders details tables and the payments table."""
@app.route("/confirmation", methods=['POST'])
def confirmation():
    log = session.get('user')
    #fetching into the orders table. 
    ref = generate_ref() #order ref
    # session['orderref'] = ref
    if log != None:

        address = request.form.get("shipping_addy")

        if address != None:

            #getting the amount 

            cart_deets = Cart.query.filter(Cart.userid==log).all()
        
            amt1 = []
            
            for i in cart_deets:
                amt1.append(i.amount)

            amt = sum(amt1)

            prod_selected = []

            for i in cart_deets:
                prod_selected.append(i.productid)

            #Adding to the order table.

            add_ord = Orders(orderref=ref,orderamt=amt,orderstatus="Pending", shippingaddress=address,shippingfee=500,userid=log)
            
            db.session.add(add_ord)
            db.session.commit()
            session['orderref'] = ref
            #Adding to the order-details table. 

            order = add_ord.orderid # Get the orderid
            for i in prod_selected: #get the product id 
                qty = get_quantity(i)
                prod_price = get_amount(i)

                ord_det = Order_details(orderid=order,productid=i,price=prod_price,quantity=qty)

                db.session.add(ord_det)
            
            #adding to the payment table. 
            p = Payments(userid=log,orderid=order,paymentmode="Pending",amount=amt,paymentref=ref,paymentstatus='Pending',paymentfeedback="Pending")
            db.session.add(p)

                #commit all changes on all tables (orders,order_details,payment) to the db
            db.session.commit()

            for i in cart_deets:
                db.session.delete(i)
            db.session.commit()

            return redirect('/initialize_paystack') #display all the things we captured back to the user on this page for confirmation b4 we tell him to pay
        else:
            flash("Please ensure that your details are filled out.")
            return redirect('/user/pending_order/view')

    else:
        return redirect("/user/login")


"""Checkout errormessage page"""

@app.route("/user/checkout/error")
def checkout_error():
    log= session.get('user')

    loggedin = User.query.filter(User.userid==log).first()

    return render_template("/user/checkouterror.html",loggedin=loggedin)

"""Paystack initialization"""

@app.route('/initialize_paystack')
def initialize_paystack():
    #connect to paystack and send amount,email, reference, pk_key(as authorization), paystack will respond back with the the url where you will direct user to in order to supply their card details

    loggedin = session.get('user')
    if loggedin != None:
        ref = session.get('orderref')
        a = Orders.query.filter(Orders.orderref==ref).first()
        g = db.session.query(User).get(loggedin)

        if a != None:

            data = {"email":g.email,"amount":a.orderamt * 100, "reference":int(ref)}
            headers = {"Content-Type": "application/json","Authorization":"Bearer sk_test_6dbe08e4ba7e449577136ce4ecc82e21f33ed441"}
            response = requests.post("https://api.paystack.co/transaction/initialize",headers=headers, data=json.dumps(data))
            # response = requests.post("https://api.paystack.co/transaction/initialize",headers=headers, data=jsonify(data))
            rsp_json = response.json()
            if rsp_json['status'] == True:
                url = rsp_json['data']['authorization_url']
                return redirect(url)
            else:
                return 'Please try again'
        
        else:
            # return str(ref)
            return redirect("/user/checkout/error")
    else:
        return redirect('/user/login')

# @app.route('/paystack_landing')
# def paystack_landing():
#     """This route would have been configured in the paystack developer dashboard, this is where user would be redirected to after inputing their card details, here you will confirm the transaction status and update your db accordingly"""

#     loggedin = session.get('user')
#     ref = session.get('orderref')
#     headers = {"Content-Type": "application/json","Authorization":"Bearer sk_test_6dbe08e4ba7e449577136ce4ecc82e21f33ed441"}
#     response = requests.get(f"https://api.paystack.co/transaction/verify/{ref}", headers=headers)
#     rsp_json = response.json() 
#     # uncomment this out to see the structure of what paystack returns, then you would be able to pick what you need
#     return rsp_json 
    
    # if rsp_json['status'] == True: 
    #     data = rsp_json['data']
    #     actual_amt = data['amount']/100
    #     feedback = data['gateway_response']
    #     #update payment table

    #     pay = Payments.query.filter(Payments.paymentref==ref).first()
        
    #     pay.paymentmode = "online"
    #     pay.paymentstatus = 'Paid'
    #     pay.paymentfeedback=feedback

    #     db.session.commit()
    #     # cart = Cart.query.get(loggedin)
        
    #     # db.session.delete(cart)
    #     # db.session.commit()
        
    #     flash("Payment Successful!")
    #     return redirect('/user/profile/') 
    #     # or direct the user to their dashboard where they would see their transaction history as Paid
    # else:
    #     pay = Payments(userid=loggedin,orderid=1,amount=actual_amt,paymentstatus='Failed')
    #     db.session.add(pay)
    #     db.session.commit()
    #     return "Failed, try again"

@app.route("/payment_feedback")
def payment_feedback():
    log = session.get("user")
    ref = session.get('orderref')
    headers = {"Content-Type": "application/json","Authorization":"Bearer sk_test_6dbe08e4ba7e449577136ce4ecc82e21f33ed441"}
    response = requests.get(f"https://api.paystack.co/transaction/verify/{ref}", headers=headers)
    rsp_json = response.json() 
    # uncomment this out to see the structure of what paystack returns, then you would be able to pick what you need
    # return rsp_json 
    
    if rsp_json['status'] == True: 
        data = rsp_json['data']
        actual_amt = data['amount']/100
        feedback = data['gateway_response']
        #update payment table

        pay = Payments.query.filter(Payments.paymentref==ref).first()
        
        pay.paymentmode = "online"
        pay.paymentstatus = 'Paid'
        pay.paymentfeedback=feedback

        db.session.commit()
        # cart = Cart.query.get(loggedin)
        
        # db.session.delete(cart)
        # db.session.commit()
        log1 = User.query.filter(User.userid==log).first()
        loggedin = log1.firstname

        ord = Orders.query.filter(Orders.userid==log).all()

        ord1 = Orders.query.filter(Orders.userid==log).filter(or_(Orders.orderstatus=="Processing",Orders.orderstatus=="Pending")).count()
        ord2 = Orders.query.filter(Orders.userid==log).filter(or_(Orders.orderstatus=="Completed",Orders.orderstatus=="Cancelled")).count()

        ord3 = Orders.query.filter(Orders.userid==log).count()

        order = Orders.query.join(Order_details,Orders.orderid==Order_details.orderid).join(Products,Order_details.productid == Products.productid).join(Payments,Orders.orderid==Payments.orderid).add_columns(Order_details,Products,Payments).filter(Orders.userid==log).filter(or_(Orders.orderstatus=="Cancelled",Orders.orderstatus=="Completed")).order_by(desc(Orders.orderdate)).all()

        trxn_deets = Payments.query.join(User,Payments.userid==User.userid).join(Orders,Payments.orderid==Orders.orderid).join(Order_details,Orders.orderid==Order_details.orderid).join(Products,Order_details.productid==Products.productid).add_columns(User,Orders,Order_details,Products).filter(User.userid==log).order_by(desc(Orders.orderdate)).all()      


        flash("Payment Successful!")
        return render_template("user/congratulations.html",loggedin=loggedin,ord=ord,ord1=ord1,ord2=ord2,order=order,ord3=ord3,trxn_deets=trxn_deets)
        # or direct the user to their dashboard where they would see their transaction history as Paid
    else:
        pay = Payments(userid=loggedin,orderid=1,amount=actual_amt,paymentstatus='Failed')
        db.session.add(pay)
        db.session.commit()
        return "Failed, try again"

"""Printing the PDF"""
@app.route("/print/order_pdf/<paymentref>")
def print_pdf(paymentref):
    log = session.get("user")
    if log == None:
        flash("You will be require to login to proceed.")
        return redirect("/user/login")

    else:
        log1 = User.query.filter(User.userid==log).first()
        loggedin = log1.firstname

        ord = Orders.query.filter(Orders.userid==log).all()

        ord1 = Orders.query.filter(Orders.userid==log).filter(or_(Orders.orderstatus=="Processing",Orders.orderstatus=="Pending")).count()
        ord2 = Orders.query.filter(Orders.userid==log).filter(or_(Orders.orderstatus=="Completed",Orders.orderstatus=="Cancelled")).count()

        ord3 = Orders.query.filter(Orders.userid==log).count()

        order = Orders.query.join(Order_details,Orders.orderid==Order_details.orderid).join(Products,Order_details.productid == Products.productid).join(Payments,Orders.orderid==Payments.orderid).add_columns(Order_details,Products,Payments).filter(Orders.userid==log).filter(or_(Orders.orderstatus=="Cancelled",Orders.orderstatus=="Completed")).order_by(desc(Orders.orderdate)).all()

        trxn_deets = Payments.query.join(User,Payments.userid==User.userid).join(Orders,Payments.orderid==Orders.orderid).join(Order_details,Orders.orderid==Order_details.orderid).join(Products,Order_details.productid==Products.productid).add_columns(User,Orders,Order_details,Products).filter(User.userid==log,Payments.paymentref==paymentref).order_by(desc(Orders.orderdate)).all() 
        
        for py,us,ord,od,pr in trxn_deets:
            total = py.amount 
            orderno = ord.orderref
            paymentref1 = py.paymentref
            pydate = py.paymentdate
            firstname = us.firstname
            lastname = us.lastname
            address = ord.shippingaddress
            phone = us.phone     
        
        return render_template("user/pdf.html", total=total,orderno=orderno,paymentref1=paymentref1,pydate=pydate,firstname=firstname,lastname=lastname,address=address,phone=phone,loggedin=loggedin)

        # pdf = pdfkit.from_string(rendered,False) # Meaning that the html file should be saved as a pdf doc, and the false means it should be stored in the memory.

        # response = make_response(pdf) # instantiating an object response. 

        # response.headers['Content-Type'] = 'application/pdf'
        # response.headers['Content-Disposition'] ='inline; filename=output.pdf'

        # return response 



"""Customer logout"""
@app.route("/user/logout")
def user_logout():
    session.pop('user',None)
    return redirect('/home')

