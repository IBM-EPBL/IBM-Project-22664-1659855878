from sendgrid import SendGridAPIClient
import re
from sendgrid.helpers.mail import *
from flask import Flask, render_template, request, redirect, session 


import ibm_db


app = Flask(__name__)
app.secret_key = "ibm"

hostname = "2f3279a5-73d1-4859-88f0-a6c3e6b4b907.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud:30756"
uid = "rhv90277"
pwd = "kH6sN97rnNsYcXUU"
driver = "{IBM DB2 ODBC DRIVER}"
db = "bludb"
port = "30756"
protocol = "TCPIP"
cert = "DigiCertGlobalRootCA.crt"

dsn = (
    "DATABASE={0};"
    "HOSTNAME={1};"
    "PORT={2};"
    "UID={3};"
    "SECURITY=SSL;"
    "SSLServerCertificate={4};"
    "PWD={5};"
).format(db, hostname, port, uid, cert, pwd)

print(dsn)

conn = ibm_db.connect(dsn, "", "")

message = ""


@app.route("/home")
def home():
      
      sql = 'SELECT TIME(date)   , amount FROM expenses  WHERE userid = %s AND DATE(date) = DATE(NOW()) '
      stmt = ibm_db.prepare(conn, sql)
      ibm_db.bind_param(stmt, 1, str(session['id']))
      texpense = stmt.fetchall()
      ibm_db.execute(texpense)

      

      print(texpense)
      
      
      sql = 'SELECT * FROM expenses WHERE userid = % s AND DATE(date) = DATE(NOW()) AND date ORDER BY `expenses`.`date` DESC'
      stmt = ibm_db.prepare(conn, sql)
      ibm_db.bind_param(stmt, 1, str(session['id']))
      expense = stmt.fetchall()
      ibm_db.execute(expense)


      
      total = 0
      t_food=0
      t_entertainment=0
      t_business=0
      t_rent=0
      t_EMI=0
      t_other=0
      


      for x in expense:
          total += int(x[4])
          if x[6] == "food":
              t_food += int(x[4])            
          elif x[6] == "entertainment":
              t_entertainment  += int(x[4])
        
          elif x[6] == "business":
              t_business  += int(x[4])
          elif x[6] == "rent":
              t_rent  += int(x[4])
           
          elif x[6] == "EMI":
              t_EMI  += int(x[4])
         
          elif x[6] == "other":
              t_other  += int(x[4])
            
      print(total)  
      print(t_food)
      print(t_entertainment)
      print(t_business)
      print(t_rent)
      print(t_EMI)
      print(t_other)


     
      return render_template("homepage.html", texpense = texpense, expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )



     

@app.route("/")
def add():
    return render_template("home.html")






@app.route("/signup")
def signup():
    return render_template("signup.html")



@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' :
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        sql = "SELECT * FROM register WHERE username = % s"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, username)
        ibm_db.execute(stmt)

        account = ibm_db.fetch_assoc(stmt)
        print("Account - ", end="")
        print(account)
        
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'name must contain only characters and numbers !'
        else:
            insert_sql = "INSERT INTO register VALUES (?, ?, ?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, username)
            ibm_db.bind_param(prep_stmt, 2, email)
            ibm_db.bind_param(prep_stmt, 3, password)
            ibm_db.execute(prep_stmt)

            session['loggedin'] = True
            session['id'] = email
            session['email'] = email
            session['username'] = username
            msg = 'You have successfully registered !'
            return render_template('signup.html', msg = msg)
        
        
 
      
    
@app.route("/signin")
def signin():
    return render_template("login.html")
        
@app.route('/login',methods =['GET', 'POST'])
def login():
    global userid
    msg = ''
   
  
    if request.method == 'POST' :
        username = request.form['username']
        password = request.form['password']
       
        sql = "SELECT * FROM register WHERE username = % s AND password = % s"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, username)
        ibm_db.bind_param(stmt, 2, password)
        ibm_db.execute(stmt)

        account = ibm_db.fetch_assoc(stmt)
        print("Account - ")
        print(account)
        
        
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            userid=  account[0]
            session['username'] = account[1]

            send_email()
           
            return redirect('/register')
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)



@app.route("/add")
def adding():
    return render_template('add.html')


