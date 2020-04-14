"""
This program edits a ScreenOS config to before being processed by a
conversion tool.

This includes 
*verifying valid ip subnet pairs. Prompting user to fix flaws
*Cuts lines which are not "set interface", "set zone", "set group address", "set service",
"set src-address", "set dst-address" or "set group service"
*Replaces invalid word choice with correct diction
*Culls other edge cases

This program only cuts/modifies a line if it detects a flaw. By default
lines will be copied from orginal document to edit file.

Author: Jake Sak
Last edit: 3-19-20

To do
*make names for intermediary files more concise
"""


import valid_subnet
import shlex

def Convert(src_str, dst_folder, tkinter_object):
    # src_str = "C:\\Users\\sakjacob\\Desktop\\S2J\\cal\\cal-orig.txt"
    fp_src = open(src_str,"r")
    dst_str = src_str[:src_str.find(".txt")] + "-edit_tool.txt" #tool differienties this file from the examples, remove "tool" when finalized
    print(dst_str)
    fp_dst = open(dst_str,"w")
    fp_cut = open(dst_folder + "\\cut.txt","w")

    lines = fp_src.readlines()
    try:
        for line in lines:
            if ("set interface" in line or "set zone" in line or "set address" in line or "set group address" in line or "set policy" in line or "set service" in line or "set src-address" in line or "set dst-address" in line or "set group service" in line):
                line = line.replace("Any-IPv4","any")
                line = line.replace("ICMP-ANY","icmp-all")
                if "set address" in line:
                    arg_list = shlex.split(line)
                    if arg_list[-1] == "255.255.255.0": # previous ip needs to end with 0
                        start = arg_list[-2].rfind('.') 
                        new_ip = arg_list[-2][:start+1] + '0' # orginal ip but last num is 0
                        line = line.replace(arg_list[-2],new_ip) # swap in new ip for old ip
                    # validate that IP and subnet pairs are valid
                    validIPV4 = True
                    if len(arg_list) < 6: # if less than 5 args there is not an IP subnet pair in this line
                        validIPV4 = False
                    if "::" in line: # This line contains an IPV6 address, IPV6 addresses are not checked
                        validIPV4 = False
                    if validIPV4: # if an IPV4 line, verify subnet and IP pairing
                        lineInList = [line] # allows line (normally immutable) to be modified by called functions
                        valid_ip = valid_subnet.ValidIPSubNetPair(arg_list[4], arg_list[5], lineInList, tkinter_object)
                        line = lineInList[0]
                        if not valid_ip:
                            fp_cut.write(line)
                            continue # do not write this line
                if "ethernet" not in line and "screen icmp-id" not in line and "unset zone" not in line:
                    fp_dst.write(line)
                else: # line cut
                    fp_cut.write(line)
                if "timeout never" in line:
                    print("Warning: conversation contains timeout never. May want to check/revise this line")

            else: # cut lines
                fp_cut.write(line)
    except:
        print("\nError in main")

    fp_src.close()
    fp_dst.close()
    fp_cut.close()

# if __name__ == "__main__":
#     Convert()
    #valid_subnet.ValidIPSubNetPair("31.124.115.12", "255.255.255.254")