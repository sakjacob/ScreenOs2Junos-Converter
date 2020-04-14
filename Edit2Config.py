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
from tkinter import filedialog, simpledialog
import tkinter as tk

class Policy:
    def __init__(self):
        self.mID = ""
        self.mFromZone = ""
        self.mToZone = ""
        self.mSrcAdress = []
        self.mDestAdress = []
        self.mApplication = []
        self.mAction = set()
        self.mDisabled = False

    def __eq__(pol2):
        if self.mID == pol2.mID:
            return True

class GroupPolicy:
    def __init__(self):
        self.template = ""
        self.group = ""

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
       self.mID = 0 
       self.mAppName = ""
       self.mSourceRange = ""
       self.mDestRange = ""
       self.mProtocol = []


class ApplicationSet:
    def __init__(self):
       self.mAppName = ""
       self.mProtocol = []


def Convert(edit_Filename, save_directory, tkinter_object):
    addresses = []
    addressSets = dict()
    policies = dict()
    applications = []
    applicationSets =[]
    failedLines = 0
    #lSystem = input("Please type in the name of the logical system you would like to use: \n")
    lSystem = simpledialog.askstring("Logical System","Please type in the name of the logical system you would like to use: \n", parent = tkinter_object)

    try:
        file = open(edit_Filename, "r")
    except:
        raise AssertionError("Cannot open file")

    if lSystem == "" or edit_Filename == "": # make sure logical system gets a value, if not we don't want to create a bad config 
        raise AssertionError("No logical system name or filename input")



    PolicyID = 0 

    # set below used to convert predefined junos policies
    policy_fp = open(os.path.join(sys.path[0], "predefined-services.txt"), "r") 
    predetermined_policies = set()
    for policy in policy_fp:
        predetermined_policies.add(policy.replace('\n',""))

    group_fp = open(os.path.join(sys.path[0], "predefined-service_groups.txt"), "r") 
    predetermined_policie_groups = set()
    for group in group_fp:
        predetermined_policie_groups.add(group.replace('\n',""))

    fp_cut = open((save_directory + "\\cut.txt"),"a")
    fp_cut.write("\n------Start of lines that were cut because of failure to convert them------\n")

    for line in file:
        
        policy = False # these will determine what type of line we are on in the config
        application = False
        address = False
        addressSet = False
        applicationSet = False

        splitLine = shlex.split(line)
        sp_index = 0 # index of arg in splitline
        for arg in splitLine: # args do not have spaces in junos
            splitLine[sp_index] = arg.replace(" ","-")
            #splitLine[sp_index] = arg.replace("_","-")
            sp_index += 1

        if splitLine[1] == "address":
            address = True
        elif splitLine[1] == "group" and splitLine[2] == "address":
            addressSet = True
        elif splitLine[1] == "policy":
            policy = True
        elif splitLine[1] == "service":
            application = True
        elif splitLine[1] == "group" and splitLine[2] == "service":
            applicationSet = True

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
                for i in range(len(splitLine)-11): # sometimes multiple actions can be on one line
                    newPolicy.mAction.add(splitLine[11+i])
                #newPolicy.mAction.add(splitLine[11])
                policies[newPolicy.mID] = newPolicy
            elif len(splitLine) == 4: # update current policy ID
                if int(splitLine[3]) not in policies: #output error check
                    print("Error, new policy ID when it should already exist")
                PolicyID = int(splitLine[3])
            elif len(splitLine) == 5 and splitLine[4] == "disable": # disable policy
                policies[int(splitLine[3])].mDisabled = True
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
        elif application == True and len(splitLine) >= 8:
            application = Application()
            for app in applications: # make sure app names are differant (ie. appname != appname_1)
                if app.mAppName == splitLine[2]:
                    application.mID += 1
            application.mAppName = splitLine[2]
            application.mProtocol = splitLine[4]
            application.mSourceRange = splitLine[6]
            application.mDestRange = splitLine[8]
            applications.append(application)
        elif applicationSet == True:
            applicationSet = ApplicationSet()
            applicationSet.mAppName = splitLine[3]
            if len(splitLine) == 6:
                if splitLine[4] == "add":
                    applicationSet.mProtocol.append(splitLine[5])
                    applicationSets.append(applicationSet)
        else:
            print("\nFailure to convert line: ")
            print(line)
            fp_cut.write(line)
            failedLines += 1
    file.close()
    fp_cut.close()

    # create output files
    fp_manual_review = open(save_directory+"\\manual-review.txt","w")
    fp_config = open(save_directory+"\\junos.config","w")

    for addyLine in addresses: # write addresses first
        if addyLine.mDnsName: # dns name must be written between name and address
            output = "set logical-systems " + lSystem + " security address-book global address " + addyLine.mDomain + " dns-name " + addyLine.mAddress + "\n"
        else:
            output = "set logical-systems " + lSystem + " security address-book global address " + addyLine.mDomain + " " + addyLine.mAddress + "\n"
        fp_config.write(output)

    # next write address book lines
    for addygroup in addressSets: # iterate address groups 
        for addy in addressSets[addygroup]: # write each member of respective group
            output = "set logical-systems " + lSystem + " security address-book global address-set " + addygroup + " address " + addy + "\n"
            fp_config.write(output)

    review_policies = [] # a list of policies that require manual review. Later written to review file
    for ID in policies:
        # front portion of every line
        IterPolicy = policies[ID] 
        beginning = "set logical-systems " + lSystem + " security policies from-zone " + IterPolicy.mFromZone + " to-zone " + IterPolicy.mToZone + " policy " + str(IterPolicy.mID)
        for src in IterPolicy.mSrcAdress:
            output = beginning + " match source-address " + src + '\n'
            fp_config.write(output)
        for dst in IterPolicy.mDestAdress:
            output = beginning + " match destination-address " + dst + '\n'
            fp_config.write(output)
        for app in IterPolicy.mApplication:
            if app.lower() in predetermined_policies: # add "junos-" to front of app 
                output = beginning + " match application junos-" + app.lower() + '\n'
            elif app.lower() in predetermined_policie_groups: # write to manual review file
                new_group = GroupPolicy()
                new_group.template = beginning + " match application"
                new_group.group = app.lower()
                review_policies.append(new_group)
            elif app.lower() == "any": # get any to use consistent case
                output = beginning + " match application " + app.lower() + '\n'
            else:
                output = beginning + " match application " + app + '\n'
            fp_config.write(output)
        if IterPolicy.mDisabled:
            fp_config.write("deactivate security policies from-zone " + IterPolicy.mFromZone + " to-zone " + IterPolicy.mToZone + " policy " + str(IterPolicy.mID)+'\n')
        for action in IterPolicy.mAction:
            if action == "permit" or action == "deny" or action == "count":
                fp_config.write(beginning + " then " + action + '\n')
            elif action == "log":
                fp_config.write(beginning + " then log session-init" +'\n')

    review_instructions ="""
-----------------------------------------------------------------------------------------------
Below is a list of junos-predetermined-groups that need to be manually converted into policies.
* each group usually converts to multiple policies
* a template is provided with each group. Once the user determines the policies this group
contains, the user can copy and paste "template + policy" for each individual policy. 
-----------------------------------------------------------------------------------------------
"""
    fp_manual_review.write(review_instructions)    
    for group in review_policies: # junos-groups need to be manually converted
        fp_manual_review.write("\nTemplate: " + group.template +"\nGroup Name: "+group.group +"\n")

    for appLine in applications:
        if appLine.mID != 0: # if this is the first app name it shouldnt have an id at the end (ie. AppleRDP_0 is a no)
            output = "set logical-systems " + lSystem +" applications application " + appLine.mAppName + " term " + appLine.mAppName + "_" + str(appLine.mID) + " protocol " + appLine.mProtocol + " destination-port " + appLine.mDestRange + " source-port " + appLine.mSourceRange + "\n"
        else:
            output = "set logical-systems " + lSystem +" applications application " + appLine.mAppName + " term " + appLine.mAppName + " protocol " + appLine.mProtocol + " destination-port " + appLine.mDestRange + " source-port " + appLine.mSourceRange + "\n"
        fp_config.write(output)
    for appLine in applicationSets:
        output = "set applications application-set " + appLine.mAppName + " application " + appLine.mAppName + " application " + appLine.mProtocol[0] + "\n"
        fp_config.write(output)
    print("Number of failed lines: ",failedLines)

if __name__ == "__main__":
    input("Warning, you are not running the full conversion program, enter to proceed")
    edit_Filename = input("Please type the filename you would like to convert with the file extension (i.e. file.txt): \n")
    Convert(edit_Filename)