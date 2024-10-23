"""
A GUI program used to generate all possible words in a NxN
grid of letters, as per the online game squardle.io
Author: Mitchell Crawford

This project is public and may be utilised by any and all individuals freely
"""

import tkinter as tk
from tkinter import messagebox

class SquardleApp(object):
    def __init__(self, master):
        # Class variables
        self._data = None
        self._size = 0
        self._master = master
        self._entries = None
        # Create window for GUI
        master.title("Squardle Solver Tool")
        master.minsize(500, 250)
        # Frame for storing the input grid
        self._grid_frame = tk.Frame(master)
        self._grid_frame.pack(side = tk.TOP)
        # Temporary lable for instruction
        self._grid_lbl = tk.Label(self._grid_frame, text="Input a table size below")
        self._grid_lbl.pack(expand = True)
        # Frame for storing all entry objects
        size_entry_frame = tk.Frame(master)
        size_entry_frame.pack(side=tk.BOTTOM, pady=10)
        # Entry text field for grid size
        self._size_entry = tk.Entry(size_entry_frame, text="Number of Rows/Columns?")
        self._size_entry.pack(side=tk.LEFT)
        # Button for taking user input
        entry_button = tk.Button(size_entry_frame, text="Enter", command=self.new_puzzle)
        entry_button.pack(side = tk.RIGHT)
        # Button to solve grid
        self._solve_grid = tk.Button(self._grid_frame, text = "Process", command = self.gather_input)
        # Frame to contain the grid
        self._grid_frame = tk.Frame(master)

    def new_puzzle(self):
        # Get the entry made by the user
        print("Gnerating new puzzle grid")
        entryString = self._size_entry.get()
        if (entryString.isdigit()):
            # the input was a valid digit
            numElements = int(entryString)
            self._size = numElements
        else:
            messagebox.showwarning("Invalid Input", "Please input a value of N for the puzzle size")
            return
        # Create a 1D array able to fit the NxN size puzzle
        self._data = []
        self.generate_grid(numElements)
    
    def generate_grid(self, n: int) -> None:
        """
        Generate a new grid of entry boxes to collect the letters of the
        given puzzle and store these input boxes into self._data
        """
        self._grid_frame.pack_forget()
        self._grid_lbl.config(text = "Processing!")
        self._entries = []
        for i in range((n*n)):
            newBox = tk.Entry(self._grid_frame, width=5)
            xPos = i % n
            yPos = i // n
            newBox.grid(row = xPos, column = yPos, sticky = tk.W, pady=10, padx = 10)
            self._entries.append(newBox)

        # Remove the lable before packing the new array
        self._grid_lbl.pack_forget()
        # Pack the new grid into the window
        self._solve_grid.pack(side = tk.TOP)
        self._grid_frame.pack(side = tk.BOTTOM)

    def gather_input(self):
        """
        Gathters the user's input from each of the entry boxes
        """
        # Initialise array to store entry inputs
        self._data = []
        # Loop through Entry objects in the grid
        for entry in self._entries:
            # Get the data from each Entry and append it to the array
            self._data.append(entry.get())
    
    def process_input(self):
        """
        Process the user input to determine all valid words that can be
        made from the puzzle inputs
        """
        print("To be implemented")

if __name__ == "__main__":
    root = tk.Tk()
    app = SquardleApp(root)
    root.mainloop()
    