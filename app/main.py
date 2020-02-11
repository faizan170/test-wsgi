from flask import Flask, jsonify,render_template, request, session, send_from_directory, Response
import threading
import sqlite3
import numpy as np
import cv2
from sqlite3 import Error
import pandas as pd
import datetime
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
import json, os, random, string
import csv

from image_process import getAvgColor

'''
        ..............................................................
        Connection to DB
        ..............................................................

'''


database = "products.db"
try:
    conn = sqlite3.connect(database, check_same_thread=False)
except Error as e:
    print(e)

cur = conn.cursor()
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")


'''
        ..............................................................
        Create tables if not exists
        ..............................................................

'''
cur.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, user_name VARCHAR(50), user_email VARHCAR(100), user_password VARHCAR(50), user_join_date text, user_approved INTEGER)")
cur.execute("CREATE TABLE IF NOT EXISTS products (product_id INTEGER PRIMARY KEY, user_id INTEGER, product_name VARCHAR(500), product_date text)")
cur.execute("CREATE TABLE IF NOT EXISTS product_foundations (foundation_id INTEGER PRIMARY KEY, product_id INTEGER, foundation_name text, foundation_type text, foundation_url text, foundation_image text, foundation_date text, foundation_desc text, foundation_product text)")

app = Flask(__name__)

cors = CORS(app)


lock = threading.Lock()


    

def addProduct(productName, uid):
    ''' 
        Add new product
        arguments:
            productName => String
            uid => Int
    '''
    cur.execute("INSERT INTO products (user_id, product_name, product_date) VALUES (?,?,?)", 
        (uid, productName, datetime.datetime.now()))
    conn.commit()
    return cur.lastrowid



def getAllProducts(uid):
    ''' 
        Get a list of products
        arguments:
            uid => Int
    '''
    curr = conn.cursor()
    products = []
    print("Active", session.get('logged_in'))
    data = curr.execute("SELECT * FROM products WHERE user_id = ?", (getUserIdFromEmail(uid),))
    for row in data:
        products.append(
            {
                "productId":row[0],
                "productName":row[2]
            }
        )
    return products

def getProductTitle(productId):
    try:
        lock.acquire(True)
        curRow = cur.execute("SELECT * FROM products WHERE product_id = ?", (productId,))
        for row in curRow:
            return row[2]
    finally:
        lock.release()
    
 
def addProductFoundation(productId, foundationName, foundationType, foundationUrl, foundationImage, foundationDetails, fPName):
    cur.execute("INSERT INTO product_foundations (foundation_name, foundation_type, foundation_url, foundation_image, product_id, foundation_date, foundation_desc, foundation_product) VALUES (?,?,?,?,?,?,?,?)",
    (foundationName, foundationType, foundationUrl, foundationImage, productId, datetime.datetime.now(), foundationDetails, fPName))
    conn.commit()
    return cur.lastrowid



def getProductFoundationslist(pid):
    productFoundations = {}
    productFoundations["product_title"] = getProductTitle(pid)
    '''
    if os.path.exists("static/csv/" + productFoundations["product_title"] + ".csv"):
        productFoundations["train_file"] = "http://localhost:5000/getfile/" + productFoundations["product_title"] + ".csv"
    else:
        productFoundations["train_file"] = "NOT_EXISTS"
    '''
    productFoundations["product_foundations"] = []
    data = cur.execute("SELECT * FROM product_foundations WHERE product_id = " + str(pid))
    for row in data:
        productFoundations["product_foundations"].append(
            {
                "foundationId":row[0],
                "foundationName":row[2]
            }
        )
    return productFoundations

def getFoundationDetails(foundation_id):
    details = {}
    data = cur.execute("SELECT * FROM product_foundations WHERE foundation_id = ?", (foundation_id,))
    for row in data:
        date = datetime.datetime.strptime(row[6], "%Y-%m-%d %H:%M:%S.%f")
        date = str(date.year) + "-" + str(date.month) + "-" + str(date.day)
        details["foundation_name"] = row[2]
        details["foundation_type"] = row[3]
        details["foundation_url"] = row[4]
        details["foundation_image"] = row[5]
        details["foundation_date"] = date
        details["foundation_desc"] = row[7]
        details["foundation_product"] = row[8]
    return details

def updateFoundation(f_id, f_name, f_type, f_url, f_file, f_desc):
    if f_file == "":
        cur.execute("UPDATE product_foundations SET foundation_name = ?, foundation_type = ?, foundation_url = ?, foundation_desc = ? WHERE foundation_id = ?",
        (f_name, f_type, f_url, f_desc, f_id))
    conn.commit()