@app.route('/addexpense',methods=['GET', 'POST'])
def addexpense():
    
    date = request.form['date']
    expensename = request.form['expensename']
    amount = request.form['amount']
    paymode = request.form['paymode']
    category = request.form['category']
    
    sql = "INSERT INTO expenses VALUES (NULL,  % s, % s, % s, % s, % s, % s)"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, session['id'])
    ibm_db.bind_param(stmt, 2, date)
    ibm_db.bind_param(stmt, 3, expensename)
    ibm_db.bind_param(stmt, 4, amount)
    ibm_db.bind_param(stmt, 5, paymode)
    ibm_db.bind_param(stmt, 6, category)
    ibm_db.execute(stmt)
    print(date + " " + expensename + " " + amount + " " + paymode + " " + category)
    
    return redirect("/display")



@app.route("/display")
def display():
    print(session["username"],session['id'])
    

    sql = "SELECT * FROM expenses WHERE userid = % s AND date ORDER BY `expenses`.`date` DESC"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, str(session['id']))

    expense = stmt.fetchall()

    ibm_db.execute(expense)

    
  
       
    return render_template('display.html' ,expense = expense)
                          


@app.route('/delete/<string:id>', methods = ['POST', 'GET' ])
def delete(id):
     sql = "DELETE FROM expenses WHERE  id = {0}".format(id)
     stmt = ibm_db.prepare(conn, sql)
     ibm_db.execute(stmt)
     print('deleted successfully')    
     return redirect("/display")


@app.route('/edit/<id>', methods = ['POST', 'GET' ])
def edit(id):
    
    sql= "SELECT * FROM expenses WHERE  id = %s"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, (id,) )

    row = stmt.fetchall()
    ibm_db.execute(row)

   
    print(row[0])
    return render_template('edit.html', expenses = row[0])




@app.route('/update/<id>', methods = ['POST'])
def update(id):
  if request.method == 'POST' :
   
      date = request.form['date']
      expensename = request.form['expensename']
      amount = request.form['amount']
      paymode = request.form['paymode']
      category = request.form['category']
       
      sql = "UPDATE `expenses` SET `date` = % s , `expensename` = % s , `amount` = % s, `paymode` = % s, `category` = % s WHERE `expenses`.`id` = % s " 
      stmt = ibm_db.prepare(conn, sql)
      ibm_db.bind_param(stmt, 1, date)
      ibm_db.bind_param(stmt, 2, expensename)
      ibm_db.bind_param(stmt, 3, amount)
      ibm_db.bind_param(stmt, 4, str(paymode))
      ibm_db.bind_param(stmt, 5, str(category))
      ibm_db.bind_param(stmt, 6, id)
      ibm_db.execute(stmt)
      
      print('successfully updated')
      return redirect("/display")
     
      

            
 


@app.route("/today")
def today():
      
      sql = 'SELECT TIME(date)   , amount FROM expenses  WHERE userid = %s AND DATE(date) = DATE(NOW()) '
      stmt = ibm_db.prepare(conn, sql)
      ibm_db.bind_param(stmt, 1, str(session['id']))
      texpense = stmt.fetchall()
      ibm_db.execute(texpense)

      

      print(texpense)
      
      
      sql = 'SELECT * FROM expenses WHERE userid = % s AND DATE(date) = DATE(NOW()) AND date ORDER BY `expenses`.`date` DESC'
      stmt = ibm_db.prepare(conn, sql)
      ibm_db.bind_param(stmt, 1, str(session['id']))
      expense = stmt.fetchall()
      ibm_db.execute(expense)


      
      total = 0
      t_food=0
      t_entertainment=0
      t_business=0
      t_rent=0
      t_EMI=0
      t_other=0
      


      for x in expense:
          total += int(x[4])
          if x[6] == "food":
              t_food += int(x[4])            
          elif x[6] == "entertainment":
              t_entertainment  += int(x[4])
        
          elif x[6] == "business":
              t_business  += int(x[4])
          elif x[6] == "rent":
              t_rent  += int(x[4])
           
          elif x[6] == "EMI":
              t_EMI  += int(x[4])
         
          elif x[6] == "other":
              t_other  += int(x[4])
            
      print(total)  
      print(t_food)
      print(t_entertainment)
      print(t_business)
      print(t_rent)
      print(t_EMI)
      print(t_other)


     
      return render_template("today.html", texpense = texpense, expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )
     

