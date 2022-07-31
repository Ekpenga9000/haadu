
import random,os
from flask import Flask, render_template, make_response, render_template_string, request, redirect, flash,session,url_for
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import values,desc
from datetime import datetime
from PIL import Image
from haadupkg import app, db,csrf
from haadupkg.models import *
from haadupkg.forms import Admin_Registration, Adminlogin


"""Admin registration"""

@app.route("/admin/register", methods=['POST','GET'])
def admin_register():

    signup = Admin_Registration()

    if request.method == 'GET':
        return render_template("admin/adminsignup.html", signup=signup)

    else:
        if signup.validate_on_submit():
            adminname = request.form.get("adminname")
            username = request.form.get("username")
            password = request.form.get("password")

            hash = generate_password_hash(password)

            admin = Admin(adminname=adminname,username=username,password=hash)

            db.session.add(admin)
            db.session.commit()

            return redirect("/admin/login")
        else:
            flash("Please input your details correctly.")
            return render_template("admin/adminsignup.html",signup=signup)


"""Admin Login"""

@app.route("/admin/validate", methods=['POST'])
def admin_validator():

    login = Adminlogin()

    if request.method == 'GET':
        return render_template("admin/adminlogin.html",login=login)
    else:
        username = request.form.get("username")
        password = request.form.get("password")

        deets = Admin.query.filter(Admin.username == username).first()

        if deets and check_password_hash(deets.password, password):
            deets= deets.adminid
            session['guest'] = deets
            return redirect("/admin/dashboard")
        else:
            flash('Invalid credentials')
            return redirect("/admin/login")

@app.route("/admin/login")
def admin_login():

    login = Adminlogin()
    return render_template("admin/adminlogin.html",login=login)
   
      
"""Admin dashboard"""

@app.route("/admin/dashboard")
def admin_dashboard():
    if session.get('guest') == None:
        return redirect('/admin/login')
    else:
        loggedin = session.get('guest')

        deets = Admin.query.filter(Admin.adminid == loggedin).all()


        cust = User.query.count()

        prod = Products.query.count()
       
        vend = Vendor.query.count()
        

        orde = Orders.query.count()
        

        return render_template("admin/admin.html", deets=deets,cust=cust,prod=prod,vend=vend,orde=orde)

"""Admin Catorgy error message"""

@app.route("/admin/category/error")
def admin_cat_error():
    loggedin = session.get('guest')
    return render_template("admin/admin_category_error.html",loggedin=loggedin)

"""Admin categories"""

@app.route("/admin/category")
def admin_cate():
    if session.get('guest') == None:
        return redirect('/admin/login')
    else:
        loggedin = session.get('guest')

        deets = Admin.query.filter(Admin.adminid == loggedin).all()

        cate = Categories.query.all()

        cust = User.query.count()

        prod = Products.query.count()
       
        vend = Vendor.query.count()
        

        orde = Orders.query.count()
    return render_template("admin/admin_category.html",deets=deets,cust=cust,prod=prod,vend=vend,orde=orde,cate=cate)


@app.route("/admin/add/category", methods=['POST'])
def add_category():
    if session.get('guest') == None:
        flash("Please signin to proceed")
        return redirect("/admin/login")
    else:
        loggedin = session.get("guest")

        name = request.form.get('categoryname')
        imageobj = request.files['categorypix']
        description = request.form.get('categorydesc')
    

        original_name = imageobj.filename 

        newname = random.random() * 1000000     

        picturename,ext = os.path.split(original_name) 


        if ext.endswith(".jpg") or ext.endswith(".jpeg") or ext.endswith(".png") and name != None and description != None:
            
            imageobj.save("haadupkg/static/category/"+str(newname)+ext)

            

            newcategory = Categories(category_img=str(newname)+ext,category_name=name,category_description=description)

            db.session.add(newcategory)
            db.session.commit()


            flash('Prouct has been uploaded successfully')
            return redirect("/admin/category")
        else:
            flash('Please ensure the form is filled correctly')
            return redirect("/admin/category")

"""Admin Edit Category"""

