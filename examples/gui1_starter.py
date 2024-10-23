"""
Simple GUI programming exercise to demonstrate component layout
and event handling.
"""

__copyright__ = "Copyright 2018, University of Queensland"


import tkinter as tk
from tkinter import messagebox


class SampleApp(object) :
    def __init__(self, master) :
        self._master = master
        master.title("Hello!")
        master.minsize(430, 200)

        self._lbl = tk.Label(master, text="This label is white", bg= "white")
        self._lbl.pack(expand= True)

        frame = tk.Frame(master)
        frame.pack(side=tk.TOP, pady=10)

        text_frame = tk.Frame(master)
        text_frame.pack(side=tk.BOTTOM, pady=10)

        btn_Blue = tk.Button(frame, text="Change to Blue", command=self.colour_blue)
        btn_Blue.pack(side=tk.RIGHT)

        btn_Red = tk.Button(frame, text="Change to Red", command=self.colour_red)
        btn_Red.pack(side=tk.LEFT)

        text_enter = tk.Entry(text_frame, text="Change the colour to:")
        text_enter.pack(side=tk.LEFT)
        self._text_enter = text_enter

        change_button = tk.Button(text_frame, text="Change it!", command=self.new_colour)
        change_button.pack(side=tk.RIGHT)

    def colour_blue(self):
        self._lbl.config(text="This label is blue", bg = "Blue")
        print("Label colour changed to Blue")

    def colour_red(self):
        self._lbl.config(text="This label is red", bg = "Red")
        print("Label colour changed to Red")

    def new_colour(self):
        colour = self._text_enter.get()
        try:
            self._lbl.config(text=f'This label is {colour}',bg = colour)
            print(f'Label colour changed to {colour}')
            
        except:
            messagebox.showerror("Invalid Error", f'{colour} is not an option!')

if __name__ == "__main__" :
    root = tk.Tk()
    app = SampleApp(root)
    root.mainloop()
