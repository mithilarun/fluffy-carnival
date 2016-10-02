import paramiko
import ConfigParser
import os
from dataCollection import projectID

projectIDObj=projectID()
instDict=projectIDObj.projectIDMapToInstance()
instPortDict=projectIDObj.projectIDMapToPorts()
	
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

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(ConfigSectionMap("Controller")['address'], username=ConfigSectionMap("Controller")['username'],password=ConfigSectionMap("Controller")['password'])
stdin, stdout, stderr = ssh.exec_command(
    "sudo ovs-ofctl dump-ports-desc br-int")
outputList=stdout.read().split("\n")
tenantPorts=dict()

for x in outputList:
	for projectID,portID in instPortDict.iteritems():
		for individualPortID in portID:
			if individualPortID in x:
				if projectID in tenantPorts:
					tenantPorts[projectID].append(x.split("(")[0].split(" ")[1])
				else:
					tenantPorts[projectID]=[x.split("(")[0].split(" ")[1]]
stdin, stdout, stderr = ssh.exec_command(
    "sudo ovs-ofctl dump-ports br-int")
outputList=stdout.read().split("\n")

bandwidthDict=dict()
i=0
for x in outputList:
	for projectID,portNumber in tenantPorts.iteritems():
		for individualPortNumber in portNumber:
			if "tx pkts" in x:
				if individualPortNumber in outputList[i-1].split(":")[0]:
					if projectID in bandwidthDict:
						bandwidthDict[projectID].append(int(x.split(",")[0].split("=")[1]))
					else:
						bandwidthDict[projectID]=[int(x.split(",")[0].split("=")[1])]
	i=i+1

#print bandwidthDict

#print tenantPorts		
			 
#print outputList

