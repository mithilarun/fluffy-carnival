import ConfigParser

config = ConfigParser.RawConfigParser()
def ConfigSectionMap(section):
	config.read("/home/ubuntu/Python-2.7.12/connection.conf")
	dict1 = {}
	try:
		options = config.options(section)
    		for option in options:
			try:
				dict1[option] = config.get(section, option)
				#if dict1[option] == -1:
				#    DebugPrint("skip: %s" % option)
			except:
				print("exception on {]".format(option))
				dict1[option] = None
	except:
		print("exception on {}".format(section))
    	return dict1	
#!/usr/bin/python
import MySQLdb

db = MySQLdb.connect(host=ConfigSectionMap("Controller")['address'],
                     user=ConfigSectionMap("Controller")['username'],   
                     passwd=ConfigSectionMap("Controller")['password'],
                     db="keystone",
		     port=3306)

#db = mysql.connector.connect( host='192.168.1.7',
#          	      user='ubuntu',   
#                      passwd='123456',
#                     db="keystone",
#                    port=3306)

# you must create a Cursor object. It will let
#  you execute all the queries you need
cur = db.cursor()

# Use all the SQL you like
cur.execute("SELECT * FROM user")

# print all the first cell of all the rows
for row in cur.fetchall():
    print row[0]

db.close()
#Name = ConfigSectionMap("Controller")['name']
#IP = ConfigSectionMap("Compute")['address']
#print Name
#print IP

