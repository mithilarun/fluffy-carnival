import ConfigParser
import MySQLdb
import os

dir_path=os.path.dirname(os.path.realpath(__file__))
fname=dir_path+"/data.txt"
if os.path.isfile(fname):
	os.remove(fname)
	f=open(fname,"w")
else:
	f=open(fname,"w") 
CONFIG_FILE="/home/ubuntu/code/BW_ctrl_ml/connection.conf"
config = ConfigParser.RawConfigParser()
def ConfigSectionMap(section):
	config.read(CONFIG_FILE)
	dict1 = {}
	try:
		options = config.options(section)
    		for option in options:
			try:
				dict1[option] = config.get(section, option)
			except:
				print("exception on {]".format(option))
				dict1[option] = None
	except:
		print("exception on {}".format(section))
    	return dict1	


instDict=dict()
db = MySQLdb.connect(host=ConfigSectionMap("Controller")['address'],
                     user=ConfigSectionMap("Controller")['username'],   
                     passwd=ConfigSectionMap("Controller")['password'],
                     db="nova",
		     port=3306)

#cursor object to execute command
cur = db.cursor()

cur.execute("SELECT * FROM instances")

for row in cur.fetchall():
	if row[6] in instDict:
		instDict[row[6]].append(row[17])
	else:
		instDict[row[6]]=[row[17]]

for it in instDict.items():
	f.write("%s:%s" %it)
f.write("\n")
#f.write(instDict)
#f.write("\n")

db = MySQLdb.connect(host=ConfigSectionMap("Controller")['address'],
                     user=ConfigSectionMap("Controller")['username'],
                     passwd=ConfigSectionMap("Controller")['password'],
                     db="neutron",
                     port=3306)

cur = db.cursor()

cur.execute("SELECT * FROM ports")

instPortDict=dict()
for row in cur.fetchall():
	if "compute:nova" in row[8]:
		if row[0] in instDict:
			if row[0] in instPortDict:
                		instPortDict[row[0]].append(row[1].split('-')[0])
        		else:
                		instPortDict[row[0]]=[row[1].split('-')[0]]
for it in instPortDict.items():
        f.write("%s:%s" %it)
f.write("\n")
#fwrite(instPortDict)
db.close()

