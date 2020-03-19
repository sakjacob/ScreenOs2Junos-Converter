"""
This program converts a ScreenOS firewall configuration to 
JunOS. 

For more information on the conversion, see the files "Orig2Edit.py"
and "Edit2Config.py"

Author: Jake Sak
Last editted: 3-19-20
"""

import Orig2Edit
import Edit2Config

print("Welcome to the ScreenOS to Juniper Conversion Tool \n")
OG_Filename = input("Please provide the full path of the ScreenOs file you wish to convert: ")
Orig2Edit.Convert(OG_Filename)
edit_FileName = OG_Filename[:OG_Filename.find(".txt")] + "-edit_tool.txt" 
Edit2Config.Convert(edit_FileName)