import mysql.connector
import datetime
import pymysql

db_host = "sql148.main-hosting.eu"
# db_host = "localhost"
db_user = "u236970030_myshop_admin"
db_password = "shop12345"
db_name = "u236970030_myshop_db"

# mydb = pymysql.connect(db_host, db_user, db_password, db_name)
# mycursor = mydb.cursor()

# # open mysql connection
mydb = mysql.connector.connect(
host=db_host,
user=db_user,
passwd=db_password,
database=db_name
)
mycursor = mydb.cursor()

# write into database
sql = "SELECT * FROM `products`;"
mycursor.execute(sql)
matched_products = mycursor.fetchall()
if len(matched_products)>0:
    print ("This product already exists")

sql = (
    "INSERT INTO `products` (`name`,`price`,`image_url`,`image_path`,`image_md5_hash`,`created_at`,`updated_at`)" \
    "VALUES" \
    "(%s,%s,%s,%s,%s,%s,%s);"
)

product_created = datetime.datetime.now()
product_updated = product_created
for i in range(10):
    val = ["aaa", "bbb", "ccc", "ddd", "eee", product_created, product_updated]
    mycursor.execute(sql, val)
    mydb.commit()