@app.route("/month")
def month():
      
      sql = 'SELECT DATE(date), SUM(amount) FROM expenses WHERE userid= %s AND MONTH(DATE(date))= MONTH(now()) GROUP BY DATE(date) ORDER BY DATE(date) '
      stmt = ibm_db.prepare(conn, sql)
      ibm_db.bind_param(stmt, 1, str(session['id']))
      texpense = stmt.fetchall()
      ibm_db.execute(texpense)
      print(texpense)
      
      
      sql = 'SELECT * FROM expenses WHERE userid = % s AND MONTH(DATE(date))= MONTH(now()) AND date ORDER BY `expenses`.`date` DESC'
      stmt = ibm_db.prepare(conn, sql)
      ibm_db.bind_param(stmt, 1, str(session['id']))
      expense = stmt.fetchall()
      ibm_db.execute(expense)

      
  
      total=0
      t_food=0
      t_entertainment=0
      t_business=0
      t_rent=0
      t_EMI=0
      t_other=0
 
     
      for x in expense:
          total += int(x[4])
          if x[6] == "food":
              t_food += int(x[4])
            
          elif x[6] == "entertainment":
              t_entertainment  += int(x[4])
        
          elif x[6] == "business":
              t_business  += int(x[4])
          elif x[6] == "rent":
              t_rent  += int(x[4])
           
          elif x[6] == "EMI":
              t_EMI  += int(x[4])
         
          elif x[6] == "other":
              t_other  += int(x[4])
            
      print(total)
        
      print(t_food)
      print(t_entertainment)
      print(t_business)
      print(t_rent)
      print(t_EMI)
      print(t_other)


     
      return render_template("month.html", texpense = texpense, expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )
         
@app.route("/year")
def year():
      sql = 'SELECT MONTH(date), SUM(amount) FROM expenses WHERE userid= %s AND YEAR(DATE(date))= YEAR(now()) GROUP BY MONTH(date) ORDER BY MONTH(date) '
      stmt = ibm_db.prepare(conn, sql)
      ibm_db.bind_param(stmt, 1, str(session['id']))
      texpense = stmt.fetchall()
      ibm_db.execute(texpense)
      print(texpense)
      
      
      sql = 'SELECT * FROM expenses WHERE userid = % s AND YEAR(DATE(date))= YEAR(now()) AND date ORDER BY `expenses`.`date` DESC'
      stmt = ibm_db.prepare(conn, sql)
      ibm_db.bind_param(stmt, 1, str(session['id']))
      expense = stmt.fetchall()
      ibm_db.execute(expense)
  
      total=0
      t_food=0
      t_entertainment=0
      t_business=0
      t_rent=0
      t_EMI=0
      t_other=0
 
     
      for x in expense:
          total += int(x[4])
          if x[6] == "food":
              t_food += int(x[4])
            
          elif x[6] == "entertainment":
              t_entertainment  += int(x[4])
        
          elif x[6] == "business":
              t_business  += int(x[4])
          elif x[6] == "rent":
              t_rent  += int(x[4])
           
          elif x[6] == "EMI":
              t_EMI  += int(x[4])
         
          elif x[6] == "other":
              t_other  += int(x[4])
            
      print(total)
        
      print(t_food)
      print(t_entertainment)
      print(t_business)
      print(t_rent)
      print(t_EMI)
      print(t_other)


     
      return render_template("year.html", texpense = texpense, expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )

@app.route('/logout')

def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return render_template('home.html')



def send_email():
    from_email=email('211719104145@smartinternz.com')
    to_email=To('suriya.ms.2019.cse@ritchennai.edu.in')
    subject = 'LOGGED IN'
    content = Content("text/plain", "You have successfully signed in to the personal expense tracker application\nwith regards\n\t\t PETA-Team")
    mail = Mail(from_email, to_email, subject, content)
    
    try:
        sg = SendGridAPIClient(['SendGridApiKey'])
        response = sg.send(mail)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)
             

if __name__ == "__main__":
    app.run(debug=True)
