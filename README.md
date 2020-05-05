# ScreenOs2Junos-Converter
This code converts firewall configurations written for ScreenOs to Juniper OS

## Covered by conversion tool:
* applications
* addresses
* address sets/books
* interfaces
* policies (junos service groups detected but not converted, see manual-review output file)

## Beta:
* zones (ping and traceroute lines enabled by default, other lines not converted)


## Not covered by conversion tool:
* VPN
* Routing instances


## Important Notes:
* session init is enabled by default for each policy
* ping and traceroute enabled by default for each zone
* inet6 dad-disable by default for each interface

# Installation:
1. Download this repository from https://github.com/sakjacob/ScreenOs2Junos-Converter
2. Extract repository from zip file to folder of user's desire
3. If python is not already installed, install python at https://www.python.org/
	* (optional) Check box to add python to path during installation. This makes running program simplier
	* Developed on python 3.7.3 but earlier versions may work too. Tested to work on 3.8.2 as well.
	
# Running:
1. Located the file "S2JConversionTool.py"
2. Double click "S2JConversionTool.py"
	* If the program runs,  hurray! (python is part of user's path)
	* If the file doesn't run, try one of the following
		1.
			* In cmd, navigate to the folder containing "S2JConversionTool.py"
			* type and enter "python S2JConversionTool.py"
		2. 
			* Right click "S2JConversionTool.py" and open with python 

