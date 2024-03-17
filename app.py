from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

# Initializing the MySQL database
mydb = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    password = 'Root.signify@22',
    database = 'foodService'
)
mycursor = mydb.cursor(buffered=True)

admin_dict = {"santosh.admin@cfsp.com" : "admin"} # Dict to store admin credentials

# The method returns userId from the Database
def getId(email):
    qstr = "select userId from user where email = '%s'" %email
    mycursor.execute(qstr)
    id = mycursor.fetchall()
    return id


# The method returns the name of the user along with "user_userId" table data
def queryexecuter(email):
    id = getId(email)
    qstr = 'select * from user_%s' %id[0][0]
    mycursor.execute(qstr)
    data = mycursor.fetchall()
    qstr2 = "select name from user where email = '%s'" %email
    mycursor.execute(qstr2)
    name = mycursor.fetchall()
    return name,data


# Redirect to login page
@app.route('/')
def welcome():
    return render_template('login.html')

# validates the user credential
@app.route('/home', methods=['POST', 'GET'])
def home():
    uname = request.form['username']
    pwd = request.form['password']
    query = "select email from user"
    mycursor.execute(query)
    users = mycursor.fetchall()
    if uname in admin_dict.keys():
        if pwd in admin_dict[uname]:
            mycursor.execute("select userId, name, email from user")
            data = mycursor.fetchall()
            return render_template('admin.html', sqldata = data)
    for i in users:
        if uname in i:
            mycursor.execute("select password from user")
            passd = mycursor.fetchall()
            print(passd)
            for j in passd:
                if pwd in j:
                    print(pwd)
                    name, data = queryexecuter(uname)
                    return render_template('index.html', user = name[0][0], sqldata = data)
                else:
                    continue
            return render_template('login.html', msg = 'Invalid Credentials')  
    else:
        return render_template('login.html', msg = 'Invalid Credentials')
        
    
# Loads the add.html for the input of food data
@app.route('/add')
def add():
    return render_template('add.html')
    
# Uses the post method to push food data into the respective user database and then reload the index page with the user details
@app.route('/addfood', methods=['GET', 'POST'])
def addfood():
    if request.method == 'POST':
        name = request.form.get('name')
        type = request.form.get('type')
        quantity = request.form.get('quantity')
        email = request.form.get('email')

        id = getId(email)
        query = 'Insert into user_%s values(%s, %s, %s)'
        data = (id[0][0], name, type, quantity)
        mycursor.execute(query,data)
        mydb.commit()

        name, data = queryexecuter(email)
        return render_template('index.html', user = name[0][0], sqldata = data)
    return render_template('add.html')

# Loads delete.html page to  take input for deletion 
@app.route('/delete')
def delete():
    return render_template('delete.html')

# Uses post method to delete the data from the respective user database and displays index page with remaining data
@app.route('/deletefood', methods=['GET', 'POST'])
def deletefood():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')

        id = getId(email)
        query2 = "DELETE FROM user_%s WHERE food_name = '%s'  " %(id[0][0], name)
        mycursor.execute(query2)
        mydb.commit()

        name, data = queryexecuter(email)
        return render_template('index.html', user = name[0][0], sqldata = data)
    return render_template('delete.html')

# Displays register page
@app.route('/register')
def register():
    return render_template( 'register.html')

# Uses post method to store the registered user value
@app.route('/res_store', methods=["GET", "POST"])
def  res_store():
    if request.method == "POST":
        mycursor.execute("select count from user_count where id = 1")
        count = mycursor.fetchall()
        name = request.form.get('username')
        email = request.form.get('email')
        passd = request.form.get('passwd')

        temp = int(count[0][0])
        query = "insert into user values(%s, %s, %s, %s)"
        data = (temp, name, email, passd)
        mycursor.execute(query,data)

        mycursor.execute("update user_count set count = count+1 where id = 1")

        str = "create table user_%s(food_name varchar(20), food_type varchar(10), quantity int)" %temp
        mycursor.execute(str)
        mydb.commit()

        return render_template( 'login.html') 
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)