"""
This program converts a ScreenOS firewall configuration to 
JunOS. 

For more information on the conversion, see the files "Orig2Edit.py"
and "Edit2Config.py"

Author: Jake Sak
Last editted: 4-20-20

to do:

"""

import Orig2Edit # preps ScreenOs config. Cuts lines, modifies keywords, validifies IP subnet Pairings 
import Edit2Config # Converts the prepped ScreenOS file into a Junos Config
from tkinter import filedialog # anything tkinter is for gui
from tkinter import *
import tkinter as tk
import traceback # for displaying info regarding crashes

"""
The application class provides a GUI for the conversion tool
"""
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

    """
    The main window of the conversion tool
    """
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

    """
    Store the users choice of ScreenOs config
    """
    def Update_SOS(self):
        temp = tk.filedialog.askopenfilename()
        if temp is not None:
            self.SOS_bool = True
            self.SOS_path = temp
            self.Screen_lbl["text"] = temp
            print(temp)

    """
    Select which directory output files are saved to
    """
    def Update_dst(self):
        temp = tk.filedialog.askdirectory()
        if temp != "":
            self.dst_bool = True
            self.dst_path = temp
            self.dst_lbl["text"] = temp
            print(temp)

    """
    Run the conversion

    Also prompts user if they've failed to select necassary inputs and also provides
    error messages in case of failed conversions.
    """
    def Run(self):
        if self.SOS_bool and self.dst_bool:
            try:
                Orig2Edit.Convert(self.SOS_path, self.dst_path, self) # run the program Orig2Edit.py
                edit_FileName = self.SOS_path[:self.SOS_path.find(".txt")] + "-edit_tool.txt" 
                Edit2Config.Convert(edit_FileName,self.dst_path, self) # run the program Edit2Config.py
                messagebox.showinfo("Success","Conversion Complete")
            except: # Catchs all any error during conversion and converts it to tkinter popup
                messagebox.showerror("Conversion Failure", traceback.format_exc())
                print("bug occured")
        else: # user tried to run conversion without required inputs, reprompt user
            messagebox.showerror("Conversion Failure", "Select all required input before running")

#format and configure main page of gui
root = tk.Tk()
root.geometry('450x200')
root.title("S2J Conversion Tool")
app = Application(master=root)
app.mainloop()