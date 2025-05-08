from flask import Flask, render_template, redirect,request,url_for,session, make_response, flash,jsonify
import random
import smtplib
from markupsafe import escape
from flask_wtf import CSRFProtect
from pymongo import MongoClient
import datetime as dt
import os
from dotenv import load_dotenv

from pyngrok import ngrok

# Open a public URL for local port 5000
'''public_url = ngrok.connect(5000)
print("Public URL:", public_url)

# Get the auth token from .env
auth='Q2PZLRHYXST3WFGWDYMBADAHYNSWHFHF'

ngrok.set_auth_token(auth)

'''

load_dotenv() # loading .env file

# Connect to MongoDB
client = MongoClient(os.getenv('MONGO_URI')) 
print(f"client=",client) # Replace with your MongoDB URI
db = client['New'] # Replace with your database 
print(f"db=",db)
collection = db['UserDetails']
collection1=db['Login_details']
collection2=db['Files']
SENDER_EMAIL, SENDER_PASSWORD=os.getenv('SENDER_EMAIL'),os.getenv('SENDER_PASSWORD')
print(f"sender=",SENDER_EMAIL)


#initialize the app

app= Flask(__name__)
app.secret_key=os.getenv('SECRET_KEY')
csrf=CSRFProtect(app)


'''===Root page==='''
@app.route('/')
def home():
    return render_template("index.html")
'''End root'''



'''Get details'''
@app.route('/get_details')
def show():
    data = list(collection.find({}, {'_id': 0}))  # Exclude MongoDB's default '_id' field
    return render_template('show.html', data=data)

'''insert into db'''
@app.route('/insert',methods=['POST','GET'])
def insert():
    if request.method=='POST':
        data=request.form.to_dict()
        result=list(collection.insert_one({data}))
        return render_template('show.html', data=data)
    else:
        pass
    

@app.route('/GoTo_uploadpage/')
def Goto_upload():
    return render_template('upload.html')
''' Name '''

@app.route('/user/<name>/')
def user(name):
    back='<button><a href="http://127.0.0.3:5000/myapplogin/">Back to login</a></button>'
    if name=='karupa':
        return f"This is {escape(name)} super user,{back}"
    else:
        return f"This is {escape(name)} Normal user"

@app.route("/superuser/<super>")
def superuser(super):
    if super=='karupa':
        return redirect(url_for("user",name='karupa'))
    else:
        return redirect(url_for("user",name='super'))

'''Post id'''

'''admin'''


'''====Dynamic content======'''



@app.route('/last page/')
def last():
    return render_template('Last.html')

@app.route('/Admin/')
def Admin():
    return redirect(url_for('admin'))

@app.route('/welcome/')
def wel():
    return render_template('Welcome.html')



@app.route('/mylogin/',methods=['POST','GET'])
def mylogin():

    print("Login function start")

    if request.method=='POST':
        '''user=request.form['username']'''
        user=request.form.get("username")
        print(f"Username {user}")
        password=request.form['psx']
        
        print("user",user,password)
        Login_table=collection1.find_one({'username':user,'password':password})
        user_table=collection.find_one({'username':user,'password':password})

        
    
        if Login_table or user_table:
            #print(collection1.find_one({'username':user,'password':password}))
            #session variable and cookies

            session['username']=user
            print(f"USER befor :{user}")
            resp = make_response(render_template('Welcome.html',name=user))
            resp.set_cookie("username",user,max_age=60*60*24)
            
            #return redirect(url_for('dashboard',name=user))
            return render_template('Welcome.html',name=user)
        else:
            return render_template('no_user.html')

    
@app.route('/Logout/')
def Logout():
    
    session.pop("username", None)  # Clear the session
    resp = make_response(redirect(url_for("login")))
    resp.delete_cookie("username")  # Remove the cookie
    flash("You have been logged out.", "info")
    return resp
    

@app.route('/form/')
def form():
    return render_template('form.html')

