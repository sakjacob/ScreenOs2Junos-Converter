"""
This program converts a ScreenOS firewall configuration to 
JunOS. 

For more information on the conversion, see the files "Orig2Edit.py"
and "Edit2Config.py"

Author: Jake Sak
Last editted: 4-6-20

to do:
* have a pop up after a config complete which informs user of manual review file
and where config is saved. 
    "Make sure to view the manual review file and add any necassary changes to the config saved at ___"
* add conversion complete or "bug occured" pop up
    * try and catch around conversion tool?
"""

import Orig2Edit
import Edit2Config
from tkinter import filedialog
from tkinter import *
import tkinter as tk
import sys
import traceback

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()
        self.SOS_path = "" # filename for screenos config 
        self.dst_path = "" # path for destination config
        self.SOS_bool = False # update to true once screenOS filename acquired
        self.dst_bool = False # update to true once destination path acquired

    def create_widgets(self):
        self.ScreenOs = tk.Button(self)
        self.ScreenOs["text"] = "Select ScreenOS config"
        self.ScreenOs["command"] = self.Update_SOS
        self.ScreenOs.grid(column=0, row=0)
        #self.ScreenOs.pack(side="top")
        self.Screen_lbl = Label(self, text="Nothing selected")
        self.Screen_lbl.grid(column=1, row = 0)

        self.dst_disclaimer = Label(self, text="Save to an empty folder to prevent \n overwrittening identical filenames", font=("Arial Bold", 10))
        self.dst_disclaimer.grid(column = 0, row = 1)
        self.dst = tk.Button(self)
        self.dst["text"] = "Select Directory to save \n new config and other outputs"
        self.dst["command"] = self.Update_dst
        self.dst.grid(column = 0, row = 2)
        self.dst_lbl = Label(self, text="Nothing selected")
        self.dst_lbl.grid(column=1, row = 2)
        #self.dst.pack(side="top")

        

        self.run = tk.Button(self)
        self.run["text"] = "Start conversion"
        self.run["command"] = self.Run
        self.run.grid(row=3)

        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=self.master.destroy)
        self.quit.grid(row=4)


    def Update_SOS(self):
        temp = tk.filedialog.askopenfilename()
        if temp is not None:
            self.SOS_bool = True
            self.SOS_path = temp
            self.Screen_lbl["text"] = temp
            print(temp)

    def Update_dst(self):
        temp = tk.filedialog.askdirectory()
        if temp != "":
            self.dst_bool = True
            self.dst_path = temp
            self.dst_lbl["text"] = temp
            print(temp)

    def Run(self):
        if self.SOS_bool and self.dst_bool:
            #print("Successful run")
            try:
                Orig2Edit.Convert(self.SOS_path, self.dst_path, self)
                edit_FileName = self.SOS_path[:self.SOS_path.find(".txt")] + "-edit_tool.txt" 
                Edit2Config.Convert(edit_FileName,self.dst_path, self)
                messagebox.showinfo("Success","Conversion Complete")
            except:
                # error_str = "Failed Conversion due to: " + str(sys.exc_info()[0])
                # for thing in sys.exc_info():
                #     print(thing)
                messagebox.showerror("Conversion Failure", traceback.format_exc())
                print("bug occured")
        else:
            print("Nope!")

root = tk.Tk()
root.geometry('450x200')
root.title("S2J Conversion Tool")
app = Application(master=root)
app.mainloop()

# Orig2Edit.Convert(self.SOS_path)
# edit_FileName = self.SOS_path[:self.SOS_path.find(".txt")] + "-edit_tool.txt" 
# Edit2Config.Convert(edit_FileName)