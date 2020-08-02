from flask import Flask, request, render_template, redirect, url_for, session
import os
import pypyodbc
import zipfile
import numpy as np
import cv2
from os.path import isfile, join

from RoleModel import RoleModel
from UserModel import UserModel
from Constants import connString


app = Flask(__name__)
app.secret_key = "MySecret"
ctx = app.app_context()
ctx.push()

with ctx:
    pass

userName = ""
roleObject = None
message = ""
msgType = ""

def initialize():
    global message, msgType
    message = ""
    msgType=""

def processRole(optionID):
    
    if optionID == 10 :
        if roleObject.canRole == False :
            return False
    if optionID == 20 :
        if roleObject.canUser == False :
            return False
    if optionID == 30 :
        if roleObject.CL111 == False :
            return False
    if optionID == 40 :
        if roleObject.CL222 == False :
            return False
    if optionID == 50 :
        if roleObject.CL333 == False :
            return False
    return True

@app.route('/')
def index():
    global userID, userName
    return render_template('Login.html')  # when the home page is called Index.hrml will be triggered.

@app.route('/processLogin', methods=['POST'])
def processLogin():
    global userID, userName, roleObject
    userName= request.form['userName']
    password= request.form['password']
    conn1 = pypyodbc.connect(connString, autocommit=True)
    cur1 = conn1.cursor()
    sqlcmd1 = "SELECT * FROM UserTable WHERE userName = '"+userName+"' AND password = '"+password+"' AND isActive = 1"; 
    
    cur1.execute(sqlcmd1)
    row = cur1.fetchone()
    
    cur1.commit()
    if not row:
        return render_template('Login.html', processResult="Invalid Credentials")
    userID = row[0]
    userName = row[3]
    
    cur2 = conn1.cursor()
    sqlcmd2 = "SELECT * FROM Role WHERE RoleID = '"+str(row[6])+"'"; 
    cur2.execute(sqlcmd2)
    row2 = cur2.fetchone()
   
    if not row2:
        return render_template('Login.html', processResult="Invalid Role")
    
    roleObject = RoleModel(row2[0], row2[1],row2[2],row2[3],row2[4],row2[5])

    return render_template('Dashboard.html')

@app.route("/ChangePassword")
def changePassword():
    global userID, userName
    return render_template('ChangePassword.html')

@app.route("/ProcessChangePassword", methods=['POST'])
def processChangePassword():
    global userID, userName
    oldPassword= request.form['oldPassword']
    newPassword= request.form['newPassword']
    confirmPassword= request.form['confirmPassword']
    conn1 = pypyodbc.connect(connString, autocommit=True)
    cur1 = conn1.cursor()
    sqlcmd1 = "SELECT * FROM UserTable WHERE userName = '"+userName+"' AND password = '"+oldPassword+"'"; 
    cur1.execute(sqlcmd1)
    row = cur1.fetchone()
    cur1.commit()
    if not row:
        return render_template('ChangePassword.html', msg="Invalid Old Password")
    
    if newPassword.strip() != confirmPassword.strip() :
       return render_template('ChangePassword.html', msg="New Password and Confirm Password are NOT same")
    
    conn2 = pypyodbc.connect(connString, autocommit=True)
    cur2 = conn2.cursor()
    sqlcmd2 = "UPDATE UserTable SET password = '"+newPassword+"' WHERE userName = '"+userName+"'"; 
    cur1.execute(sqlcmd2)
    cur2.commit()
    return render_template('ChangePassword.html', msg="Password Changed Successfully")


@app.route("/Dashboard")
def Dashboard():
    global userID, userName
    return render_template('Dashboard.html')


@app.route("/Information")
def Information():
    global message, msgType
    return render_template('Information.html', msgType=msgType, message = message)




@app.route("/UserListing")

