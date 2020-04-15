# ScreenOs2Junos-Converter
This code converts firewall configurations written for ScreenOs to Juniper OS

Installation:
1. Download this repository from https://github.com/sakjacob/ScreenOs2Junos-Converter
2. Extract repository from zip file to folder of user's desire
3. If python is not already installed, install python at https://www.python.org/
	a. (optional) Check box to add python to path during installation. This makes running program simplier
	*Developed on python 3.7.3 but earlier versions may work too. Tested to work on 3.8.2 as well.
	
Running:
1. Located the file "S2JConversionTool.py"
2. Double click "S2JConversionTool.py"
	a. If the program runs,  hurray! (python is part of user's path)
	b. If the file doesn't run, try one of the following
		i. In cmd, navigate to the folder containing "S2JConversionTool.py"
		ii. type and enter "python S2JConversionTool.py"
		
		or 
		
		i. Right click "S2JConversionTool.py" and open with python 

Covered by conversion tool:
policies (manual intervention needed for predefined service groups)
applications
address
address sets/books


Not covered by conversion tool:
zones
interfaces
predfined service groups in policies. User will be notified of these lines, however
VPN
Routing instances