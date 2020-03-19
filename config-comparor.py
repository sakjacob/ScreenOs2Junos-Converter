"""
To Do
*apply IP verification to set address lines
    * beware of edge cases where last two args are not the ips
"""

import math


def main():
    tool_config = "C:\\Users\\sakjacob\\Desktop\\S2J\\bcc\\bcc-edit-srx_tool.config"
    fp_tool = open(tool_config,"r")
    orig_config = "C:\\Users\\sakjacob\\Desktop\\S2J\\bcc\\bcc-srx.config"
    print(orig_config)
    fp_orig = open(orig_config,"r")

    orig_lines = set(fp_orig.readlines())
    tool_lines = fp_tool.readlines()

    line_num = 1
    for line in tool_lines:
        if line not in orig_lines:
            print("\nline ",line_num, "is not in the orig set")
            print(line)
        line_num += 1




    print("Done")




if __name__ == "__main__":
    main()