def UserListing():
    global userID, userName
    
    global message, msgType, roleObject
    if roleObject == None:
        message = "Application Error Occurred"
        msgType="Error"
        return redirect(url_for('Information'))
    canRole = processRole(10)

    if canRole == False:
        message = "You Don't Have Permission to Access User"
        msgType="Error"
        return redirect(url_for('Information'))
    
    conn2 = pypyodbc.connect(connString, autocommit=True)
    cursor = conn2.cursor()
    sqlcmd1 = "SELECT * FROM UserTable ORDER BY userName"
    cursor.execute(sqlcmd1)
    records = []
    
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        
        conn3 = pypyodbc.connect(connString, autocommit=True)
        cursor3 = conn3.cursor()
        temp = str(dbrow[6])
        sqlcmd3 = "SELECT * FROM Role WHERE RoleID = '"+temp+"'"
        cursor3.execute(sqlcmd3)
        rolerow = cursor3.fetchone()
        roleModel = RoleModel(0)
        if rolerow:
           roleModel = RoleModel(rolerow[0],rolerow[1])
        else:
           print("Role Row is Not Available")
        
        row = UserModel(dbrow[0], dbrow[1], dbrow[2], dbrow[3], dbrow[4], dbrow[5], dbrow[6], roleModel=roleModel)
        records.append(row)
    return render_template('UserListing.html', records=records)


@app.route("/UserOperation")
def UserOperation():
    
    global userID, userName
    
    global message, msgType, roleObject
    if roleObject == None:
        message = "Application Error Occurred"
        msgType="Error"
        return redirect(url_for('Information'))
    canRole = processRole(10)

    if canRole == False:
        message = "You Don't Have Permission to Access User"
        msgType="Error"
        return redirect(url_for('Information'))
    
    operation = request.args.get('operation')
    unqid = ""
    
    
    
    rolesDDList = []
    
    conn4 = pypyodbc.connect(connString, autocommit=True)
    cursor4 = conn4.cursor()
    sqlcmd4 = "SELECT * FROM Role"
    cursor4.execute(sqlcmd4)
    print("sqlcmd4???????????????????????????????????????????????????????/", sqlcmd4)
    while True:
        roleDDrow = cursor4.fetchone()
        if not roleDDrow:
            break
        print("roleDDrow[1]>>>>>>>>>>>>>>>>>>>>>>>>>", roleDDrow[1])
        roleDDObj = RoleModel(roleDDrow[0], roleDDrow[1])
        rolesDDList.append(roleDDObj)
        
        
    row = UserModel(0)

    if operation != "Create" :
        unqid = request.args.get('unqid').strip()
        conn2 = pypyodbc.connect(connString, autocommit=True)
        cursor = conn2.cursor()
        sqlcmd1 = "SELECT * FROM UserTable WHERE UserID = '"+unqid+"'"
        cursor.execute(sqlcmd1)
        dbrow = cursor.fetchone()
        if dbrow:
            
            conn3 = pypyodbc.connect(connString, autocommit=True)
            cursor3 = conn3.cursor()
            temp = str(dbrow[6])
            sqlcmd3 = "SELECT * FROM Role WHERE RoleID = '"+temp+"'"
            cursor3.execute(sqlcmd3)
            rolerow = cursor3.fetchone()
            roleModel = RoleModel(0)
            if rolerow:
               roleModel = RoleModel(rolerow[0],rolerow[1])
            else:
               print("Role Row is Not Available")
            row = UserModel(dbrow[0], dbrow[1], dbrow[2], dbrow[3], dbrow[4], dbrow[5], dbrow[6], roleModel=roleModel)
        
    return render_template('UserOperation.html', row = row, operation=operation, rolesDDList=rolesDDList )




