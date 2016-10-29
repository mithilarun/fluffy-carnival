import ConfigParser
from datetime import datetime
import MySQLdb
from portsInfo import portInfo

CONFIG_FILE = "/home/ubuntu/code/BW_ctrl_ml/connection.conf"
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
                print "exception on {}".format(option)
                dict1[option] = None
    except:
        print "exception on {}".format(section)
        return dict1

db = MySQLdb.connect(host=ConfigSectionMap("Controller")['address'],
                     user=ConfigSectionMap("Controller")['username'],
                     passwd=ConfigSectionMap("Controller")['password'],
                     port=3306)

cur = db.cursor()

cur.execute("create database if not exists bandwidth")

db = MySQLdb.connect(host=ConfigSectionMap("Controller")['address'],
                     user=ConfigSectionMap("Controller")['username'],
                     passwd=ConfigSectionMap("Controller")['password'],
                     db="bandwidth",
                     port=3306)

cur = db.cursor()

portInfoObj = portInfo()
portInfoObj.sshConnect()
tenantPorts = portInfoObj.instanceToPortNumber()
bandwidthDict = portInfoObj.instanceToBandwidth()

i = 0
for instance, bandwidthList in bandwidthDict.iteritems():
    cur.execute("SET sql_notes=0; ")
    cur.execute("create table if not exists {} \
				(currentdatetime VARCHAR(50),bandwidthusage INTEGER);"
                .format("tenant" + str(i)))
    cur.execute("SET sql_notes=1; ")
    cur.execute("INSERT INTO {} (currentdatetime,bandwidthusage) values ('{}',{});"
                .format("tenant" + str(i), datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
                        sum(bandwidthList)))
    db.commit()
    i = i + 1

db.close()
