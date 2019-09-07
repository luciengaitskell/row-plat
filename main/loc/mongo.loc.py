from pymongo import MongoClient

db_name = input("Input database name: ")

cli = MongoClient('rowplatpi.local')
col = cli[db_name].log  # Select log collection contained within inputted database

# Print all entries:
for i in col.find():
    print(i)
