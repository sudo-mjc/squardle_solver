import csv as csv
import tkinter as tk

class CSV(object):

    def __init__(self, master):
        self._master = master
        master.title('Csv listbox test file')
        master.minsize(500, 500)

        self._scale_filePath = "C:/Users/Mitchell Crawford/Google Drive/Uni Work/Third Year/ENGG2800/Project/scales.csv"

        self._scales_file = open(self._scale_filePath, "r")
        self._scales_read = csv.reader(self._scales_file)
        self._scales_data = list(self._scales_read)
        self._scales_seletion = None
        self._scaleListSelect = None

        #Variables to store listed elements
        self._scales_names = []
        self._scales_options = [11]

        # Read all scale names
        # Picking rows from files to show each scale once in the list
        for x in range(0, len(self._scales_data), 12):
            self._scales_names.append(self._scales_data[x][0])

        #Make Frames for neat packing of widgets
        self._ScalesFrame = tk.Frame(master)
        self._ScalesFrame.pack()
        self._listboxFrame = tk.Frame(self._ScalesFrame)
        self._listboxFrame.pack(side=tk.TOP)
        self._listBtnFrame = tk.Frame(self._ScalesFrame)
        self._listBtnFrame.pack(side=tk.BOTTOM)

        self._scaleLockLbl = tk.Label(self._listBtnFrame, padx=5, pady=5, width=60, relief=tk.SUNKEN
                                      ,text="")
        scrollbar = tk.Scrollbar(self._listboxFrame, orient=tk.VERTICAL)
        self._scalesListbox = tk.Listbox(self._listboxFrame, bg='ghost white', bd=4
                             , height=10, cursor='arrow', relief=tk.SUNKEN
                             , selectmode=tk.SINGLE, yscrollcommand=scrollbar.set)

        self._optionsListbox = tk.Listbox(self._listboxFrame, bg='lemon chiffon', bd=4
                                          , height=10, cursor='target', relief=tk.RIDGE
                                          , selectmode=tk.SINGLE, yscrollcomman=scrollbar.set, width=45)

        # Buttons to confirm selections and update lists
        self._listSelect = tk.Button(self._listBtnFrame, relief=tk.GROOVE, text='View', command=self.ScaleSelection)
        self._ScaleLockBtn = tk.Button(self._listBtnFrame, relief=tk.GROOVE, text='View', command=self.EnableScaleLock)
        self._ScaleSelect = tk.Button(self._listBtnFrame, relief=tk.GROOVE, text='Select', command=self.SetScaleLock)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._scaleLockLbl.pack()
        self._listSelect.pack(side=tk.LEFT, pady=5, padx=50)
        self._ScaleSelect.pack(side=tk.RIGHT, pady=5, padx=100)
        self._scalesListbox.pack(side=tk.LEFT, pady=10, padx=10)
        self._optionsListbox.pack(side=tk.LEFT, pady=10, padx=10)
        scrollbar.config(command=self._scalesListbox.yview)

        # For each iteration of x (limited to the number of rows in scales_names list), insert
        for x, y in enumerate(self._scales_names):
            self._scalesListbox.insert(x, y)

    def ScaleSelection(self):
        # Allows the user to see what scales relate to the name they chose
        self._scaleListSelect = (self._scalesListbox.curselection())[0]
        print(self._scaleListSelect)
        self.ScalesOptions(self._scaleListSelect)

    def ScalesOptions(self, selection):
        """Based on the scale chosen, find the row number in the CSV for that scale and show
        all relevant scales that proceed it"""
        # Clear scales options list first
        self._scales_options = []

        # Track position in scales options list
        counter = 0
        csv_step = selection * 12

        for x in range((csv_step), (csv_step + 12), 1):
            self._scales_options.append(self._scales_data[x][1:(len(self._scales_data[x]))])
            counter += 1

        for x, y in enumerate(self._scales_options):
            self._optionsListbox.insert(x,y)

    def SetScaleLock(self):
        """Sets the scale lock chosen by the user"""
        note_select = (self._optionsListbox.curselection())[0]
        scaleArrNum = ((self._scaleListSelect * 12) + (note_select))
        self._scales_seletion = self._scales_data[scaleArrNum]
        self._scaleLockLbl.config(text=f"Scale Lock: {self._scales_seletion}")
        print(note_select)
        print(scaleArrNum)
        print(self._scales_seletion)

    def EnableScaleLock(self):
        """Sets the scale lock chosen and    """


# __________________________________________________________________________________________________
# BOOT______________________________________________________________________________________________
if __name__ == '__main__' :
    root = tk.Tk()
    app = CSV(root)
    root.mainloop()

#___________________________________________________________________________________________________