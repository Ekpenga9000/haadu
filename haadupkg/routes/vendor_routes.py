import random,os
from flask import Flask, render_template, make_response, render_template_string, request, redirect, flash,session,url_for,jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import values,desc
from datetime import datetime
from haadupkg import app, db,csrf
from haadupkg.models import *
from haadupkg.forms import Vendorregistration, Vendorlogin


"""Vendor registration"""


@app.route("/vendor/register/", methods=['POST','GET'])
def vendor_register():

    vsignup = Vendorregistration()

    if request.method == 'GET':
        return render_template("vendor/vendorsignup.html", vsignup=vsignup)

    else:
        if vsignup.validate_on_submit():
            vendorname = request.form.get("vendorname")
            vendor_img = request.form.get("default_profile")
            shoptype = request.form.get("shoptype")
            email = request.form.get("email")
            address = request.form.get("address")
            state = request.form.get("state")
            phone = request.form.get("phone")
            username = request.form.get("username")
            password = request.form.get("password")

            hash = generate_password_hash(password)

            vendor = Vendor(vendor_name=vendorname,vendor_img=vendor_img,vendor_type=shoptype,email=email,address=address,stateid=state,phone=phone,username=username,password=hash)

            db.session.add(vendor)
            db.session.commit()

            return redirect("/vendor/login")
            
           
        else:
            flash("Please input your details correctly.")
            return render_template("vendor/vendorsignup.html",vsignup=vsignup)
            


"""Vendor Login"""

@app.route("/vendor/validate", methods=['POST'])
def vendor_validator():

    login = Vendorlogin()

    if request.method == 'GET':
        return render_template("vendor/vendorlogin.html",login=login)
    else:
        username = request.form.get("username")
        password = request.form.get("password")

        vdeets = Vendor.query.filter(Vendor.username == username).first()

        if vdeets and check_password_hash(vdeets.password, password):
            vdeets= vdeets.vendorid
            session['vendor'] = vdeets
            return redirect("/vendor/dashboard")
        else:
            flash('Invalid credentials')
            return redirect("/vendor/login")

@app.route("/vendor/login")
def vendor_login():

    login = Vendorlogin()
    return render_template("vendor/vendorlogin.html",login=login)
   
      
"""Vendor dashboard"""

@app.route("/vendor/dashboard")
def vendor_dashboard():
    if session.get('vendor') == None:
        return redirect('/vendor/login')
    else:
        loggedin = session.get('vendor')

        vdeets = Vendor.query.filter(Vendor.vendorid == loggedin).all()

        prodcount = Products.query.filter(Products.vendorid == loggedin).count()

        cust = User.query.count()

        prod = Products.query.count()
       
        vend = Vendor.query.count()
        
        ord_deets = Order_details.query.join(Orders,Order_details.orderid==Orders.orderid).join(Products,Order_details.productid==Products.productid).join(Vendor,Products.vendorid==Vendor.vendorid).add_columns(Orders,Products,Vendor).filter(Vendor.vendorid==loggedin).all()

        ord_deets2 = Order_details.query.join(Orders,Order_details.orderid==Orders.orderid).join(Products,Order_details.productid==Products.productid).join(Vendor,Products.vendorid==Vendor.vendorid).add_columns(Orders,Products,Vendor).filter(Vendor.vendorid==loggedin,Orders.orderstatus=="Pending").count()

        orde = Orders.query.count()
        


        return render_template("vendor/vendor.html", vdeets=vdeets,cust=cust,prod=prod,vend=vend,orde=orde, prodcount=prodcount,ord_deets=ord_deets,ord_deets2=ord_deets2)

"""Vendor goes to shops"""
@app.route("/vendor/shop")
def exit_to_shop():
    session.pop('vendor',None)
    return redirect("/home")

"""View Orders"""
@app.route("/vendor/view/orders")
def vendor_view_orders():
    loggedin = session.get('vendor')
    if loggedin == None:
        flash("Please signin to proceed")
        return redirect("/vendor/login")
    else:
        vdeets = Vendor.query.filter(Vendor.vendorid == loggedin).all()

        prodcount = Products.query.filter(Products.vendorid == loggedin).count()

        ord_deets2 = Order_details.query.join(Orders,Order_details.orderid==Orders.orderid).join(Products,Order_details.productid==Products.productid).join(Vendor,Products.vendorid==Vendor.vendorid).add_columns(Orders,Products,Vendor).filter(Vendor.vendorid==loggedin,Orders.orderstatus=="Pending").count()

        ord_deets = Order_details.query.join(Orders,Order_details.orderid==Orders.orderid).join(Products,Order_details.productid==Products.productid).join(Vendor,Products.vendorid==Vendor.vendorid).join(Payments,Orders.orderid==Payments.orderid).add_columns(Orders,Products,Vendor,Payments).filter(Vendor.vendorid==loggedin,Orders.orderstatus=="Pending").order_by(desc(Orders.orderdate)).all()

        proddeets = Products.query.join(Categories,Products.categoryid==Categories.categoryid).add_columns(Categories).filter(Products.vendorid == loggedin).all()

        return render_template("vendor/vendororderview.html",proddeets=proddeets,prodcount=prodcount,vdeets=vdeets,ord_deets2=ord_deets2,ord_deets=ord_deets)

