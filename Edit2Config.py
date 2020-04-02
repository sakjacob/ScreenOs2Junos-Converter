"""
This program creates a JunOS configuration from a 
pre-processes ScreenOS configuration.

Authors: Jake Sak and Sam Gendelmen
Last editted: 3-24-20
"""

import shlex
import fileinput
import os
import sys

addresses = []
addressSets = dict()
policies = dict()
applications = []



class Policy:
    def __init__(self):
        self.mID = ""
        self.mFromZone = ""
        self.mToZone = ""
        self.mSrcAdress = []
        self.mDestAdress = []
        self.mApplication = []
        self.mAction = ""
        self.mDisabled = False

    def __eq__(pol2):
        if self.mID == pol2.mID:
            return True

class Address:
    def __init__(self):
       self.mAddress = ""
       self.mDomain = ""
       self.mSecurityZone = ""
       self.mSubNet = ""
       self.mCIDR = 0
       self.mDnsName= False # "dns-name" must be inserted between name and address

    def __eq__(add2):
        if self.mAddress == add2.mAddress:
            return True      

class Application:
    def __init__(self):
       self.id = 0 
       self.mAppName = ""
       self.mSourceRange = ""
       self.mDestRange = ""
       self.mProtocol = []

def Convert(edit_Filename):
    failedLines = 0
    lSystem = input("Please type in the name of the logical system you would like to use: \n")

    if lSystem == "" or edit_Filename == "": # make sure logical system gets a value, if not we don't want to create a bad config 
        raise AssertionError("No logical system name or filename input")

    logicalSystemLine = ["set", "logical-systems", str(lSystem), "security"] # covers adresses and policies
    applicationsLine = ["set", "applications", "application"] # covers applications

    try:
        file = open(edit_Filename, "r")
    except:
        raise AssertionError("Cannot open file")

    PolicyID = 0 

    # set below used to convert predefined junos policies
    policy_fp = open(os.path.join(sys.path[0], "predefined-services.txt"), "r") 
    predetermined_policies = set()
    for policy in policy_fp:
        predetermined_policies.add(policy.replace('\n',""))

    for line in file:
        
        policy = False # these will determine what type of line we are on in the config
        application = False
        address = False
        addressSet = False

        splitLine = shlex.split(line)
        sp_index = 0 # index of arg in splitline
        for arg in splitLine: # args do not have spaces in junos
            splitLine[sp_index] = arg.replace(" ","-")
            sp_index += 1

        if splitLine[1] == "address":
            address = True
        elif splitLine[1] == "group" and splitLine[2] == "address":
            addressSet = True
        elif splitLine[1] == "policy":
            policy = True
        elif splitLine[1] == "service":
            application = True
            
        """
        Sam policy code
        """
        # if policy == True:
        #     pol = Policy()
        #     for option in range(len(splitLine)): # get the components of the line and store them in an object
        #         if splitLine[option] == "id":
        #             pol.mID = splitLine[option + 1]
        #         if splitLine[option] == "from":
        #             pol.mFromZone = splitLine[option + 1]
        #         if splitLine[option] == "to":
        #             pol.mToZone = splitLine[option + 1]
        #             if splitLine[option + 2] == "Any": # "any" is case sensitive, make corrections
        #                 pol.mSrcAdress.append("any")
        #             else:
        #                 pol.mSrcAdress.append(splitLine[option + 2].replace(" ","-")) # replaces spaces with dashes
        #             pol.mDestAdress.append(splitLine[option + 3])
        #             pol.mApplication = splitLine[option + 4]
        #             pol.mAction = splitLine[option + 5]
        #             break
        #     policies.append(pol)

        if policy:
            if len(splitLine) >= 12: # new policy line
                # create new policy object. Throw an error if already in dictionary
                newPolicy = Policy()
                newPolicy.mID = int(splitLine[3])
                newPolicy.mFromZone = splitLine[5]
                newPolicy.mToZone = splitLine[7]
                newPolicy.mSrcAdress.append(splitLine[8])
                newPolicy.mDestAdress.append(splitLine[9])
                newPolicy.mApplication.append(splitLine[10])
                newPolicy.mAction = splitLine[11]
                policies[newPolicy.mID] = newPolicy
            elif len(splitLine) == 4: # update current policy ID
                if int(splitLine[3]) not in policies: #output error check
                    print("Error, new policy ID when it should already exist")
                PolicyID = int(splitLine[3])
            elif len(splitLine) == 5 and splitLine[4] == "disable": # disable policy
                policies[PolicyID].mDisabled = True
            else:
                print("\nUn-accounted for edge case in policy on line:")
                print(line)
        elif len(splitLine) == 3 and splitLine[1] == "src-address": # add another source to current policy 
            policies[PolicyID].mSrcAdress.append(splitLine[2])
        elif len(splitLine) == 3 and splitLine[1] == "dst-address": # add another destination to current policy 
            policies[PolicyID].mDestAdress.append(splitLine[2])
        elif len(splitLine) == 3 and splitLine[1] == "service": # add another service/application to current policy
            policies[PolicyID].mApplication.append(splitLine[2])
        elif address == True:
            address = Address()
            address.mSecurityZone = str(splitLine[2])
            address.mDomain = splitLine[3].replace(" ","-").replace("(","-").replace(")","")
            address.mAddress = splitLine[4]
            if "::" not in splitLine[4]: # IPV4 address
                if len(splitLine) < 6:
                    address.mDnsName = True
                    print("\nSuspected dns-name line. Line reads:")
                    print(line)
                    continue
                address.mSubNet = str(splitLine[5])
                subNet = address.mSubNet.split(".") # get the cidr value from the subnet we are given
                subnet = 0
                for val in subNet:
                    v = int(val)
                    v = f'{v:08b}' # convert the subnet int into binary to count for CIDR
                    for bin in v:
                        if bin == '1':
                            subnet += 1
                address.mCIDR = str(subnet)
                address.mAddress = str(splitLine[4]) +"/"+ address.mCIDR
            else: # IPV6 address
                address.mDnsName= True
            addresses.append(address)
            #print(address.mDomain, address.mAddress)
        elif addressSet == True:
            if len(splitLine) < 5: # don't know what to do with this line
                print("\nFailure to convert line: ")
                print(line)
            elif (len(splitLine) == 5 or (len(splitLine) == 7 and splitLine[5] == "comment")): # make a new address group
                addressSets[splitLine[4].replace(" ","-")] = []
            elif (len(splitLine) >= 7 and splitLine[5] == "add"): # add to an address set
                if splitLine[4].replace(" ","-") in addressSets:
                    addressSets[splitLine[4].replace(" ","-")].append(splitLine[6].replace(" ","-"))
                else: # group was never created, create group and add to it 
                    addressSets[splitLine[4].replace(" ","-")] = [splitLine[6].replace(" ","-")]
            else:
                print("\nFailure to convert line: ")
                print(line)
        elif application == True and len(splitLine) > 3:
            application = Application()
            for app in applications: # make sure app names are differant (ie. appname != appname_1)
                if app.mAppName == splitLine[2]:
                    app.mID += 1
            application.mAppName = splitLine[2]
            application.mProtocol = splitLine[4]
            application.mSourceRange = splitLine[6]
            application.mDestRange = splitLine[8]
            applications.append(application)
        else:
            print("\nFailure to convert line: ")
            print(line)
            failedLines += 1
    file.close()

    new_name = "" # This will write the name of the file in srx.config style
    dst_str = ""
    for i in range(len(edit_Filename)):
        if edit_Filename[i] == "-":
            dst_str = edit_Filename[0:i] + "-srx_tool.config"
    fp_dst = open(dst_str,"w")

    for addyLine in addresses: # write addresses first
        if addyLine.mDnsName: # dns name must be written between name and address
            output = "set logical-systems " + lSystem + " security address-book global address " + addyLine.mDomain + " dns-name " + addyLine.mAddress + "\n"
        else:
            output = "set logical-systems " + lSystem + " security address-book global address " + addyLine.mDomain + " " + addyLine.mAddress + "\n"
        fp_dst.write(output)

    # next write address book lines
    for addygroup in addressSets: # iterate address groups 
        for addy in addressSets[addygroup]: # write each member of respective group
            output = "set logical-systems " + lSystem + " security address-book global address-set " + addygroup + " address " + addy + "\n"
            fp_dst.write(output)

    for ID in policies:
        # front portion of every line
        IterPolicy = policies[ID] 
        beginning = "set logical-systems " + lSystem + " security policies from-zone " + IterPolicy.mFromZone + " to-zone " + IterPolicy.mToZone + " policy " + str(IterPolicy.mID)
        for src in IterPolicy.mSrcAdress:
            output = beginning + " match source-address " + src + '\n'
            fp_dst.write(output)
        for dst in IterPolicy.mDestAdress:
            output = beginning + " match destination-address " + dst + '\n'
            fp_dst.write(output)
        for app in IterPolicy.mApplication:
            if app.lower() in predetermined_policies: # add "junos-" to front of app 
                output = beginning + " match application junos-" + app.lower() + '\n'
            elif app.lower() == "any": # get any to use consistent case
                output = beginning + " match application " + app.lower() + '\n'
            else:
                output = beginning + " match application " + app + '\n'
            fp_dst.write(output)
        fp_dst.write(beginning + " then " + IterPolicy.mAction + '\n')

    # for appLine in applications:
    #     if appLine.mID != 0: # if this is the first app name it shouldnt have an id at the end (ie. AppleRDP_0 is a no)
    #         output = "set applications application " + appLine.mAppName + " term " + appLine.mAppName + "_" + appLine.mID + " protocol " + appLine.mProtocol + " destination-port " + appLine.mDestRange + " source-port " + appLine.mSourceRange
    #     else:
    #         output = "set applications application " + appLine.mAppName + " term " + appLine.mAppName + " protocol " + appLine.mProtocol + " destination-port " + appLine.mDestRange + " source-port " + appLine.mSourceRange
    #     fp_dst.write(output)
    print("Number of failed lines: ",failedLines)

if __name__ == "__main__":
    edit_Filename = input("Please type the filename you would like to convert with the file extension (i.e. file.txt): \n")
    Convert(edit_Filename)