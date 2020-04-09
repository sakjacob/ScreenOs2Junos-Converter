"""
To Do
*apply IP verification to set address lines
    * beware of edge cases where last two args are not the ips
"""

import math
from tkinter import filedialog
from tkinter import *
import tkinter as tk


def main(example_filename, tool_filename, save_folder):
    fp_tool = open(tool_filename,"r") # filename for tool config
    fp_orig = open(example_filename,"r") # filename for example config

    orig_lines = fp_orig.readlines()
    orig_set = set(orig_lines)
    tool_lines = fp_tool.readlines()
    tool_set = set(tool_lines)


    print("Checking if lines from tool exist in the orginal.")
    log = save_folder + "\\lines-not-in-orig.txt"
    fp_log = open(log, "w")
    line_num = 1
    for line in tool_lines:
        if line not in orig_set:
            print("\nline ",line_num, "is not in the orig set")
            print(line)
            fp_log.write(line)
        line_num += 1
    fp_log.close()
    print("Checking if lines from orginal exist in the tool.")
    log = save_folder + "\\lines-missing-in-tool.txt"
    fp_log = open(log, "w")
    line_num = 1
    for line in orig_lines:
        if line not in tool_set:
            print("\nline ",line_num, "is not in the tool set")
            print(line)
            fp_log.write(line)
        line_num += 1
    fp_log.close()

    fp_orig.close()
    fp_tool.close()
    print("Done")

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()
        self.e_path = "" # filename for example config 
        self.dst_path = "" # path for destination config
        self.e_bool = False # update to true once eConfig filename acquired
        self.dst_bool = False # update to true once destination path acquired
        self.t_path = "" # filename for tool config
        self.t_bool = False # update to true once tool config filename acquired

    def create_widgets(self):
        self.eConfig = tk.Button(self) # example config
        self.eConfig["text"] = "Select eConfig config"
        self.eConfig["command"] = self.Update_Example
        self.eConfig.grid(column=0, row=0)
        self.e_lbl = Label(self, text="Nothing selected")
        self.e_lbl.grid(column=1, row = 0)

        self.tConfig = tk.Button(self) # tool config
        self.tConfig["text"] = "Select tConfig config"
        self.tConfig["command"] = self.Update_Tool
        self.tConfig.grid(column=0, row=1)
        self.t_lbl = Label(self, text="Nothing selected")
        self.t_lbl.grid(column=1, row = 1)

        self.dst = tk.Button(self)
        self.dst["text"] = "Select Directory to save \n new config and other outputs"
        self.dst["command"] = self.Update_dst
        self.dst.grid(column = 0, row = 2)
        self.dst_lbl = Label(self, text="Nothing selected")
        self.dst_lbl.grid(column=1, row = 2)


        

        self.run = tk.Button(self)
        self.run["text"] = "Start conversion"
        self.run["command"] = self.Run
        self.run.grid(row=3)

        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=self.master.destroy)
        self.quit.grid(row=4)


    def Update_Example(self):
        temp = tk.filedialog.askopenfilename()
        if temp is not None:
            self.e_bool = True
            self.e_path = temp
            self.e_lbl["text"] = temp
            print(temp)

    def Update_Tool(self):
        temp = tk.filedialog.askopenfilename()
        if temp is not None:
            self.t_bool = True
            self.t_path = temp
            self.t_lbl["text"] = temp
            print(temp)

    def Update_dst(self):
        temp = tk.filedialog.askdirectory()
        if temp != "":
            self.dst_bool = True
            self.dst_path = temp
            self.dst_lbl["text"] = temp
            print(temp)

    def Run(self):
        if self.e_bool and self.t_bool and self.dst_bool:
            print("Successful run")
            main(self.e_path,self.t_path,self.dst_path)
        else:
            print("Nope!")

root = tk.Tk()
root.geometry('450x200')
root.title("Junos Config Comparor")
app = Application(master=root)
app.mainloop()

# Orig2Edit.Convert(self.e_path)
# edit_FileName = self.e_path[:self.e_path.find(".txt")] + "-edit_tool.txt" 
# Edit2Config.Convert(edit_FileName)