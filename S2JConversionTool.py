"""
This program converts a ScreenOS firewall configuration to 
JunOS. 

For more information on the conversion, see the files "Orig2Edit.py"
and "Edit2Config.py"

Author: Jake Sak
Last editted: 3-19-20

to do:
* remove temporary files like edit
* ask for save location
* prompt for desired name of resulting config
* add required.txt to repo so users can download required extensions
* update readme with tutorial on how to download and use program
* have user select a save location that will 
"""

import Orig2Edit
import Edit2Config
from tkinter import filedialog
import tkinter as tk

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
        self.ScreenOs.pack(side="top")

        self.dst = tk.Button(self)
        self.dst["text"] = "Save new Junos \n config as?"
        self.dst["command"] = self.Update_dst
        self.dst.pack(side="top")

        self.run = tk.Button(self)
        self.run["text"] = "Start conversion"
        self.run["command"] = self.Run
        self.run.pack(side="top")

        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=self.master.destroy)
        self.quit.pack(side="bottom")


    def Update_SOS(self):
        temp = tk.filedialog.askopenfilename()
        if temp is not None:
            self.SOS_bool = True
            self.SOS_path = temp
            print(temp)

    def Update_dst(self):
        temp = tk.filedialog.asksaveasfilename()
        if temp is not None:
            self.dst_bool = True
            self.dst_path = temp
            print(temp)

    def Run(self):
        if self.SOS_bool and self.dst_bool:
            print("Successful run")
            Orig2Edit.Convert(self.SOS_path, self)
            edit_FileName = self.SOS_path[:self.SOS_path.find(".txt")] + "-edit_tool.txt" 
            Edit2Config.Convert(edit_FileName,self.dst_path, self)
        else:
            print("Nope!")

root = tk.Tk()
app = Application(master=root)
app.mainloop()

# Orig2Edit.Convert(self.SOS_path)
# edit_FileName = self.SOS_path[:self.SOS_path.find(".txt")] + "-edit_tool.txt" 
# Edit2Config.Convert(edit_FileName)