def deleteProductFoundation(fid):
    print(fid)
    cur.execute("DELETE FROM product_foundations WHERE foundation_id = " + str(fid))
    conn.commit()

def deleteProduct(productId):
    print("Product:", productId)
    foundations = getProductFoundationslist(productId)
    print("Total Length", len(foundations))
    print("Product Foundations:", foundations)
    for row in foundations['product_foundations']:
        print(row)
        deleteProductFoundation(row["foundationId"])
    cur.execute("DELETE FROM products WHERE product_id = " + str(productId))
    conn.commit()




def countProducts(uid, pType = '"%d-%m-%Y"'):
    data = []
    curRow = cur.execute('select COUNT(product_id) as pid, strftime(' + pType + ', product_date) as month_year from products where user_id = ' + str(getUserIdFromEmail(uid)) +' group by strftime(' + pType + ', product_date)')
    for row in curRow:
        data.append(row)
    return data




def getChartData(uid):
    dataChartRes = countProducts(uid)
    print(dataChartRes)
    template = {
        "labels": [a[1] for a in dataChartRes],
        "datasets": [
          {
            "label": "Products",
            "fill": True,
            "lineTension": 0.3,
            "backgroundColor": "rgba(225, 204,230, .3)",
            "borderColor": "rgb(205, 130, 158)",
            "borderCapStyle": "butt",
            "borderDash": [],
            "borderDashOffset": 0.0,
            "borderJoinStyle": "miter",
            "pointBorderColor": "rgb(205, 130,1 58)",
            "pointBackgroundColor": "rgb(255, 255, 255)",
            "pointBorderWidth": 10,
            "pointHoverRadius": 5,
            "pointHoverBackgroundColor": "rgb(0, 0, 0)",
            "pointHoverBorderColor": "rgba(220, 220, 220,1)",
            "pointHoverBorderWidth": 2,
            "pointRadius": 1,
            "pointHitRadius": 10,
            "data": [a[0] for a in dataChartRes]
          }
        ]
      }
    return template











def jsonfiyData(data):
    my_json = data.decode('utf8').replace("'", '"')
    data = json.loads(my_json)
    return data
#addProductShade(1, "FENTY BEAUTY - Pro Filt'r Mattee Longwear Foundation", "470 Cold", "http://google.com", "img.jpg")

def checkEmailExistance(email):
    curRow = cur.execute("SELECT COUNT(*) FROM users WHERE user_email = ?", (email,))
    for row in curRow:
        return row[0]

def registerUser(uname, uemail, upass):
    if checkEmailExistance(uemail) == 0:
        cur.execute("INSERT INTO users (user_name, user_email, user_password, user_join_date, user_approved) VALUES (?,?,?,?,?)",
        (uname, uemail, upass, datetime.datetime.now(), 0))
        conn.commit()
        return cur.lastrowid
    else:
        return "exists"

def checkUser(email, password):
    curRow = cur.execute("SELECT COUNT(*) FROM users WHERE user_email = ? AND user_password = ?", (email, password))
    for row in curRow:
        return row[0]

def getUsersList():
    data = []
    curRow = cur.execute("SELECT * FROM users WHERE user_id != 1")
    for row in curRow:
        date = row[4]
        date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
        date = str(date.year) + "-" + str(date.month) + "-" + str(date.day)
        data.append({
            "user_id": row[0],
            "user_name":row[1],
            "user_email":row[2],
            "user_date":date,
            "user_approved":row[5]
        })
    return data


def checkUserApproved(userId):
    curRow =  cur.execute("SELECT COUNT(*) FROM users WHERE user_id = ? and user_approved = ?", (userId, 1))
    for row in curRow:
        if row[0] == 1:
            return True
        else:
            return False

def updateUserApproved(uid, val):
    curr = conn.cursor()
    curr.execute("UPDATE users SET user_approved = ? WHERE user_id = ?", (val, uid))
    conn.commit()

def getUserName(userId):
    curr = conn.cursor()
    curRow = curr.execute("SELECT user_name FROM users WHERE user_id = ?", (userId,))
    for row in curRow:
        return row[0]

def getUserIdFromEmail(uemail):
    curr = conn.cursor()
    try:
        lock.acquire(True)
        curRow = curr.execute("SELECT user_id FROM users WHERE user_email = ?", (uemail,))
        for row in curRow:
            return row[0]
    finally:
        lock.release()
    


def processFoundations(project_id):
    data = []
    curRow = cur.execute("SELECT * FROM product_foundations WHERE product_id = ?", (project_id,))
    for row in curRow:
        data.append((row[0], "static/images/" + row[5]))
    from foundationBuilder import processData
    print("INFO: Total Data Length:", len(data))
    result = processData(data)
    return result