"""Vendor editing orders"""
@app.route("/vendor/edit/order/<id>",methods=['POST','GET'])
def vendor_edit_orders(id):
    loggedin = session.get('vendor')
    if loggedin == None:
        flash("Please signin to proceed")
        return redirect("/vendor/login")
    else:
        if request.method == 'GET':
            vdeets = Vendor.query.filter(Vendor.vendorid == loggedin).all()

            prodcount = Products.query.filter(Products.vendorid == loggedin).count()

            ord_deets2 = Order_details.query.join(Orders,Order_details.orderid==Orders.orderid).join(Products,Order_details.productid==Products.productid).join(Vendor,Products.vendorid==Vendor.vendorid).join(Payments,Orders.orderid==Payments.orderid).add_columns(Orders,Products,Vendor,Payments).filter(Vendor.vendorid==loggedin,Orders.orderstatus=="Pending").count()

            ord1 = Orders.query.get(id)

            ord = ord1.orderid

            proddeets = Products.query.join(Categories,Products.categoryid==Categories.categoryid).add_columns(Categories).filter(Products.vendorid == loggedin).all()


            return render_template("/vendor/vendororderedit.html",proddeets=proddeets,prodcount=prodcount,vdeets=vdeets,ord_deets2=ord_deets2,ord=ord)
        
        else:
            order = request.form.getlist('order')
            msg = request.form.get('message')

            ord_stat = Orders.query.get(id)

            ord_stat.orderstatus = order[0] 

            ord_stat.message = msg

            db.session.commit()

            flash('Order has been updated')
            return redirect("/vendor/view/orders")

"""View products"""

@app.route("/vendor/view/products")
def view_products():

    if session.get('vendor') == None:
        flash("Please signin to proceed")
        return redirect("/vendor/login")
    else:
        loggedin = session.get("vendor")

        ord_deets2 = Order_details.query.join(Orders,Order_details.orderid==Orders.orderid).join(Products,Order_details.productid==Products.productid).join(Vendor,Products.vendorid==Vendor.vendorid).add_columns(Orders,Products,Vendor).filter(Vendor.vendorid==loggedin,Orders.orderstatus=="Pending").count()

        vdeets = Vendor.query.filter(Vendor.vendorid == loggedin).all()

        prodcount = Products.query.filter(Products.vendorid == loggedin).count()

        proddeets = Products.query.join(Categories,Products.categoryid==Categories.categoryid).add_columns(Categories).filter(Products.vendorid == loggedin).all()

        return render_template("vendor/vendorproductview.html",proddeets=proddeets,prodcount=prodcount,vdeets=vdeets,ord_deets2=ord_deets2)

"""Vendor Add Products"""

@app.route("/vendor/update/products")
def add_products_form():
    if session.get('vendor') == None:
        flash("Please signin to proceed")
        return redirect("/vendor/login")
    else:
        loggedin = session.get("vendor")

        ord_deets2 = Order_details.query.join(Orders,Order_details.orderid==Orders.orderid).join(Products,Order_details.productid==Products.productid).join(Vendor,Products.vendorid==Vendor.vendorid).add_columns(Orders,Products,Vendor).filter(Vendor.vendorid==loggedin).count()

        vdeets = Vendor.query.filter(Vendor.vendorid == loggedin).all()

        prodcount = Products.query.filter(Products.vendorid == loggedin).count()

        ct = Categories.query.all()

        return render_template("vendor/vendoraddproduct.html", vdeets=vdeets,prodcount=prodcount,ord_deets2=ord_deets2,ct=ct)

"""Vendor add product 2"""

