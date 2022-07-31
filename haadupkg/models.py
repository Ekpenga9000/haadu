from datetime import datetime
import email
import enum
from enum import unique
from haadupkg import db 





class State(db.Model):
    stateid = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    state_name = db.Column(db.String(255),nullable=False) 

class User(db.Model):
    userid = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    firstname = db.Column(db.String(100),nullable=False)
    lastname = db.Column(db.String(100),nullable=False)
    email = db.Column(db.String(100),nullable=False)
    address = db.Column(db.Text())
    phone = db.Column(db.String(12),nullable=False)
    stateid = db.Column(db.Integer(),db.ForeignKey('state.stateid'))
    username = db.Column(db.String(100),nullable=False,unique=True)
    password = db.Column(db.String(255),nullable=False)
    datereg = db.Column(db.DateTime(), default=datetime.utcnow())

    userstateview = db.relationship('State',backref='userstate')

class Vendor(db.Model):
    vendorid = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    vendor_img = db.Column(db.String(255), nullable = True)
    vendor_name = db.Column(db.String(255),nullable=False)
    vendor_type = db.Column(db.String(30), nullable=False) #This will be provided as a select option. maybe later we will use the enum. 
    email = db.Column(db.String(100),nullable=False)
    address = db.Column(db.Text())
    phone = db.Column(db.String(12),nullable=False)
    stateid = db.Column(db.Integer(),db.ForeignKey('state.stateid'))
    username = db.Column(db.String(100),nullable=False,unique=True)
    password = db.Column(db.String(255),nullable=False)
    datereg = db.Column(db.DateTime(), default=datetime.utcnow())

    stateview = db.relationship('State',backref='vendorstate') #relationship with the state from the vendor.

class Categories(db.Model):
    categoryid = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    category_img = db.Column(db.String(255),nullable=True) 
    category_name = db.Column(db.String(255),nullable=False) 
    category_description = db.Column(db.Text())

    prodview = db.relationship('Products',backref='cprod',overlaps="cprod,prodview")

class Products(db.Model):
    productid = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    product_name = db.Column(db.String(255),nullable=False) 
    product_img = db.Column(db.String(255), nullable=False)
    product_description = db.Column(db.Text(), nullable=False)
    categoryid = db.Column(db.Integer(), db.ForeignKey('categories.categoryid'), nullable=False)
    vendorid = db.Column(db.Integer(), db.ForeignKey('vendor.vendorid'), nullable=False)
    price= db.Column(db.Integer(), nullable=False)
    quantity = db.Column(db.Integer(), nullable=False)
    datereg = db.Column(db.DateTime(), default=datetime.utcnow())

    
    pvendview = db.relationship('Vendor', backref='pvend') #relationship with the Vendor from the products.

class Orders(db.Model):
    orderid = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    orderdate = db.Column(db.DateTime(), default=datetime.utcnow())
    orderref = db.Column(db.Integer(),nullable=False)
    orderamt = db.Column(db.Float(),nullable=False)
    orderstatus = db.Column(db.Enum("Completed","Processing","Pending","Cancelled"), nullable=False )
    message = db.Column(db.Text(), nullable=True )
    shippingaddress= db.Column(db.Text())
    shippingdate = db.Column(db.DateTime())
    shippingfee = db.Column(db.Integer(), nullable=False)
    userid = db.Column(db.Integer(), db.ForeignKey('user.userid'), nullable=False)
    
class Order_details(db.Model):
    order_details_id = db.Column(db.Integer(),primary_key = True, autoincrement=True)
    orderid = db.Column(db.Integer(), db.ForeignKey('orders.orderid'), nullable=False)
    productid = db.Column(db.Integer(), db.ForeignKey('products.productid'), nullable=False) 
    price = db.Column(db.Integer(), nullable=False)
    quantity = db.Column(db.Integer(), nullable=False)


class Payments(db.Model):
    paymentid = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    userid = db.Column(db.Integer(), db.ForeignKey('user.userid'), nullable=False)
    orderid = db.Column(db.Integer(), db.ForeignKey('orders.orderid'), nullable=False)
    paymentmode = db.Column(db.String(20),nullable=False)
    amount = db.Column(db.Integer(), nullable=False)
    paymentref=db.Column(db.Integer())
    paymentstatus=db.Column(db.Enum("Paid","Pending","Failed"), nullable=False )
    paymentdate= db.Column(db.DateTime(), default=datetime.utcnow())
    paymentfeedback = db.Column(db.String(255), nullable=False)

class Reviews(db.Model):
    reviewid = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    userid=db.Column(db.Integer(), db.ForeignKey('user.userid'),nullable=False)
    orderid=db.Column(db.Integer(), db.ForeignKey('orders.orderid'),nullable=False)
    comment=db.Column(db.Text())
    stars = db.Column(db.Integer(), nullable=True)
    dateposted=db.Column(db.DateTime(), default=datetime.utcnow())

class Cart(db.Model):
    cartid = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    userid=db.Column(db.Integer(), db.ForeignKey('user.userid'),nullable=False)
    productid = db.Column(db.Integer(), db.ForeignKey('products.productid'), nullable=False)
    quantity = db.Column(db.Integer(), nullable=True)
    amount = db.Column(db.Float(), nullable=False)

    cart_product = db.relationship('Products',backref='cartprod')

class Admin(db.Model):
    adminid = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    adminname = db.Column(db.String(100),nullable=False)
    username = db.Column(db.String(100),nullable=False,unique=True)
    password = db.Column(db.String(255),nullable=False)
    datereg = db.Column(db.DateTime(), default=datetime.utcnow(), nullable=False)
    userid = db.Column(db.Integer(), db.ForeignKey('user.userid'), nullable=True)
    categoryid = db.Column(db.Integer(), db.ForeignKey('categories.categoryid'), nullable=True)
    vendorid = db.Column(db.Integer(), db.ForeignKey('vendor.vendorid'), nullable=True)
    orderid = db.Column(db.Integer(), db.ForeignKey('orders.orderid'), nullable=True)
    productid = db.Column(db.Integer(), db.ForeignKey('products.productid'), nullable=True)
    paymentid = db.Column(db.Integer(), db.ForeignKey('payments.paymentid'), nullable=True)
    stateid = db.Column(db.Integer(), db.ForeignKey('state.stateid'), nullable=True)

    