def finalizeFoundation(results):
    fResults = []
    for res in results:
        fDet = getFoundationDetails(res[0])
        fResults.append((fDet['foundation_name'], res[1], res[2],
         fDet['foundation_type'], fDet['foundation_url'], fDet["foundation_product"],
          fDet["foundation_image"], fDet["foundation_desc"]))
    
    return fResults

def finalizeFResults(project_id):
    res = processFoundations(project_id)
    print("INFO:Total Result Length", len(res))
    
    minVal = res[0][1]
    maxVal = res[len(res) - 1][1]
    if minVal < 70:
        minVal = 70
    if maxVal > 220:
        maxVal = 220
    if minVal - 100 > 10:
        minVal -= 10
    if 200 - maxVal > 10:
        maxVal += 15
    print("Min:", minVal, " - Max:", maxVal)
    print("Interval:", int((maxVal - minVal) / len(res)))
    data = []
    for i in range(minVal, maxVal, int((maxVal - minVal) / len(res))):
        data.append(i)
    maxValues = len(data) - len(res)
    if maxValues > 2:
        nums = [random.randint(0, len(res) + 1) for i in range(maxValues - 2)]
        for val in nums:
            del data[val]
    print("Length of data:", len(data))
    print("Data:", data)
    nData = []
    for i, val in enumerate(data):
        if i == 0:
            if val < 76: 
                val = 0
            else:
                val -= 10
            nData.append([res[i][0], val, data[i + 1]])
        elif i < len(data) - 3:
            nData.append([res[i][0], val, data[i + 1]])
        elif i == len(data) - 3:
            nData.append([res[i][0], val, maxVal])

        else:
            pass
    res = finalizeFoundation(nData)
    column_name = ['Foundation Name', 'Min Val', 'Max Val', 
    'Foundation Type', 'Foundation Url', 'Foundation Product', 'Foundation Image', 'Description']
    xml_df = pd.DataFrame(res, columns=column_name)
    xml_df.to_csv(("static/csv/" + getProductTitle(project_id) + ".csv"), index=None)
    return "done"


def findProducts(IMG_PATH):
    print("[info] Recognizing face in image")
    print("INFO: Img Path:", IMG_PATH)
    avg_color = getAvgColor(IMG_PATH)
    links = getFProductsLink(avg_color)
    return links


def getFProductsLink(valueS):
    values = []
    for f in os.listdir("static/csv"):
        fdata = {}
        fdata["product_name"] = f.split(".")[0]
        with open("static/csv/" + f, "r") as file:
            data = csv.reader(file, delimiter=",")
            i = 0
            for row in data:
                i += 1
                if i < 2:
                    continue
                if valueS >= int(row[1]) and valueS < int(row[2]):
                    fdata["foundation_details"] = [row[0], row[3], row[4],
                     "https://shadefinder.app/foundation-image/" + row[5],
                     "https://shadefinder.app/foundation-image/" + row[6], row[7]]
        values.append(fdata)
    return values


'''
        ......................................................................................
        
        
        
        Working with Routes start Here



        
        ......................................................................................

'''


# @app.route("/")
# def main():
#     return "app is Working"






@app.route("/mainpage-details/<string:uid>")
@cross_origin(origin='*')
def mainPageDetailsRoute(uid):
    data = {}
    data["products"] = getAllProducts(uid)
    data["chart"] = getChartData(uid)
    data["user_id"] = getUserIdFromEmail(uid)
    data["users"] = None
    if getUserIdFromEmail(uid) == 1:
        data["users"] = getUsersList()
    return jsonify(data)




@app.route("/user-details/<string:uid>")
@cross_origin(origin='*')
def getUserDetails(uid):
    data = {}
    data["user_name"] = getUserName(getUserIdFromEmail(uid))
    data["user_id"] = getUserIdFromEmail(uid)
    return jsonify(data)



@app.route("/add-product", methods=["POST"])
@cross_origin(origin='*')
def addProducts():
    data = jsonfiyData(request.data)
    id  = addProduct(data["product_name"], getUserIdFromEmail(data['user_id']))
    return jsonify({"id":id})

@app.route("/get-products/<string:uid>")
@cross_origin(origin='*')
def getProducts(uid):
    products = getAllProducts(uid)
    return jsonify(products)

@app.route("/delete-product", methods=["POST"])
@cross_origin(origin='*')
def deleteProductForm():
    data = jsonfiyData(request.data)
    deleteProduct(data["product_id"])
    return "done"