@app.route("/admin/edit/category/<id>")
def edit_cate(id):
    loggedin = session.get('guest')

    if loggedin != None:

        deets = Admin.query.filter(Admin.adminid == loggedin).all()

        cate_edit = Categories.query.filter(Categories.categoryid == id).all()

        cate = Categories.query.all()

        cust = User.query.count()

        prod = Products.query.count()
       
        vend = Vendor.query.count()

        orde = Orders.query.count()

        return render_template("admin/admineditcategory.html",deets=deets,cust=cust,prod=prod,vend=vend,orde=orde,cate=cate,cate_edit=cate_edit)

@app.route("/admin/cat/submit/", methods=['POST'])
def submitedit_cate():

    categoryid = request.form.get('categoryid')
    category_image = request.files['category_image']
    category_name = request.form.get('category_name')
    category_description=request.form.get('category_description')


    originame_name = category_image.filename

    newname = random.random() * 1000

    picturename,ext=os.path.split(originame_name)
    try:
        if ext.endswith(".png") or ext.endswith(".jpg") or ext.endswith(".jpeg") and category_name != None and category_name != '' and category_description != None and category_description != '':

            category_image.save("haadupkg/static/category/"+str(newname)+ext)  

            cate_del = Categories.query.get(categoryid)

            cate_del.categoryid = categoryid
            cate_del.category_img = str(newname)+ext
            cate_del.category_name = category_name
            cate_del.category_description = category_description

            # db.session.execute(f"UPDATE categories SET categoryid = {categoryid} ,category_img = '{str(newname)+ext}',category_name = '{category_name}',category_description = '{category_description}' WHERE categoryid = {categoryid}")

            db.session.commit()

            flash("Category has been updated.")
            return redirect("/admin/category")
            
        else:
            flash("Please ensure the form is filled correctly")
            return redirect("/admin/edit/category/<id>")
    except Exception:
        return render_template("/admin/category/error")

"""Admin Delete Category"""

@app.route("/admin/delete/category/<id>")

def delete_category(id):
    loggedin = session.get('guest')

    if loggedin != None:
        try:
            cate_del = Categories.query.get(id)

            db.session.delete(cate_del)
            db.session.commit()

            flash('Catergory has been deteled')
            return redirect("/admin/category")
        except Exception:
            return redirect("/admin/category/error")
    else:
        flash("Please login to proceed")
        return redirect("/admin/login")


"""Admin All customers"""

@app.route("/admin/customers")
def admin_customers():
    if session.get('guest') != None:
        loggedin = session.get('guest')
        deets = Admin.query.filter(Admin.adminid == loggedin).all()
        cust = User.query.count()
        prod = Products.query.count()
        vend = Vendor.query.count()
        orde = Orders.query.count()
        cust2 =User.query.all()
        return render_template("admin/admincustomers.html",deets=deets, cust=cust, cust2=cust2,prod=prod,vend=vend,orde=orde) 
    else:
        flash("You have been logged out.")
        return redirect("/admin/login")


"""Delete customers"""

@app.route("/delete/customer/<myid>")
def admin_delete(myid):

    delete_customer = User.query.get(myid)
    db.session.delete(delete_customer)
    db.session.commit()

    flash("Product has been deleted!")
    return redirect("/admin/customers")

"""Admin All vendors"""

@app.route("/admin/vendors")
def admin_vendors():
    if session.get('guest') != None:
        loggedin = session.get('guest')
        deets = Admin.query.filter(Admin.adminid == loggedin).all()
        cust = User.query.count()
        prod = Products.query.count()
        vend = Vendor.query.count()
        orde = Orders.query.count()
        vend2 = Vendor.query.all()
        
        return render_template("admin/adminvendors.html",vend=vend,vend2=vend2,deets=deets, cust=cust, orde=orde,prod=prod)
    else:
        flash("You have been logged out.")
        return redirect("/admin/login")

"""Admin delete vendors"""

@app.route("/delete/vendor/<myid>")
def vendor_delete(myid):

    delete_vendor = Vendor.query.get(myid)
    db.session.delete(delete_vendor)
    db.session.commit()

    flash("Product has been deleted!")
    return redirect("/admin/vendors")



"""Admin all products"""

@app.route("/admin/products")
def admin_products():
    if session.get('guest') != None:
        loggedin = session.get('guest')
        deets = Admin.query.filter(Admin.adminid == loggedin).all()
        cust = User.query.count()
        prod = Products.query.count()
        vend = Vendor.query.count()
        orde = Orders.query.count()
        prod2 = Products.query.join(Categories,Products.categoryid==Categories.categoryid).add_columns(Categories).all()
        return render_template("admin/adminproducts.html",deets=deets,cust=cust,vend=vend,orde=orde,prod2=prod2,prod=prod)
    else:
        flash("You have been logged out.")
        return redirect("/admin/login")

