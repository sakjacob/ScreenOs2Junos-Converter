"""
To Do
*apply IP verification to set address lines
    * beware of edge cases where last two args are not the ips
"""

import math


def main():
    userChoice = input("Type 1 to compare orginal to tool, 2 to compare tool to original: ")
    tool_config = "C:\\Users\\sakjacob\\Desktop\\S2J\\bcc\\bcc-edit-srx_tool.config"
    fp_tool = open(tool_config,"r")
    orig_config = "C:\\Users\\sakjacob\\Desktop\\S2J\\bcc\\bcc-srx.config"
    print(orig_config)
    fp_orig = open(orig_config,"r")
    log = "C:\\Users\\sakjacob\\Desktop\\S2J\\bcc\\config-comparision.txt"
    fp_log = open(log, "w")

    orig_lines = fp_orig.readlines()
    orig_set = set(orig_lines)
    tool_lines = fp_tool.readlines()
    tool_set = set(tool_lines)


    if int(userChoice) == 2:
        print("Checking if lines from tool exist in the orginal.")
        line_num = 1
        for line in tool_lines:
            if line not in orig_set:
                print("\nline ",line_num, "is not in the orig set")
                print(line)
                fp_log.write(line)
            line_num += 1
    elif int(userChoice) == 1:
        print("Checking if lines from orginal exist in the tool.")
        line_num = 1
        for line in orig_lines:
            if line not in tool_set:
                print("\nline ",line_num, "is not in the tool set")
                print(line)
                fp_log.write(line)
            line_num += 1




    print("Done")




if __name__ == "__main__":
    main()