@app.route("/get-product-foundations/<int:id>", methods=['GET'])
@cross_origin(origin='*')
def getProductFoundations(id):
    return jsonify(getProductFoundationslist(id))

@app.route("/delete-foundation", methods=["POST"])
@cross_origin(origin='*')
def deleteFoundationForm():
    data = jsonfiyData(request.data)
    deleteProductFoundation(data["foundation_id"])
    print("foundation deleted")
    return "done"


@app.route("/add-foundation", methods=["POST"])
@cross_origin(origin='*')
def addFoundationForm():
    file = request.files['foundationFile'] 
    filename = secure_filename(file.filename)
    file2 = request.files['foundationProduct']
    filename_product = secure_filename(file2.filename)
    dataDigit = list(string.ascii_lowercase)
    num = "".join([dataDigit[random.randint(0,25)] for a in range(10)])
    filename = str(random.randint(503, 103943)) + "-" + num + "-" + filename
    dPath = os.path.join("static/images", filename)
    file.save(dPath)
    filename_product = str(random.randint(503, 103943)) + "-" + num + "-f-" + filename_product
    file2.save(os.path.join("static/images", filename_product))
    id = addProductFoundation(request.form["productId"],
    request.form["foundationName"], request.form["foundationType"],
     request.form["foundationUrl"], filename, request.form["foundationDetails"], filename_product)
    return "ok"

@app.route("/edit-foundation", methods=["POST"])
@cross_origin(origin='*')
def updateFoundationForm():
    updateFoundation(request.form["foundationId"], request.form["foundationName"], request.form["foundationType"],
    request.form["foundationUrl"], "", request.form["foundationDetails"])
    return "ok"


@app.route("/foundation-details/<int:id>", methods=['GET'])
@cross_origin(origin='*')
def getFDetails(id):
    return jsonify(getFoundationDetails(id))



@app.route("/login", methods=["POST"])
@cross_origin(origin='*')
def loginUserForm():
    data = jsonfiyData(request.data)
    email = data["userEmail"]
    password = data["userPassword"]
    if checkUser(email, password):
        if checkUserApproved(getUserIdFromEmail(email)) == False:
            return jsonify({"success":False, "type":"unapproved"})
        
        session['logged_in'] = True
        session["login_cbot_user"] = email
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "type":"invalid"})

@app.route("/register", methods=["POST"])
@cross_origin(origin='*')
def registerUserForm():
    data = jsonfiyData(request.data)
    name = data["userName"]
    email = data["userEmail"]
    password = data["userPassword"]
    print(name, email, password)
    if registerUser(name, email, password) == "exists":
        return jsonify({"success": False, "text":"Email Exists"})
    else:
        return jsonify({"success": True})


@app.route("/users-list/<string:uid>")
@cross_origin(origin='*')
def getUsersListRequest(uid):
    print(uid)
    uid = getUserIdFromEmail(uid)
    print("User Id:", uid)
    if uid == 1:
        data = getUsersList()
        return jsonify(data)
    else:
        return jsonify({"status": "not-allowed"})



@app.route("/approve-user", methods=["POST"])
@cross_origin(origin='*')
def approveUser():
    data = jsonfiyData(request.data)
    uid = data["user_id"]
    pid = getUserIdFromEmail(data["p_id"])
    
    if pid == 1:
        updateUserApproved(uid, 1)
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})

@app.route("/disapprove-user", methods=["POST"])
@cross_origin(origin='*')
def disapproveUser():
    data = jsonfiyData(request.data)
    uid = data["user_id"]
    pid = getUserIdFromEmail(data["p_id"])
    if pid == 1:
        updateUserApproved(uid, 0)
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})

@app.route("/process-foundation", methods=["POST"])
def processFoundationRequest():
    data = jsonfiyData(request.data)
    idP = data["product_id"]
    res = finalizeFResults(idP)
    res = {"status":"success"}
    return jsonify(res)

@app.route("/foundation-image/<path:filename>")
def getFile(filename):
    return send_from_directory(directory="static/images", filename=filename)



@app.route("/foundations-products", methods=['POST'])
@cross_origin(origin='*')
def getFoundationsListForProducts():
    file = request.files['image'] 
    filename = secure_filename(file.filename)
    IMG_PATH = "./static/images_test/" + filename
    file.save(IMG_PATH)
    data = findProducts(IMG_PATH)
    return jsonify(data)

#server route working
@app.route('/')
def hello_world():
   return render_template('index.html')

   #server admin route working
@app.route('/admin')
def hello_world1():
   return render_template('admin.html')

if __name__ == "__main__":
    app.secret_key = "areyoumaddieiooandk"
    app.run(host='0.0.0.0',port='80', debug=True)
