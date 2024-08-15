from kiteconnect import KiteTicker,KiteConnect
from functools import reduce
import json
import mysql.connector as mc

# CREATING A MYSQL CURSOR TO THE DATABASE VARS
mydb = mc.connect(
    host = "localhost",
    user = "root",
    passwd = "imtheadmin",
    database = "vars"
)
mycursor = mydb.cursor()


# KITETICKER OBJECT WITH API_KEY AND ACCESS TOKEN
kws = KiteTicker( "klxymrz872j2nng8" , "tdZisdRn8dUKkLSwz13vw17n9JcrZ8uJ" )
kc = KiteConnect( "klxymrz872j2nng8" , "tdZisdRn8dUKkLSwz13vw17n9JcrZ8uJ" )

def get_items():
    # IMPORTING INSTRUMENT TOKENS FROM JSON FILE
    with open("items.json", "r") as f:
        items = json.load(f)
        return [int(x) for x in items.keys()]

items = get_items()

# CHECKING IF ALL ITEMS ARE IN THE DATABASE
def check_items():
    for tick in items:
        # CHECKING IF THE STOCK IS ALREADY IN THE DATABASE
        mycursor.execute("SELECT * FROM items WHERE instrument_token = %s", (tick,))
        myresult = mycursor.fetchall()
        if len(myresult) == 0:
            # INSERTING THE STOCK INTO THE DATABASE
            sql = "INSERT INTO items (instrument_token) VALUES (%s)"
            val = (tick,)
            mycursor.execute(sql, val)
    mydb.commit()

    

def max_price_bid( x , y ):
    if x["price"] > y["price"]:
        return x
    else:
        return y

def max_price_ask( x , y ):
    if x["price"] < y["price"]:
        return x
    else:
        return y

# FUNCTIONS CALLED BY THE EVENT LISTENER
def on_ticks( ws , ticks ):
    
    for tick in ticks:
        bestask = reduce(max_price_ask,tick["depth"]["sell"])
        bestbid = reduce(max_price_bid,tick["depth"]["buy"])
        bap = bestask["price"]
        bbp = bestbid["price"]
        baq = bestask["quantity"]
        bbq = bestbid["quantity"]
        avg_price = tick["average_price"]

        
        
        # UPDATING THE STOCK IN THE DATABASE
        sql = "UPDATE items SET best_ask_price = %s, best_ask_quantity = %s, best_bid_price = %s, best_bid_quantity = %s WHERE instrument_token = %s"
        val = (bap,baq,bbp,bbq,tick["instrument_token"])
        mycursor.execute(sql, val)
    mydb.commit()

        # # SQL QUERY TO CREATE A TABLE FOR THESE VALUES
        # sql = "CREATE TABLE IF NOT EXISTS items (instrument_token INT PRIMARY KEY, best_ask_price FLOAT, best_ask_quantity INT, best_bid_price FLOAT, best_bid_quantity INT)"

        

def on_connect( ws , response ):
    # global last_trade
    check_items()
    print("succesfully connected")
    ws.subscribe(items)
    ws.set_mode(ws.MODE_FULL,items)

kws.on_connect = on_connect
kws.on_ticks = on_ticks

kws.connect()