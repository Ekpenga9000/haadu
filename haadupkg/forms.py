from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField,FileField,SelectField
from wtforms.validators import DataRequired,Length, Email,EqualTo

class Admin_Registration(FlaskForm):
    adminname = StringField("Admin Name", validators=[DataRequired(message="Please enter your full name to proceed")])
    username = StringField("Username",validators=[DataRequired(message="Your username must be at least 5 characters long"),Length(min=5)])
    password = PasswordField("Password",validators=[DataRequired(message="Your password must be at least 5 characters long"),Length(min=5)])
    cpassword = PasswordField("Confirm password",validators=[EqualTo("password")])
    submit = SubmitField("Submit")

class Adminlogin(FlaskForm):
    username = StringField("Username",validators=[DataRequired(message="Your username must be at least 5 characters long"),Length(min=5)])
    password = PasswordField("Password",validators=[DataRequired(message="Your password must be at least 5 characters long"),Length(min=5)])
    submit = SubmitField("Submit")

class Userregistration(FlaskForm):
    firstname = StringField("First Name", validators=[DataRequired(message="Please enter your full name to proceed")])
    lastname = StringField("Last Name", validators=[DataRequired(message="Please enter your full name to proceed")])
    email_addy = StringField("Email", validators=[Email(message="Please enter a valid email address")])
    phone = StringField("Phone number", validators=[DataRequired(message="Please input a valid mobile number"),Length(min=11,max=11)])
    username = StringField("Username",validators=[DataRequired(message="Your username must be at least 5 characters long"),Length(min=5)])
    password = PasswordField("Password",validators=[DataRequired(message="Your password must be at least 5 characters long"),Length(min=5)])
    cpassword = PasswordField("Confirm password",validators=[EqualTo("password")])
    submit = SubmitField("Submit")


class Userlogin(FlaskForm):
    username = StringField("Username",validators=[DataRequired(message="Your username must be at least 5 characters long"),Length(min=5)])
    password = PasswordField("Password",validators=[DataRequired(message="Your password must be at least 5 characters long"),Length(min=5)])
    submit = SubmitField("Submit")

class Vendorregistration(FlaskForm):
    vendorname = StringField("Vendor's Name", validators=[DataRequired(message="Please enter your full name to proceed")])
    shoptype = SelectField(u'Shop Type', choices=[('Corporate', 'Corporate'), ('Individual', 'Individual')])
    email = StringField("Email", validators=[Email(message="Please enter a valid email address")])
    phone = StringField("Phone number", validators=[DataRequired(message="Please input a valid mobile number"),Length(min=11,max=11)])
    address=TextAreaField()
    state = SelectField(u'State', choices=[('', '--Please select state--'),('1', 'Abia State'),('2', 'Adamawa State'), ('3', 'Akwa Ibom State'),('4', 'Anambra State'),('5', 'Bauchi State'),('6', 'Bayelsa State'),('7', 'Benue State'),('8', 'Borno State'),('9', 'Cross River State'),('10', 'Delta State'),('11', 'Ebonyi State'),('12', 'Edo State'),('13', 'Ekiti State'),('14', 'Enugu State'),('15', 'Gombe State'),('16', 'Imo State'),('17', 'Jigawa State'),('18', 'Kaduna State'),('19', 'Kano State'),('20', 'Katsina State'),('21', 'Kebbi State'),('22', 'Kogi State'),('23', 'Kwara State'),('24', 'Lagos State'),('25', 'Nasarawa State'),('26', 'Niger State'),('27', 'Ogun State'),('28', 'Ondo State'),('29', 'Osun State'),('30', 'Oyo State'),('31', 'Plateau State'),('32', 'Rivers State'),('33', 'Sokoto State'),('34', 'Taraba State'),('35', 'Yobe State'),('36', 'Zamfara State'),('37', 'Federal Capital Territory')])

    username = StringField("Username",validators=[DataRequired(message="Your username must be at least 5 characters long"),Length(min=5)])
    password = PasswordField("Password",validators=[DataRequired(message="Your password must be at least 5 characters long"),Length(min=5)])
    cpassword = PasswordField("Confirm password",validators=[EqualTo("password")])
    submit = SubmitField("Submit")

class Vendorlogin(FlaskForm):
    username = StringField("Username",validators=[DataRequired(message="Your username must be at least 5 characters long"),Length(min=5)])
    password = PasswordField("Password",validators=[DataRequired(message="Your password must be at least 5 characters long"),Length(min=5)])
    submit = SubmitField("Submit")