@app.route("/vendor/add/product", methods=['POST','GET'])
def add_products():
    if session.get('vendor') == None:
        flash("Please signin to proceed")
        return redirect("/vendor/login")
    else:
        loggedin = session.get("vendor")

        name = request.form.get('productname')
        imageobj = request.files['productpix']
        description = request.form.get('productdesc')
        category = request.form.get('category')
        price = request.form.get('price')
        quantity = request.form.get('quantity')
    

        original_name = imageobj.filename 

        newname = random.random() * 1000000     

        picturename,ext = os.path.split(original_name) 


        if ext.endswith(".jpg") or ext.endswith(".jpeg") or ext.endswith(".png") and name != None and description != None and category != None and price != None and quantity != None:
            
            imageobj.save("haadupkg/static/uploads/"+str(newname)+ext)

            newproduct = Products(product_name=name,product_img=str(newname)+ext,product_description=description,categoryid=category,vendorid=loggedin,price=price,quantity=quantity)

            db.session.add(newproduct)
            db.session.commit()


            flash('Prouct has been uploaded successfully')
            return redirect("/vendor/dashboard")
        else:
            flash('Please ensure the form is filled correctly')
            return redirect("/vendor/update/products")

"""Vendor edit product error"""

@app.route("/product/edit/error")
def vendor_edit_error():
    loggedin = session.get('vendor')

    return render_template("vendor/vendorproductediterror.html", loggedin=loggedin)

"""vendor Edit Products"""

@app.route("/vendor/edit/product/<id>")
def vendor_edit_product(id):
    loggedin = session.get('vendor')

    if loggedin != None:
        
        edit_p = Products.query.join(Categories,Products.categoryid==Categories.categoryid).add_columns(Categories).filter(Products.productid == id).all()
        vdeets = Vendor.query.filter(Vendor.vendorid == loggedin).all()

        prodcount = Products.query.filter(Products.vendorid == loggedin).count()

        return render_template("vendor/vendorproductedit.html",vdeets=vdeets, prodcount=prodcount,edit_p=edit_p)

    else:
        flash("You will be required to be logged in to continue")
        return redirect("/vendor/login")

    
        

@app.route("/edit/product/", methods=['POST'])
def edit_product():
    loggedin = session.get('vendor')

    name = request.form.get('productname')
    id = request.form.get('productid')
    imageobj = request.files['productpix']
    description = request.form.get('productdesc')
    category = request.form.get('category')
    price = request.form.get('price')
    quantity = request.form.get('quantity')

    if loggedin != None:
        try:
            edit_prod = Products.query.filter(Products.productid == id).all()

            original_name = imageobj.filename 

            newname = random.random() * 1000000     

            picturename,ext = os.path.split(original_name) 

            
            if ext.endswith(".jpg") or ext.endswith(".jpeg") or ext.endswith(".png") and name != None and description != None and category != None and price != None and quantity != None:
                
                imageobj.save("haadupkg/static/uploads/"+str(newname)+ext)
                
                for i in edit_prod:

                    i.product_name = name
                    i.product_img = str(newname)+ext
                    i.product_description = description
                    i.categoryid = category
                    i.price=price
                    i.quantity = quantity

                db.session.commit()

                flash('You product has been updated successfully')
                return redirect("/vendor/view/products")
            else:
                flash('Please ensure the fields are properly filled.')
                return redirect('/vendor/edit/product/<id>')
        except Exception:
            return redirect('/product/edit/error')
    else:
        flash("You will be required to be logged in to continue")
        return redirect("/vendor/login")

    

"""Vendor Delete Products"""

@app.route("/delete/product/<myid>")
def product_delete(myid):
    try:
        delete_product = Products.query.get(myid)
        db.session.delete(delete_product)
        db.session.commit()

        flash("Product has been deleted!")
        return redirect("/vendor/view/products")
    except Exception:
            return redirect('/product/edit/error')

"""vendor profile edit"""

@app.route("/vendor/profile/edit")
def vendor_edit_profile():
    loggedin = session.get('vendor')

    if loggedin != None:
        
        vdeets = Vendor.query.filter(Vendor.vendorid == loggedin).all()

        vedit = Vendorregistration()

        state = State.query.all()

        prodcount = Products.query.filter(Products.vendorid == loggedin).count()

        return render_template("vendor/vendorprofileedit.html",vdeets=vdeets, prodcount=prodcount,vedit=vedit, state=state)

    else:
        flash("You will be required to be logged in to continue")
        return redirect("/vendor/login")

    
        

@app.route("/vendor/profile/update/", methods=['POST'])
def edit_profile():
    loggedin = session.get('vendor')

    name = request.form.get('vendorname')
    shoptype = request.form.get('shoptype')
    email = request.form.get('email')
    address = request.form.get('address')
    phone = request.form.get('phone')
    state = request.form.get('state')

    if loggedin != None:

        edit_vend = Vendor.query.filter(Vendor.vendorid == loggedin).all()
        
        if name != None and shoptype != None and email != None and address != None and phone != None and state != None:
             
            for i in edit_vend:

                i.vendor_name = name
                i.vendor_type = shoptype
                i.email = email
                i.address = address
                i.phone = phone
                i.stateid = state

            db.session.commit()

            flash('You product has been updated successfully')
            return redirect("/vendor/profile/edit")
        else:
            flash('Please ensure the fields are properly filled.')
            return redirect("/vendor/profile/edit")
    else:
        flash("You will be required to be logged in to continue")
        return redirect("/vendor/login")