@app.route('/Home_page')
def Home_page():
    if session['username']:
        current_user=session['username'] 
        print(session) 
    elif(session['user']):
        current_user=session['user']  
    else:
        return render_template('login.html')
      

    return render_template('Home.html',name=current_user)

@app.route('/login/')
def login():
    return render_template('login.html')
@app.route('/Email_page/')
def Email_page():
    return render_template('Auth/email_auth.html')

@app.route('/Verify_page/')
def Verify_page():
    return render_template('Auth/verify_OTP.html')

@app.route('/Email/', methods=['GET', 'POST'])
def Email():

    if request.method == 'POST':
        email = request.form.get('email')
        x=checkuser(email)
        print("username=",x,checkuser(email))
        if x:
       
        # Add your OTP sending logic here\\
            '''otp=123
            session['OTP']=otp'''
            otp=random.randint(100000,999997)
            session['OTP']=otp
            session['email']=email
            session['user']=x
            # Send OTP (for demonstration, use email)
            send_email(email, otp)
            flash("OTP sent to your email{user}.")

            print(f"email:{email},session:{session['email']},otp:{otp}")

        
            #return f"OTP sent to {email}"
            return redirect('/Verify_page/')
        else:
            return f'{email} not found'
        
    return render_template('/Auth/email_auth.html')

def send_email(recipient, otp):
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            message = f"Subject: Your OTP Code\n\nYour OTP is {otp}."
            server.sendmail(SENDER_EMAIL, recipient, message)
    except Exception as e:
        print(f"Error sending email: {e}")   


def checkuser(username):
    if collection1.find_one({'email':username}):
        Login_username=collection1.find_one({'email':username})
        if not Login_username:
            Login_username=collection.find_one({'email':username})


        
        print(f'Inside checkuser username:{Login_username}')
        #user=jsonify(user.get("username"))
        print(f'after getting username:{Login_username}')
        return Login_username['username']
    
    
        


@app.route('/Verify_otp/',methods=['GET', 'POST'])
def Verify_otp():
    Gen_OTP=session.get('OTP')
    email=session.get('email')
    user=session.get('user')
    '''OTP=session.get('OTP')'''
    
   #check if user exist

    if request.method=='POST':
        OTP=request.form.get('OTP')
        print(f"OTP:{OTP}---Gen_OTP:{Gen_OTP}--{type(OTP)},{type(Gen_OTP)}")

        if Gen_OTP==int(OTP):
           return render_template('Welcome.html',name=user)
        else:
            return f'incorrect OTP,please retry'
        
    return f'Bad request, please retry'


    
@app.route('/success/<name>')    
def success(name):
    return f"Welcome %s {escape(name)}"

@app.route('/In')
def inh():
    return render_template('child.html')


@app.route('/protected_form/' , methods=['POST','GET']) 
def protected_form():

    if request.method=='POST':
      
        data=request.form.to_dict()
        
        
        if data:
            
            try:
                result=collection.insert_one(data)
                flash(f"Data inserted successfully!{result}", "success")
            except Exception as e:
                flash(f"Error inserting data: {e}/ {data.name}", "danger")


            finally: 
                return render_template('Welcome.html')   
            #print(f'Successfully registered {result}')
            '''data1 = list(collection.find({}, {'_id': 0})) 
            return render_template('show.html',data=data1)'''

        else:
            return f'Not a valid Json'
    else:
        pass
    return render_template('index.html')


# uploading a file in mongodb

@app.route('/upload_file',methods=['POST','GET'])
def upload_file():
    if request.method=='POST':
        file=request.files['file']
        print("File",file)
        created_date=dt.datetime.now()

        if file:
            file_data={

                "created_date":created_date,
                "filename":file.filename,
                "content-type":file.content_type,
                "data":file.read()
            }
            if_file_inserted=collection2.insert_one(file_data)
            flash(f"{ if_file_inserted},{file.filename} successfully inserted!!")
            return render_template('success.html',name=session['username'])
        else:
            pass
            
            


if __name__ == "__main__":
    app.run(host="127.0.0.3",debug=True,port=5000)
