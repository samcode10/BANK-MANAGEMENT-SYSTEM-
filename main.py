from flask import Flask, render_template,request, redirect
import pymysql as sql
from flask import session
from getpass import getpass
import math
import random
import smtplib


app = Flask(__name__)

app.secret_key ="fgokneigurefiuherfiuhegiuj446wrfoierhfi"

def connect():
    db = sql.connect(host='localhost', port=3306, user='root', password='', database='python1pm')
    cur = db.cursor()
    return db,cur

def passkey(password):
        
    lower= 0
    upper=0
    special = 0
    digit = 0
    
    for char in password:
        if char.isdigit():
            digit += 1
        elif char.isupper():
            upper += 1
        elif char.islower():
            lower += 1
        elif not char.isidentifier():
            special += 1
        
    if lower>=1 and upper>=1 and digit>=1 and special>=1 and len(password)>=8:
        return True
    else:
        return False

@app.route('/')
def index():
    if session.get('user'):
        return redirect('/dashboard')

    return render_template('main.html')
@app.route("/login/", methods=['GET','POST'])
def login():
    if request.method == "POST":
        acc_no = request.form.get('acc_no')
        password = request.form.get('password')
        db, cur = connect()
        cmd = f"select acc_no, user_name, balance, email from bank_data where acc_no = '{acc_no}' and password = '{password}'"
        cur.execute(cmd)
        user = cur.fetchone()
        db.commit()

        if user:
            session['user'] = user
            return redirect("/dashboard/")
        else:
            return render_template("login.html",message="Invalid Credentials")


    # Define user outside of the if user: block to ensure it's always defined.
    return render_template('login.html')

@app.route('/signup/')
def signup():
    return render_template('signup.html')

@app.route('/aftersubmit/', methods = ['GET', 'POST'])
def afterSubmit():
    if request.method == "GET":
        return render_template('index.html')
    else:
        name = request.form.get('name')
        password = request.form.get('password')
        email = request.form.get('email')
        db,cur = connect()
        cur.execute(f"select acc_no from bank_data where user_name='{name}';")
        info = cur.fetchone()
        
        # new_acc = info[0][0] +1
        if(info):
            return {"status":"error","message":"Account already exists"}
        
        cmd1 = f"insert into bank_data(user_name, password, balance,email) values('{name}','{password}',2000, '{email}')"
        cur.execute(cmd1)
        db.commit()
        cur.execute(f"select acc_no,user_name,balance,email from bank_data where user_name='{name}';")
        data = cur.fetchone()
        session['user'] = data
        return redirect('/dashboard/')
        # return render_template('dashboard.html', data = data)
        # return {
        #     "status":"success",
        #     "message":f"Account created with account no {data[0]}",
        #     "data":{
        #         "account_no":data[0],
        #         "name":data[1]
        #     }
        # }


@app.route("/dashboard/", methods=['GET', 'POST'])
def afterlogin():
    if session.get("user"):
        return render_template('dashboard.html', data=session.get("user"))
    else:
        return redirect("/login/")

    



@app.route('/chnge-pass/', methods=["POST","GET"])
def chnge_pass():
    if not session.get("user"):
        return redirect("/")
    srvr,crsr = connect()
    new_acc = session.get("user")[0]
    if request.method=="GET":
        digits="0123456789"
        OTP=""
        for i in range(6):
            OTP+=digits[math.floor(random.random()*10)]
        otp = OTP + " is your OTP"
        msg= otp
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login("kuldeepsinghtak10@gmail.com", "fmlekqacqtuadnsd")
        print(session.get("user"))
        emailid = session.get("user")[3]
        s.sendmail('&&&&&&&&&&&',emailid,msg)
        session['otp']=OTP
        print(session['otp'])
        
    if request.method=="POST":
        
        otp = request.form.get("otp")
        if str(otp)== str(session.get('otp')):
            print("Verified")
            new_password = request.form.get("newpass")
            if passkey(new_password):
                new1 = f"update bank_data set password = '{new_password}' where acc_no = {new_acc}"
                crsr.execute(new1)
                srvr.commit()
                return redirect("/dashboard/")
            else:
                return {"message":"Invalid password format. Password must be at least 8 characters long and contain at least one number, one uppercase letter, one lowercase letter, and one special character"}
        else:
            return {"message":"Please Check your OTP again"}
    
    return render_template("chnge.html")

@app.route("/acc_detail/")
def details():
    if not 'user' in session :
        return redirect('/')
    data = session.get("user")
    return render_template("acc_detail.html",data=data)
@app.route('/transactions/', methods=["GET","POST"])
def transaction():
    if not session.get("user"):
        return redirect("index.html")
    if request.method=="GET":
        return render_template("credit-debit.html")
    if request.method=="POST":
        type = request.form.get("transactionType")
        amount = request.form.get("amount")
        db,cur = connect()
        acc_no = session.get("user")[0]
        if type.lower()=="credit":
            cur.execute(f"update bank_data set balance = balance+{amount} where acc_no = {acc_no}")
        elif type.lower()=="debit":
            
            balance = session.get("user")[2]
            if float(amount)>float(balance):
                print("Balance insufficient wala koi alert system") 
            else:
                cur.execute(f"update bank_data set balance = balance-{amount} where acc_no = {acc_no}")
        db.commit()
        
        cur.execute(f"select acc_no,user_name,balance,email from bank_data where acc_no = {acc_no};")
        user = cur.fetchone()
        if user:
            session['user'] = user

        return redirect('/dashboard/')

    
@app.route('/logout/')
def logout():
    if session.get("user"):
        del session['user']
    return redirect('/')


app.run(debug=True)
