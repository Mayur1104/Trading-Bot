from kiteconnect import KiteConnect
import datetime
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

# KITECONNECT OBJECT
kc = KiteConnect( "klxymrz872j2nng8" , "tdZisdRn8dUKkLSwz13vw17n9JcrZ8uJ" )

def get_items():
    # IMPORTING INSTRUMENT TOKENS FROM JSON FILE
    with open("items.json", "r") as f:
        items = json.load(f)
        return [int(x) for x in items.keys()]

items = get_items()

def get_vars():
    # IMPORTING INSTRUMENT TOKENS FROM JSON FILE
    with open("items.json", "r") as f:
        vars = json.load(f)
    new_vars = {}
    for item in items:
        new_vars[item] = vars[str(item)]
    return new_vars
    

vars = get_vars()

def update_vars(item,new_vars):
    vars[item] = new_vars
    with open("items.json", "w") as f:
        json.dump(vars, f)

def log_to_file(text,token):
    with open("log.txt", "a") as log:
        log.write(str(token) + " : " +  text + " at " + str(datetime.datetime.now()) + "\n")

def get_items():
    # IMPORTING INSTRUMENT TOKENS FROM JSON FILE
    with open("items.json", "r") as f:
        items = json.load(f)
        return [int(x) for x in items.keys()]

items = get_items()

while True:
    for item in items:
        # RETRIEVING THE VARS FROM THE DATABASE
        mycursor.execute("SELECT * FROM items WHERE instrument_token = %s", (item,))
        myresult = mycursor.fetchall()
        if len(myresult) != 0:
             myresult = myresult[0]
             bap = myresult[1]
             baq = myresult[2]
             bbp = myresult[3]
             bbq = myresult[4]

        VARS = vars[item]

        if VARS["bid_trip"] == True and bbp < VARS["bid_threshold"] and VARS["last_order"] != "sell":
            VARS["bid_trip"] = False
            kc.place_order(
                variety = kc.VARIETY_REGULAR,
                exchange = kc.EXCHANGE_NSE,
                tradingsymbol = list(items.values())[0][0],
                transaction_type = kc.TRANSACTION_TYPE_SELL,
                quantity = VARS["SELL_QUANTITY"],
                product = kc.PRODUCT_MIS,
                order_type = kc.ORDER_TYPE_LIMIT,
                price = bbp
            )
            VARS["last_order"] = "sell"
            print("SELL TRIGGERED")
            log_to_file("Sell order placed for " + str(bbp) + "with a stoploss of " + str(bbp * (1-VARS["PERCENTAGE_MARGIN_FOR_SELL"])),item)
            VARS["bid_threshold"] = None
            update_vars(item,VARS)

        if VARS["bid_trip"] == False and bbq > VARS["X"]:
            VARS["bid_trip"] = True
            VARS["ask_trip"] = False
            VARS["bid_threshold"] = bbp
            log_to_file("Bid registered with threshold set to  " + str(bbp) + " when the quantity was " + str(bbq),item)
            print("BID REGISTERED")
            update_vars(item,VARS)

        if VARS["ask_trip"] == True and bap > VARS["ask_threshold"] and VARS["last_order"] != "buy":
            VARS["ask_trip"] = False
            kc.place_order(
                variety = kc.VARIETY_REGULAR,
                exchange = kc.EXCHANGE_NSE,
                tradingsymbol = list(items.values())[0][0],
                transaction_type = kc.TRANSACTION_TYPE_BUY,
                quantity = VARS["BUY_QUANTITY"],
                product = kc.PRODUCT_MIS,
                order_type = kc.ORDER_TYPE_LIMIT,
                price = bap
            )
            VARS["last_order"] = "buy"              
            print("BUY TRIGGERED")
            log_to_file("Buy order placed for " + str(bap) + "with a squareoff of " + str(bap * (1+VARS["PERCENTAGE_MARGIN_FOR_BUY"])),item)
            VARS["ask_threshold"] = None
            update_vars(item,VARS)

        if VARS["ask_trip"] == False and baq > VARS["X"]:
            VARS["ask_trip"] = True
            VARS["bid_trip"] = False
            VARS["ask_threshold"] = bap
            log_to_file("Ask registered with threshold set to  " + str(bap) + " when the quantity was " + str(baq),item)
            print("ASK REGISTERED")
            update_vars(item,VARS)