"""Admin delete products"""

@app.route("/delete/product/<myid>")
def adminproduct_delete(myid):

    product_delete = Products.query.get(myid)
    db.session.delete(product_delete)
    db.session.commit()

    flash("Product has been deleted!")
    return redirect("/admin/products")


"""Admin all orders"""

@app.route("/admin/orders")
def admin_orders():
    if session.get('guest') != None:
        loggedin = session.get('guest')
        deets = Admin.query.filter(Admin.adminid == loggedin).all()
        cust = User.query.count()
        prod = Products.query.count()
        vend = Vendor.query.count()
        orde = Orders.query.count()
        ord = Orders.query.join(User,Orders.userid==User.userid).join(Payments,Orders.orderid==Payments.orderid).add_columns(User,Payments).order_by(desc(Orders.orderdate)).all()
        return render_template("admin/adminorders.html", ord=ord,deets=deets,cust=cust,prod=prod,vend=vend,orde=orde)
    else:
        flash("You have been logged out.")
        return redirect("/admin/login")

"""Admin delete orders"""

@app.route("/edit/orders/<myid>")
def orders_edit(myid):

    loggedin = session.get('guest')
    if loggedin != None:

        deets = Admin.query.filter(Admin.adminid == loggedin).all()
        cust = User.query.count()
        prod = Products.query.count()
        vend = Vendor.query.count()
        orde = Orders.query.count()
        # ord = Orders.query.join(User,Orders.userid==User.userid).join(Payments,Orders.orderid==Payments.orderid).add_columns(User,Payments).all()
        ord1 = Orders.query.get(myid)
        
        ord = ord1.orderid
        return render_template("admin/admineditorder.html", ord=ord,deets=deets,cust=cust,prod=prod,vend=vend,orde=orde)
        
        # if request.form == 'GET':
        #     deets = Admin.query.filter(Admin.adminid == loggedin).all()
        #     cust = User.query.count()
        #     prod = Products.query.count()
        #     vend = Vendor.query.count()
        #     orde = Orders.query.count()
        #     # ord = Orders.query.join(User,Orders.userid==User.userid).join(Payments,Orders.orderid==Payments.orderid).add_columns(User,Payments).all()
        #     ord1 = Orders.query.get(id)
        
        #     ord = ord1.orderid
        #     return render_template("admin/admineditorder.html", ord=ord,deets=deets,cust=cust,prod=prod,vend=vend,orde=orde)
        # else:
        #     order = request.form.getlist('order1')

        #     ord_stat = Orders.query.get(myid)

        #     ord_stat.orderstatus = order

        #     db.session.commit()

        #     flash("Order status has been updated.")
        #     return redirect("/admin/orders")
    else:
        flash("You have been logged out.")
        return redirect("/admin/login")

@app.route("/admin/order_status_update/<id>",methods=['POST'])
def admin_update_status(id):
    try:
        order = request.form.getlist('order1')
        msg = request.form.get("message")
        ord_stat = Orders.query.get(id)

        ord_stat.orderstatus = order[0]
        ord_stat.message = msg

        db.session.commit()

        flash("Order status has been updated.")
        return redirect("/admin/orders")
    except Exception:
        return redirect("/admin/login")


"""Admin Logout"""

@app.route('/admin/logout')
def admin_logout():
    session.pop('guest',None)
    return redirect("/admin/login")

"""Admin panel"""

@app.route('/admin/panel')
def admin_panel():
    if session.get('guest') == None:
        return redirect("/admin/login")
    else:
        loggedin = session.get('guest')

        cust1 = User.query.all()
        cust = len(cust1)

        prod1 = Products.query.all()
        prod = len(prod1)

        vend1 = Vendor.query.all()
        vend = len(vend1)

        orde1 = Orders.query.all()
        orde = len(orde1)
        #retrieving the object of the table. 
        deets=Admin.query.filter(Admin.adminid==loggedin).all()

        return render_template("admin/admintemplate.html",deets=deets,cust=cust,prod=prod,vend=vend,orde=orde)