@app.route("/ProcessUserOperation",methods = ['POST'])
def processUserOperation():
    global userName, userID
    operation = request.form['operation']
    unqid = request.form['unqid'].strip()
    userName= request.form['userName']
    emailid= request.form['emailid']
    password=request.form['password']
    contactNo= request.form['contactNo']
    isActive = 0
    if request.form.get("isActive") != None :
        isActive = 1
    roleID= request.form['roleID']
    
    
    conn1 = pypyodbc.connect(connString, autocommit=True)
    cur1 = conn1.cursor()
    
    
    if operation == "Create" :
        sqlcmd = "INSERT INTO UserTable( userName,emailid, password,contactNo, isActive, roleID) VALUES('"+userName+"','"+emailid+"', '"+password+"' , '"+contactNo+"', '"+str(isActive)+"', '"+str(roleID)+"')"
    if operation == "Edit" :
        sqlcmd = "UPDATE UserTable SET userName = '"+userName+"', emailid = '"+emailid+"', password = '"+password+"',contactNo='"+contactNo+"',  isActive = '"+str(isActive)+"', roleID = '"+str(roleID)+"' WHERE UserID = '"+unqid+"'"  
    if operation == "Delete" :

        sqlcmd = "DELETE FROM UserTable WHERE UserID = '"+unqid+"'" 

    if sqlcmd == "" :
        return redirect(url_for('Information')) 
    cur1.execute(sqlcmd)
    cur1.commit()
    conn1.close()
    return redirect(url_for("UserListing"))







'''
    Role Operation Start
'''

@app.route("/RoleListing")
def RoleListing():
    
    global message, msgType
    print("roleObject>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", roleObject)
    if roleObject == None:
        message = "Application Error Occurred"
        msgType="Error"
        return redirect(url_for('Information'))
    canRole = processRole(20)

    if canRole == False:
        message = "You Don't Have Permission to Access Role"
        msgType="Error"
        return redirect(url_for('Information'))
    
    searchData = request.args.get('searchData')
    print(searchData)
    if searchData == None:
        searchData = "";
    conn2 = pypyodbc.connect(connString, autocommit=True)
    cursor = conn2.cursor()
    sqlcmd1 = "SELECT * FROM Role WHERE roleName LIKE '"+searchData+"%'"
    print(sqlcmd1)
    cursor.execute(sqlcmd1)
    records = []
    
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        
        row = RoleModel(dbrow[0],dbrow[1],dbrow[2],dbrow[3],dbrow[4],dbrow[5],dbrow[6])
        
        records.append(row)
    
    return render_template('RoleListing.html', records=records, searchData=searchData)

@app.route("/RoleOperation")
def RoleOperation():
    
    global message, msgType
    if roleObject == None:
        message = "Application Error Occurred"
        msgType="Error"
        return redirect(url_for('/'))
    canRole = processRole(120)

    if canRole == False:
        message = "You Don't Have Permission to Access Role"
        msgType="Error"
        return redirect(url_for('Information'))
    
    operation = request.args.get('operation')
    unqid = ""
    row = RoleModel(0, "",0,0,0,0)
    if operation != "Create" :
        unqid = request.args.get('unqid').strip()
        
        
        conn2 = pypyodbc.connect(connString, autocommit=True)
        cursor = conn2.cursor()
        sqlcmd1 = "SELECT * FROM Role WHERE RoleID = '"+unqid+"'"
        cursor.execute(sqlcmd1)
        while True:
            dbrow = cursor.fetchone()
            if not dbrow:
                break
            row = RoleModel(dbrow[0],dbrow[1],dbrow[2],dbrow[3],dbrow[4],dbrow[5],dbrow[6])
        
    return render_template('RoleOperation.html', row = row, operation=operation )


