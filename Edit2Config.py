"""
This program creates a JunOS configuration from a 
pre-processed ScreenOS configuration.

To Do
* convert services for zones
* convert screen stuff for zones

Authors: Jake Sak and Sam Gendelmen
Last editted: 4-29-20
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
        self.mName = ""

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

class AddressSet:
    def __init__(self):
        self.mAddresses = []
        self.mAddressSets = []

class Application:
    def __init__(self):
       self.mID = 0 
       self.mAppName = ""
       self.mSourceRange = ""
       self.mDestRange = ""
       self.mProtocol = []
       self.mTimeout = ""


class ApplicationSet:
    def __init__(self):
       self.mAppName = ""
       self.mProtocol = []

class Zone:
    def __init__(self):
        self.mName = ""
        self.mServices = [] # enabled services like tcp-rst
        self.mScreen = [] # screen stuff like "ping-death" or "limit-session source-ip-based ___", etc
        self.mInterface = None

class Interface:
    def __init__(self):
        self.mName = ""
        self.mIpv6 = ""
        self.mUnit = -1
        self.mZone = None
        self.mPrimary = "" # primary ipv4 address 
        self.mSecondary = [] # secondary ipv4 addresses

"""
Converts a subnet in the form of xxx.xxx.xxx.xxx to cidr notation
"""

def ValidifyLeadingChar(s):
    while (len(s) > 0 and s[0] in ["-","_"]):
        s = s[1:]
    return s

def CIDR(subnet):
    quadrants = subnet.split(".") # get the cidr value from the subnet we are given
    cidr = 0
    for val in quadrants:
        v = int(val)
        v = f'{v:08b}' # convert the subnet int into binary to count for CIDR
        for bin in v:
            if bin == '1':
                cidr += 1
    return(str(cidr))


def Convert(edit_Filename, save_directory, tkinter_object):
    addresses = []
    addressSets = dict()
    policies = dict()
    applications = []
    applicationSets = []
    zones = dict()
    interfaces = dict() # same members as zones but organized with a different key
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

        splitLine = shlex.split(line.replace("#","-").replace("*","_"))
        sp_index = 0 # index of arg in splitline
        for arg in splitLine: # args do not have spaces in junos
            splitLine[sp_index] = arg.replace(" ","-")
            splitLine[sp_index] = ValidifyLeadingChar(arg)
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
                newPolicy.mName = splitLine[3]
                if splitLine[4] == "name" and len(splitLine) >= 13: #policy has name, indexing will be different
                    newPolicy.mName = splitLine[5].replace(" ","-")
                    newPolicy.mFromZone = splitLine[7]
                    newPolicy.mToZone = splitLine[9]
                    newPolicy.mSrcAdress.append(splitLine[10])
                    newPolicy.mDestAdress.append(splitLine[11])
                    newPolicy.mApplication.append(splitLine[12])
                    for i in range(len(splitLine)-13): # sometimes multiple actions can be on one line
                        newPolicy.mAction.add(splitLine[13+i])
                    policies[newPolicy.mID] = newPolicy
                else: # policy doesn't name, use id
                    newPolicy.mFromZone = splitLine[5]
                    newPolicy.mToZone = splitLine[7]
                    newPolicy.mSrcAdress.append(splitLine[8])
                    newPolicy.mDestAdress.append(splitLine[9])
                    newPolicy.mApplication.append(splitLine[10])
                    for i in range(len(splitLine)-11): # sometimes multiple actions can be on one line
                        newPolicy.mAction.add(splitLine[11+i])
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
                if len(splitLine) < 6: # dns address
                    address.mDnsName = True
                    #print("\nSuspected dns-name line. Line reads:")
                    #print(line)
                else:
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
                address.mDnsName = True
            addresses.append(address)
            #print(address.mDomain, address.mAddress)
        elif addressSet == True:
            if len(splitLine) < 5: # don't know what to do with this line
                print("\nFailure to convert line: ")
                print(line)
            # elif (len(splitLine) == 5 or (len(splitLine) == 7 and splitLine[5] == "comment")): # make a new address group
            #     addressSets[splitLine[4].replace(" ","-")] = AddressSet()
            # elif (len(splitLine) >= 7 and splitLine[5] == "add"): # add to an address set
            #     if splitLine[6].replace(" ","-") in addressSet: # add as addressSet
            #         addressSet[]
            master = splitLine[4].replace(" ","-") # name of address set being created or modified
            if master not in addressSets: # new address set
                addressSets[splitLine[4].replace(" ","-")] = AddressSet() # create new addressSet
            if (len(splitLine) >= 7 and splitLine[5] == "add"): # adding an address or address set
                addition = splitLine[6].replace(" ","-") # name of address or address set being added
                if addition in addressSets: # add as addressSet
                    addressSets[master].mAddressSets.append(addition)
                else: # adding a address
                    addressSets[master].mAddresses.append(addition)
                
                """
                if in addressSet
                    then address, add to currentAddressSet's address sets
                else:
                    is a address, add as an address
                """

            # elif (len(splitLine) == 5 or (len(splitLine) == 7 and splitLine[5] == "comment")): # make a new address group
            #     addressSets[splitLine[4].replace(" ","-")] = set()
            # elif (len(splitLine) >= 7 and splitLine[5] == "add"): # add to an address set
            #     if splitLine[4].replace(" ","-") in addressSets: # group already exists
            #         if splitLine[6].replace(" ","-") in addressSets: # combining two address sets
            #             addressSets[splitLine[4].replace(" ","-")] |= (addressSets[splitLine[6].replace(" ","-")])
            #         else: # add single address
            #             addressSets[splitLine[4].replace(" ","-")].add(splitLine[6].replace(" ","-")) # add single address
            #     else: # group was never created, create group and add to it 
            #         addressSets[splitLine[4].replace(" ","-")] = set()
            #         if splitLine[6].replace(" ","-") in addressSets: # combining two address sets
            #             addressSets[splitLine[4].replace(" ","-")].union(addressSets[splitLine[6].replace(" ","-")])
            #         else: # add single address
            #             addressSets[splitLine[4].replace(" ","-")].add(splitLine[6].replace(" ","-")) # add single address
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
            if len(splitLine) >= 10:
                application.mTimeout = str(int(splitLine[10]) * 60)
        elif applicationSet == True:
            applicationSet = ApplicationSet()
            applicationSet.mAppName = splitLine[3]
            if len(splitLine) == 6:
                if splitLine[4] == "add":
                    applicationSet.mProtocol.append(splitLine[5])
                    applicationSets.append(applicationSet)
        elif len(splitLine) >= 5 and splitLine[1] == "zone" and splitLine[2] == "id" and tkinter_object.zoneBool.get(): # new zone
            newZone = Zone()
            newZone.mName = splitLine[4]
            zones[newZone.mName] = newZone
            #print(newZone.mName)
        elif len(splitLine) >= 7 and splitLine[1] == "interface" and splitLine[3] == "tag" and splitLine[5] == "zone" and tkinter_object.zoneBool.get(): # new interface
            #print("Interface with e: ",splitLine[2]," and tag: ",splitLine[4])
            newInterface = Interface()
            newInterface.mName = splitLine[2]
            newInterface.mUnit = splitLine[4]
            if zones.get(splitLine[6]) == None:
                print("dictionary error on line: ",line)
                fp_cut.write(line)
                failedLines += 1
                continue
            else: # dictionary key error
                # pair zone and interface and add interface to interface dictionary
                newInterface.mZone = zones[splitLine[6]]
                newInterface.mZone.mInterface = newInterface
                interfaces[newInterface.mName] = newInterface
        elif len(splitLine) >= 5 and splitLine[1] == "interface" and splitLine[3] == "ip" and tkinter_object.zoneBool.get(): # ipv4 info for an interface
            if interfaces.get(splitLine[2]) == None:
                print("dictionary error on line: ",line)
                fp_cut.write(line)
                failedLines += 1
                continue
            else:
                if interfaces[splitLine[2]].mPrimary == "" and "secondary" not in splitLine: # set as primary address
                    if '.' in splitLine[4] and "/" in splitLine[4]: # ipv4 address in CIDR Form
                        interfaces[splitLine[2]].mPrimary = splitLine[4]
                    elif '.' in splitLine[4] and len(splitLine) >= 6: # ipv4 without CIDR
                        interfaces[splitLine[2]].mPrimary = splitLine[4] + '/' + CIDR(splitLine[5])
                else: # secondary address
                    if '.' in splitLine[4] and "/" in splitLine[4]: # ipv4 address in CIDR Form
                        interfaces[splitLine[2]].mSecondary.append(splitLine[4])
                    elif '.' in splitLine[4] and len(splitLine) >= 6: # ipv4 without CIDR
                        interfaces[splitLine[2]].mSecondary.append(splitLine[4] + '/' + CIDR(splitLine[5]))
                # can be other stuff, such as "manageable". Add support for this later
        else:
            # print("\nFailure to convert line: ")
            # print(line)
            fp_cut.write(line)
            failedLines += 1
    file.close()
    fp_cut.close()

    # delete temporary files
    os.remove(edit_Filename)

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
        parent = addressSets[addygroup] # write each member of respective group
            # write sets then individual addresses
            # output = "set logical-systems " + lSystem + " security address-book global address-set " + addygroup + " address " + addy + "\n"
        for s in parent.mAddressSets:
            fp_config.write("set logical-systems " + lSystem + " security address-book global address-set " + addygroup + " address-set " + s + "\n")
        for a in parent.mAddresses:
            fp_config.write("set logical-systems " + lSystem + " security address-book global address-set " + addygroup + " address " + a + "\n")

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
            if app.lower().replace(".","") in predetermined_policies: # add "junos-" to front of app 
                output = beginning + " match application junos-" + app.lower().replace(".","") + '\n'
            elif app.lower().replace(".","") in predetermined_policie_groups: # write to manual review file
                new_group = GroupPolicy()
                new_group.template = beginning + " match application"
                new_group.group = app.lower().replace(".","")
                review_policies.append(new_group)
            elif app.lower() == "any": # get any to use consistent case
                output = beginning + " match application " + app.lower() + '\n'
            elif app.lower() == "dns": # dns is split into udp and tcp line
                fp_config.write(beginning + " match application junos-dns-udp\n") # write the udp line
                output = beginning + " match application junos-dns-tcp\n" # set tcp to be be written later
            else:
                output = beginning + " match application " + app + '\n'
            fp_config.write(output)
        if IterPolicy.mDisabled:
            fp_config.write("deactivate logical-systems " + lSystem + " security policies from-zone " + IterPolicy.mFromZone + " to-zone " + IterPolicy.mToZone + " policy " + str(IterPolicy.mID) +'\n')
        for action in IterPolicy.mAction:
            if action == "permit" or action == "deny" or action == "count" or action == "reject":
                fp_config.write(beginning + " then " + action + '\n')
            # elif action == "log":
        fp_config.write(beginning + " then log session-init" +'\n')
    for appLine in applicationSets:
        output = "set logical-systems " + lSystem + " applications application-set " + appLine.mAppName + " application " + appLine.mProtocol[0] + "\n"
        fp_config.write(output)
    for zoneKey in zones:
        zoneIter = zones[zoneKey]
        if zoneIter.mInterface == None: # zone does not have interface. Can't write zone lines without interface tag
            print("Zone does not have interface, can't convert")
            fp_manual_review.write("Error converting zone "+ zoneIter.mName + "\n")
            continue
        beginning = "set logical-systems " + lSystem + " security zones security-zone " + zoneIter.mName
        fp_config.write(beginning + " host-inbound-traffic system-services ping\n")
        fp_config.write(beginning + " host-inbound-traffic system-services traceroute\n")
        fp_config.write(beginning + " interfaces reth0." +zoneIter.mInterface.mUnit + " host-inbound-traffic system-services ping\n")
        fp_config.write(beginning + " interfaces reth0." +zoneIter.mInterface.mUnit + " host-inbound-traffic system-services traceroute\n")
    for interfaceName in interfaces:
        iterInterface = interfaces[interfaceName]
        beginning = "set logical-systems " + lSystem + " interfaces reth0 unit " + iterInterface.mUnit
        interface_str = beginning + " vlan-id " + iterInterface.mUnit + "\n"
        fp_config.write(interface_str)

        if iterInterface.mPrimary != "": # ipv4 address known
            ipv4 = beginning + " family inet address " + iterInterface.mPrimary + " primary\n"
            fp_config.write(ipv4)
        for secondaryIP in iterInterface.mSecondary: # write secondary IPs
            fp_config.write(beginning + " family inet address " + secondaryIP + "\n")

        if iterInterface.mZone.mName != "": # interace connected with zone
            description = beginning + " description " + iterInterface.mZone.mName + "\n"
            fp_config.write(description)

        fp_config.write(beginning + " family inet6 dad-disable\n")

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
            output = "set logical-systems " + lSystem + " applications application " + appLine.mAppName + " term " + appLine.mAppName + "_" + str(appLine.mID) + " protocol " + appLine.mProtocol + " destination-port " + appLine.mDestRange + " source-port " + appLine.mSourceRange
        else:
            output = "set logical-systems " + lSystem + " applications application " + appLine.mAppName + " term " + appLine.mAppName + " protocol " + appLine.mProtocol + " destination-port " + appLine.mDestRange + " source-port " + appLine.mSourceRange
        if appLine.mTimeout != "": # if there is a time out associated with the application then add it in or finish the line
            output = output + " inactivity-timeout " + appLine.mTimeout + "\n"
        else:
            output = output + "\n"
        fp_config.write(output)

    print("Number of failed lines: ",failedLines)
    #print("convert zones?: ",tkinter_object.zoneBool.get())
if __name__ == "__main__":
    input("PLEASE RUN S2JCONVERSIONTOOL.PY\n Enter anything to end program")