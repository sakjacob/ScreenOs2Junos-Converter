"""
This program compares Ip addresses to their 
subnet masks and prompts the user to edit
invalid pairs.

Author: Jake Sak
Last Editted: 4-6-20
"""

import math
from tkinter import filedialog, simpledialog # for gui
import tkinter as tk # for gui

def findNth(search, ele, n):
    """
    returns the index of the nth occurence of ele in search
    
    :param search: string to be searched
    :param ele: substring we are searching for
    :param n: the nth occurence of ele we want index for
    :returns: the index of nth occurence or -1 if error
    """
    if (n <= 0):
        return -1 # Occurence must be greater or equal to 1

    searchString = search
    IterIndex = 0 # index relevant to substring
    RealIndex = 0 # index relevant to orginal string
    for i in range(n):
        IterIndex = searchString.find(ele)
        if IterIndex == -1:
            return -1
        searchString = searchString[IterIndex+1:]
        RealIndex += IterIndex
        if i > 0:
            RealIndex += 1
    return RealIndex

def subnetValidifier(subnet):
    """
    checks that ones are left as possible in octete
    """
    filteredSubnet = subnet & 255
    if (filteredSubnet == subnet):
        return True
    else:
        return False

def OcteteComparer(ipO, subO, line):
    """
    compares an octete from an IP address and subnet and
    determines if the pair is valid

    Assumes ones in octetes are left most as possible

    :param ipO: int
    :param subO: int
    :param line: a list containing a single string which is the line being read
    :return: bool representing if valid octete pairing 
    """
    if (subnetValidifier(ipO) and subnetValidifier(subO)): # check octetes are valid
        temp = 254 - subO
        zeros = (round(math.log(temp,2)))
        subnetbits = 8 - zeros
        #print(subnetbits)
        subnetRange = 256//(2**subnetbits)
        if (not ipO%subnetRange):
            return True
        else: 
            return False

    else:
        print("ones are not leftmost in Octete Comparer")
        return False

def ValidIPSubNetPair(ipAddress, subnetMask, line, tkinter_object):
    """
    Given a full IPV4 Address and a subnet, this function compares the two
    and makes sure they are a valid pairing.

    The user is prompted for input when correcting some errors

    :param ipAddress: string
    :param subnetMask: string
    :param line: a list containing a single string which is the line being read
    :param tkinter_object: used to gather input through a gui
    :return: bool representing if the pairing is valid. False prevents line from being written in main
    """
    try:
        IpOctetes = ipAddress.split('.')
        SubnetOctetes = subnetMask.split('.')
        if (len(IpOctetes) != 4 or len(SubnetOctetes) != 4):
            print("invalid arg provided to IP verifier")
            return False
        else:
            for index in range(len(SubnetOctetes)-1,-1,-1):
                if (int(SubnetOctetes[index]) == 0 and int(IpOctetes[index]) != 0):
                    print("Error: Octete",index+1,"in IP should be 0, not",IpOctetes[index])
                    # use index to find correct period for index for changing octete to zero
                    newIP = ""
                    if index == 3: # octete 4
                        newIP = ipAddress[0:findNth(ipAddress, ".", 3)+1] + "0"
                    elif index == 2: # octete 3
                        prevP = findNth(ipAddress, ".", 2) # start of octete 3
                        nextP = findNth(ipAddress, ".", 3) # end of octete 3
                        newIP = ipAddress[0:prevP+1] + "0" + ipAddress[nextP:]
                    elif index == 1: # octete 2
                        prevP = findNth(ipAddress, ".", 1) # start of octete 2
                        nextP = findNth(ipAddress, ".", 2) # end of octete 2
                        newIP = ipAddress[0:prevP+1] + "0" + ipAddress[nextP:] # update line
                    else: # octete 1
                        nextP = findNth(ipAddress, ".", 1) # end of octete 1
                        newIP = "0" + ipAddress[nextP:] # update line
                    line[0] = line[0].replace(ipAddress,newIP)
                    IpOctetes[index] = "0" # update octete list
                    ipAddress = newIP

                    #return False
                if(int(SubnetOctetes[index]) == 254 or int(SubnetOctetes[index]) == 255):
                    continue # subnets 31 and 32 are okay be default, no check needed
                if (int(SubnetOctetes[index]) != 0):
                    # print(SubnetOctetes[index])
                    if (OcteteComparer(int(IpOctetes[index]),int(SubnetOctetes[index]),line)): # continue if no errors detected, else return false
                        continue
                    else:
                        print("\nInvalid IP subnet pair detected on the line: ",line[0])
                        error_str = "Invalid IP subnet pair detected on the line: \n" + line[0] + "\n" + "type 1 to edit IP, 2 to edit subnet, or anything else to delete line: "
                        userChoice = simpledialog.askinteger("Modify IP/subnet pair", error_str, parent = tkinter_object)
                        if (userChoice == 1): # edit IP
                            ip_str = "input the new ip in the format of 4 octetes seperated by periods"
                            new_ip = simpledialog.askstring("Modify IP/subnet pair", ip_str, parent = tkinter_object)

                            line[0] = line[0].replace(ipAddress,new_ip) # swap in new ip for old ip
                            return True
                        elif (userChoice == 2): # edit subnet
                            sub_str = "input the new subnet in the format of 4 octetes seperated by periods"
                            new_subnet = simpledialog.askstring("Modify IP/subnet pair", sub_str, parent = tkinter_object)
                            line[0] = line[0].replace(subnetMask,new_subnet) # swap in new ip for old ip
                            return True
                        return False
        return True
    except:
        print("\nError in ValidIPSubNetPair function")