@app.route("/ProcessRoleOperation", methods=['POST'])
def ProcessRoleOperation():
    global message, msgType
    if roleObject == None:
        message = "Application Error Occurred"
        msgType="Error"
        return redirect(url_for('/'))
    canRole = processRole(120)

    if canRole == False:
        message = "You Don't Have Permission to Access Role"
        msgType="Error"
        return redirect(url_for('Information'))
    
    
    print("ProcessRole")
    
    operation = request.form['operation']
    if operation != "Delete" :
        roleName = request.form['roleName']
        canRole = 0
        canUser = 0
        CL111 = 0
        CL222 = 0
        CL333 = 0
        
        
        
        if request.form.get("canRole") != None :
            canRole = 1
        if request.form.get("canUser") != None :
            canUser = 1
        if request.form.get("CL111") != None :
            CL111 = 1
        if request.form.get("CL222") != None :
            CL222 = 1
        if request.form.get("CL333") != None :
            CL333 = 1
        
        
    
    print(1)
    unqid = request.form['unqid'].strip()
    print(operation)
    conn3 = pypyodbc.connect(connString, autocommit=True)
    cur3 = conn3.cursor()
    
    
    sqlcmd = ""
    if operation == "Create" :
        sqlcmd = "INSERT INTO Role (roleName, canRole, canUser, CL111, CL222, CL333) VALUES ('"+roleName+"', '"+str(canRole)+"', '"+str(canUser)+"', '"+str(CL111)+"', '"+str(CL222)+"', '"+str(CL333)+"')"
    if operation == "Edit" :
        print("edit inside")
        sqlcmd = "UPDATE Role SET roleName = '"+roleName+"', canRole = '"+str(canRole)+"', canUser = '"+str(canUser)+"', CL111 = '"+str(CL111)+"', CL222 = '"+str(CL222)+"', CL333 = '"+str(CL333)+"' WHERE RoleID = '"+unqid+"'" 
    if operation == "Delete" :
        conn4 = pypyodbc.connect(connString, autocommit=True)
        cur4 = conn4.cursor()
        sqlcmd4 = "SELECT roleID FROM UserTable WHERE roleID = '"+unqid+"'" 
        cur4.execute(sqlcmd4)
        dbrow4 = cur4.fetchone()
        if dbrow4:
            message = "You can't Delete this Role Since it Available in Users Table"
            msgType="Error"
            return redirect(url_for('Information')) 
        
        sqlcmd = "DELETE FROM Role WHERE RoleID = '"+unqid+"'" 
    print(operation, sqlcmd)
    if sqlcmd == "" :
        return redirect(url_for('Information')) 
    cur3.execute(sqlcmd)
    cur3.commit()
    
    return redirect(url_for('RoleListing')) 
    
'''
    Role Operation End
'''



import pandas as pd
import numpy as np
from sklearn import model_selection
from string import printable
from keras.preprocessing import sequence

import warnings
from CustomNetwork import CustomNetwork

warnings.filterwarnings("ignore")
_DATA= 'static/model/'

def run_model(model, X, url_int_tokens, target, max_len, epochs, batch_size, model_from_file, name):
    X_train, X_test, target_train, target_test = model_selection.train_test_split(X, target, test_size=0.25,
                                                                                  random_state=33)
    print("Running model " + name)
    if model_from_file is None:
        model.train_model(X_train, target_train, epochs=epochs, batch_size=batch_size)
        model.save_model(_DATA + name + ".json", _DATA + name + ".h5")
    else:
        model.load_model(_DATA + name + ".json", _DATA + name + ".h5")
    # loss, accuracy = mymodel.test_model(X_test, target_test)
    # print("loss " + str(loss))
    # print("accuracy " + str(accuracy))
    model.export_plot()


@app.route("/TrainTheModel")
def TrainTheModel():
    df = pd.read_csv('static/datasets/dataset.csv')
    url_int_tokens = [[printable.index(x) + 1 for x in url if x in printable] for url in df.url]
    max_len = 75
    X = sequence.pad_sequences(url_int_tokens, maxlen=max_len)
    target = np.array(df.isMalicious)
    epochs = 5
    batch_size = 32

    mymodel = CustomNetwork()

    run_model(mymodel, X, url_int_tokens, target, max_len, epochs, batch_size, None, "my_custom_model")

    return render_template('TrainTheModelResult.html')

@app.route("/PredictTheWebsite")
def PredictTheWebsite():
    return render_template('PredictTheWebsite.html')

@app.route("/ProcessPredictTheWebsite", methods=["POST"])
def ProcessPredictTheWebsite():
    myurl = request.form['myurl']
    name = "my_custom_model"
    mymodel = CustomNetwork()
    mymodel.load_model(_DATA + name + ".json", _DATA + name + ".h5")
    result = mymodel.predict(myurl)
    return render_template('PredictTheWebsiteResult.html', result=result, myurl=myurl)



if __name__ == "__main__":
    app.run()