"""vendor profile picture change """

@app.route("/vendor/picture/<id>")
def vendor_edit_picture(id):
    loggedin = session.get('vendor')

    if loggedin != None:
        
        vdeets = Vendor.query.filter(Vendor.vendorid == loggedin).all()

        prodcount = Products.query.filter(Products.vendorid == loggedin).count()

        return render_template("vendor/vendorprofilepictureedit.html",vdeets=vdeets, prodcount=prodcount)

    else:
        flash("You will be required to be logged in to continue")
        return redirect("/vendor/login")

    
        

@app.route("/edit/vendor/picture", methods=['POST'])
def edit_vendor_picture():
    loggedin = session.get('vendor')

    imageobj = request.files['profilepix']
    
    edit_vend = Vendor.query.filter(Vendor.vendorid == loggedin).all()

    original_name = imageobj.filename 

    newname = random.random() * 1000000     

    picturename,ext = os.path.split(original_name) 

        
    if ext.endswith(".jpg") or ext.endswith(".jpeg") or ext.endswith(".png"):
            
        imageobj.save("haadupkg/static/uploads/"+str(newname)+ext)

        filename = str(newname)+ext
            
        for i in edit_vend:

            i.vendor_img = str(newname)+ext

        db.session.commit()

        flash('You product has been updated successfully')
        return redirect("/vendor/picture/<id>")
    else:
        flash("<p class='alert alert-danger'>Please ensure your profile picture is in any of these format: .jpg, .jpeg, .png </p>")
        return redirect("/vendor/picture/<id>")

"""Vendor view transactions"""
@app.route("/vendor/view/transactions")
def vendor_transactions():
    loggedin = session.get('vendor')
    if loggedin != None:
        vdeets = Vendor.query.filter(Vendor.vendorid == loggedin).all()

        prodcount = Products.query.filter(Products.vendorid == loggedin).count()

        ord_deets2 = Order_details.query.join(Orders,Order_details.orderid==Orders.orderid).join(Products,Order_details.productid==Products.productid).join(Vendor,Products.vendorid==Vendor.vendorid).add_columns(Orders,Products,Vendor).filter(Vendor.vendorid==loggedin,Orders.orderstatus=="Pending").count()

        ord_deets = Order_details.query.join(Orders,Order_details.orderid==Orders.orderid).join(Products,Order_details.productid==Products.productid).join(Vendor,Products.vendorid==Vendor.vendorid).join(Payments,Orders.orderid==Payments.orderid).add_columns(Orders,Products,Vendor,Payments).filter(Vendor.vendorid==loggedin,Orders.orderstatus=="Pending").order_by(desc(Orders.orderdate)).all()

        proddeets = Products.query.join(Categories,Products.categoryid==Categories.categoryid).add_columns(Categories).filter(Products.vendorid == loggedin).all()

        # return render_template("vendor/vendororderview.html",proddeets=proddeets,prodcount=prodcount,vdeets=vdeets,ord_deets2=ord_deets2,ord_deets=ord_deets)
        payment_deets = Payments.query.join(Orders,Payments.orderid==Orders.orderid).join(Order_details,Orders.orderid==Order_details.orderid).join(Products,Order_details.productid==Products.productid).join(Vendor,Products.vendorid==Vendor.vendorid).add_columns(Orders,Order_details,Products,Vendor).filter(Vendor.vendorid==loggedin,Payments.paymentstatus=="Paid",Orders.orderstatus=="Completed").order_by(desc(Orders.orderdate)).all()
        
        total_amt=[]
        for py,ord,od,pr,ve in payment_deets:
            total_amt.append(int(od.price)*int(od.quantity))
        total = sum(total_amt)
         

        return render_template("vendor/vendortransaction.html",proddeets=proddeets,prodcount=prodcount,vdeets=vdeets,ord_deets2=ord_deets2,ord_deets=ord_deets, payment_deets=payment_deets,total=total)
    else:
        flash("You will be required to login to proceed")
        return redirect("/vendor/login")

"""Vendor Logout"""

@app.route('/vendor/logout')
def vendor_logout():
    session.pop('vendor',None)
    return redirect("/vendor/login")

