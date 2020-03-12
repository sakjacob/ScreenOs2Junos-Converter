import shlex
import fileinput

addresses = []
addressSets = []
policies = []
applications = []

class Policy:
    def __init__(self):
        self.mID = ""
        self.mFromZone = ""
        self.mToZone = ""
        self.mSrcAdress = []
        self.mDestAdress = []
        self.mApplication = ""
        self.mAction = ""

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

    def __eq__(add2):
        if self.mAddress == add2.mAddress:
            return True      

class AddressGroup:
    def __init__(self):
       self.mSetName = ""
       self.mZone = ""
       self.mAddresses = []


print("Welcome to the ScreenOS to Juniper Conversion Tool \n")
fileName = input("Please type the filename you would like to convert with the file extension (i.e. file.txt): \n")
lSystem = input("Please type in the name of the logical system you would like to use: \n")

if lSystem == "" or fileName == "": # make sure logical system gets a value, if not we don't want to create a bad config 
    raise AssertionError("No logical system name or filename input")

logicalSystemLine = ["set", "logical-systems", str(lSystem), "security"] # covers adresses and policies
applicationsLine = ["set", "applications", "application"] # covers applications

try:
    file = open(fileName, "r")
except:
    raise AssertionError("Cannot open file")

for line in file:
    
    policy = False # these will determine what type of line we are on in the config
    application = False
    address = False
    adressSet = False

    splitLine = shlex.split(line)

    if splitLine[1] == "address":
        address = True
    # for key in splitLine:
    #     if key == "policy" and len(splitLine) > 4: # determines what type of line it is editing
    #         policy = True
    #         break
    #     if splitLine[1] == "src-address": # any excess info for policies gets stored in the last object stored
    #         policies[-1].mSrcAdress.append(splitLine[2])
    #     if splitLine[1] == "dest-address":
    #         policies[-1].mDestAdress.append(splitLine[2])
    #     if addressSets and splitLine[1] == "group": # any excess address in this group get added to that object
    #         if splitLine[4] == addressSets[-1].mSetName:
    #             nf = splitLine[6]
    #             nf = nf[1:-1]
    #             addressSets[-1].mAddresses.append(nf)
    #             break
            
    #     if key == "address":
    #         address = True
    #         break
    #     if key == "group":
    #         adressSet = True
    #         break
    #     if key == "service":
    #         application = True
    #         break
        

    if policy == True:
        pol = Policy()
        for option in range(len(splitLine)): # get the components of the line and store them in an object
            if splitLine[option] == "id":
                pol.mID = splitLine[option + 1]
            if splitLine[option] == "from":
                pol.mFromZone = splitLine[option + 1]
            if splitLine[option] == "to":
                pol.mToZone = splitLine[option + 1]
                pol.mSrcAdress.append(splitLine[option + 2])
                pol.mDestAdress.append(splitLine[option + 3])
                pol.mApplication = splitLine[option + 4]
                pol.mAction = splitLine[option + 5]
                break
        policies.append(pol)
        
    elif address == True:
        # check if IPV4 or IPV6
        if "::" in splitLine[4]: # IPV6 address
            pass
        else: #IPV4
            if len(splitLine) < 6:
                print("\nIPV4 index error. Line reads:")
                print(line)
                continue
            address = Address()
            address.mSecurityZone = str(splitLine[2])
            address.mDomain = str(splitLine[3])
            # address.mDomain = address.mDomain[1:-1]
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
            addresses.append(address)
            #print(address.mDomain, address.mAddress)
    elif adressSet == True:
        addressGroup = AddressGroup()
        addressGroup.mSetName = splitLine[4]
        addressGroup.mZone = splitLine[3]
        addressSets.append(addressGroup)
    elif application == True:
        pass
file.close()

new_name = "" # This will write the name of the file in srx.config style
dst_str = ""
for i in range(len(fileName)):
    if fileName[i] == "-":
        dst_str = fileName[0:i] + "-srx_tool.config"
fp_dst = open(dst_str,"w")
print(fp_dst)
for addyLine in addresses: # write addresses first
    output = "set logical-systems " + lSystem + " security address-book global address " + addyLine.mDomain + " " + addyLine.mAddress + "\n"
    fp_dst.write(output)