"""
ENGG2800 MIDI Project Gui Code

Mitchell Crawford (s4584081) -- Sem One, 2021

The following works through a range of libraries (found in InfoTextsURLs.txt)
and is inspired by the code personally written in past CSSE1001 practicals
"""
# Imported libraries for use in the file
import tkinter as tk
from tkinter import messagebox
import csv as csv
import serial as ser
import time
import threading


# _____________________________________________________________________________
# Threading Class


class ThreadCreate(threading.Thread):
    """ A class used to establish and run threads for the concurrent running
     and processing of operations whilst TkInter root.mainloop is in operation
    """

    def __init__(self, name, com_port, text_labels, key_refs, keys_canvas):
        super().__init__(daemon=True)
        self.thread_name = name
        self._thread_com = com_port
        self._label_access = text_labels
        self._key_refs = key_refs
        self._key_canvas = keys_canvas

        # General Class Variables for storing received
        # default and calculated information
        self._sharp_index = [1, 3, 6, 8, 10]
        self._waveforms = ["Triangle", "Saw", "Square", "Noise", "Drawn",
                           "Sine", "NSine", "ASine"]
        self._info_received = ''
        self._info_data = ''
        self._info_prefix = ''
        self._info_note = 0
        self._current_oct = 3
        self._current_tempo = 0.0
        self._current_arp = 1.0
        self._exit_message = ''
        self._exit_flag = None

    def run(self):
        # Function called when start is executed, containing the
        print(f'Thread {self.thread_name} Initiated')
        self._exit_flag = False
        waiting_bits = 0
        while not self._exit_flag:
            # Check if the com port is still active
            # if true then raise exit flag/ terminate loop
            if not self._thread_com.isOpen():
                # If port is closed then show error and terminate loop
                self._exit_flag = True
                self._thread_com.close()
                self._exit_message = f'Port {self._thread_com.port} closed!'
                # pass this loop of the thread to trigger exit flag
                pass

            # Check for waiting bits in the buffer
            try:
                waiting_bits = self._thread_com.inWaiting()

            except ser.SerialException:
                self._exit_flag = True
                self._exit_message = f'Port {self._thread_com.port} was lost!'

            # Receiving and parsing strings into simplified formats
            if waiting_bits != 0:
                # Set try statement

                # Attempt read and info conversion
                self._info_received = self._thread_com.read(8) \
                    .strip().decode('utf-8')
                print(self._info_received)

                self._info_prefix = int(self._info_received[0:1])
                self._info_note = int(self._info_received[3:6])
                self._info_data = self._info_received[2:6]

                # Check if the message control change or note control
                if (self._info_prefix == 9) or (self._info_prefix == 0):
                    # Note Control
                    if self._info_prefix == 9:
                        # Note On
                        self.display_note(1, self._info_note)
                    else:
                        # Note Off
                        self.display_note(0, self._info_note)
                else:
                    # Control Change
                    self.control_change(self._info_prefix, self._info_data)
            time.sleep(0.01)

        # Should the loop be broken, destroy the main window and elements
        print(f'Thread {self.thread_name} exiting')
        self._exit_message = "Exit Flag Raised!"
        self.thread_shutdown()

    def display_note(self, note_op, note_value):
        # Used to turn GUI keys on or off according to note messages
        # Calculate the lowest key value for mid and high octaves
        mid_oct_calc = (self._current_oct + 3) * 12
        high_oct_calc = (self._current_oct + 4) * 12
        print(f'{self._info_note},{mid_oct_calc}, {high_oct_calc}')
        # key index position
        octave_select = 2
        note_index = (note_value % 12)
        if note_value < mid_oct_calc:
            # Key is in the lower octave and adjust note index for 7 indexs
            octave_select = 0
            note_index = (note_value % 12) - 5

        elif note_value < high_oct_calc:
            # key is in the middle octave
            octave_select = 1
        # Both tests are passed so key is in the upper octave with
        # note index and octave index preset

        # Determine key colour
        if note_op:
            note_colour = "red"
        else:
            if octave_select == 1:
                if note_index in self._sharp_index:
                    note_colour = "gray30"
                else:
                    note_colour = "gray90"
            else:
                if note_index % 2 == 0:
                    note_colour = "gray90"
                else:
                    note_colour = "gray30"

        # Change Colour according to operation
        self._key_canvas.itemconfig(self._key_refs[octave_select][note_index],
                                    fill=note_colour)

    def control_change(self, prefix, data):
        # Handle for events of control change messages being received
        if prefix == 1:
            # Octave Shift (UP or Down)
            if data == "0011":
                print("OS UP")
                self._current_oct += 1
                self._label_access[0].config(
                    text=f'Octave:{self._current_oct}')
                print(self._current_oct)
            else:
                print("OS DOWN")
                self._current_oct -= 1
                self._label_access[0].config(
                    text=f'Octave:{self._current_oct}')
                print(self._current_oct)
        elif prefix == 2:
            # Tempo Change (Time value)
            # Calculate BMP
            ms_reading = self._info_data
            self._current_tempo = 60 / (int(self._info_data) / 1000)
            self._current_tempo = round(self._current_tempo, 2)
            self._label_access[1].config(
                text=f'Tempo: {self._current_tempo}BPM/{ms_reading}ms')
        elif prefix == 3:
            # Control Change
            bits = ["X", "Y", "Z"]
            accel_data = bytearray(self._info_data, 'utf-8')
            if accel_data[0] == 48:
                bits[0] = "-"
                print("X OFF")
            if accel_data[1] == 48:
                bits[1] = "-"
            if accel_data[2] == 48:
                bits[2] = "-"
                print("Z OFF")
            # Display accelerometer data onto label
            print(f'{bits[0]}, {bits[1]}, {bits[2]}')
            self._label_access[6].config(
                text=f'Accel: {bits[0]}/{bits[1]}/{bits[2]}')

        elif prefix == 4:
            # ARP Multiplier (double or half current value)
            if self._info_data == "1100":
                # Double the current multiplier
                if self._current_arp < 16:
                    self._current_arp *= 2
                    self._label_access[2].config(
                        text=f'ARP Multiplier: {self._current_arp}')
            else:
                # Half the current multiplier
                if self._current_arp != 0.25:
                    self._current_arp = self._current_arp / 2
                    self._label_access[2].config(
                        text=f'ARP Multiplier: {self._current_arp}')

        elif prefix == 5:
            # Mode select
            if data == "1100":
                self._label_access[3].config(text="Keypress Mode: Normal")
            else:
                self._label_access[3].config(text="Keypress Mode: ARP")
        elif prefix == 6:
            # Volume set
            self._label_access[4].config(
                text=f'Vol: {(self._info_note * 10)}%')

        elif prefix == 7:
            # Waveform select
            wave_index = self._info_note
            print(wave_index)
            if self._info_note < 7:
                self._label_access[5].config(
                    text=f'Waveform: {self._waveforms[wave_index]}')
        else:
            self._info_received = ""

    def thread_shutdown(self):
        # Handler for thread closer, with any relevant error messages shown
        self._thread_com.close()
        app.com_enableBtn.config(bg="tomato")
        messagebox.showerror("ReceiverThread Exited",
                             f'{self.thread_name} exited: {self._exit_message}')


# ____________________________________________________________________________________________________________
# CSV Commands Class


class CSV(tk.Frame):
    """"A class developed for accessing scales.csv and displaying
    the material to the gui, creating a scale lock for the MIDI
    Original code found in CSV Testfile.py in GIT Repo
    """

    def __init__(self, parent, serial_port):
        """Initialise the widget with Frame class tools + additional methods"""
        super().__init__(parent)

        self._port_connection = serial_port

        # Set file path to the scales document
        self._scale_filePath = "C:/Users/Mitchell Crawford/Google Drive/Uni " \
                               "Work/Third Year/ENGG2800/Project/scales.csv"

        # Set variables for use throughout the class
        self._scales_file = open(self._scale_filePath, "r")
        self._scales_read = csv.reader(self._scales_file)
        self._scales_data = list(self._scales_read)
        self._scales_selection = self._scales_data[156]
        self._scaleListSelect = None

        # Variables to store listed elements
        self._scales_names = []
        self._scales_options = [11]

        # Read all scale names
        # Picking rows from files to show each scale once in the list
        for x in range(0, len(self._scales_data), 12):
            self._scales_names.append(self._scales_data[x][0])

        # Make Frames for neat packing of widgets
        self._ScalesFrame = tk.Frame(parent)
        self._ScalesFrame.pack(side=tk.RIGHT, padx=20)
        self._listboxFrame = tk.Frame(self._ScalesFrame)
        self._listboxFrame.pack(side=tk.TOP)
        self._listBtnFrame = tk.Frame(self._ScalesFrame)
        self._listBtnFrame.pack(side=tk.BOTTOM)

        # Creation of widget elements (labels, buttons, listboxes, etc)
        # Scale lock label
        self._scaleLockLbl = tk.Label(self._listBtnFrame, padx=5, pady=5,
                                      width=70,
                                      relief=tk.SUNKEN,
                                      text=f"{self._scales_selection}")
        self._locklblstatic = tk.Label(self._listBtnFrame, padx=5, pady=5,
                                       width=20, text="Scale Lock is:")
        # Scroll Bar
        scrollbar = tk.Scrollbar(self._listboxFrame, orient=tk.VERTICAL)
        # List boxes
        self._scalesListbox = tk.Listbox(self._listboxFrame, bg='ghost white',
                                         bd=4, height=10, cursor='arrow',
                                         relief=tk.SUNKEN,
                                         selectmode=tk.SINGLE,
                                         yscrollcommand=scrollbar.set)

        self._optionsListbox = tk.Listbox(self._listboxFrame,
                                          bg='lemon chiffon', bd=4,
                                          height=10, cursor='target',
                                          relief=tk.RIDGE,
                                          selectmode=tk.SINGLE,
                                          yscrollcomman=scrollbar.set,
                                          width=45)

        # Buttons to confirm selections and update lists
        self._listSelect = tk.Button(self._listBtnFrame, relief=tk.GROOVE,
                                     text='View', command=self.scale_selection)
        self._ScaleLockBtn = tk.Button(self._listBtnFrame, relief=tk.GROOVE,
                                       text='View')
        self._ScaleSelect = tk.Button(self._listBtnFrame, relief=tk.GROOVE,
                                      text='Select',
                                      command=self.set_scalelock)

        # Packing into respective frames
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._locklblstatic.pack(pady=10)
        self._scaleLockLbl.pack(padx=10)
        self._listSelect.pack(side=tk.LEFT, pady=5, padx=50)
        self._ScaleSelect.pack(side=tk.RIGHT, pady=5, padx=100)
        self._scalesListbox.pack(side=tk.LEFT, pady=10, padx=15)
        self._optionsListbox.pack(side=tk.LEFT, pady=10, padx=15)
        scrollbar.config(command=self._scalesListbox.yview)

        # For each iteration of x, insert each name once
        for x, y in enumerate(self._scales_names):
            self._scalesListbox.insert(x, y)

    def scale_selection(self):
        # Allows the user to see relevant scales to first selection
        self._scaleListSelect = (self._scalesListbox.curselection())[0]
        self.scales_options(self._scaleListSelect)

    def scales_options(self, selection):
        # Based on the scale chosen, find the row number in the CSV and
        # show all relevant scales

        # Clear scales options list first
        self._scales_options = []

        # Track position in scales options list
        counter = 0
        csv_step = selection * 12

        # Append list section into options list
        for x in range(csv_step, (csv_step + 12), 1):
            self._scales_options.append(
                self._scales_data[x][1:(len(self._scales_data[x]))])
            counter += 1

        # Insert options list to the listbox
        for x, y in enumerate(self._scales_options):
            self._optionsListbox.insert(x, y)

    def set_scalelock(self):
        # Sets the scale lock chosen by the user
        note_select = (self._optionsListbox.curselection())[0]
        scale_arr_num = ((self._scaleListSelect * 12) + note_select)
        self._scales_selection = self._scales_data[scale_arr_num]
        # Alter the text label showing this selection
        self._scaleLockLbl.config(text=f"Scale Lock: {self._scales_selection}")
        # Write the scale lock chosen to the serial port
        try:
            message = ','.join(str(e) for e in self._scales_selection[1:len(
                self._scales_selection)]) + '\r\n'
            self._port_connection.write(message.encode('ascii'))

        except ser.SerialException:
            # Raise serial exception error
            messagebox.showerror("Serial Exception Error",
                                 f'An error occurred when writing to port {self._port_connection.port}')


# _______________________________________________________________________________________________________________
# MIDI Application Class


class MidiGui(object):
    """A Gui application for running the MIDI keyboard"""

    def __init__(self, master):
        # Establish master window and settings
        self._master = master
        master.title("ENGG2800 S1 MIDI GUI -- Team 14")
        master.minsize(1100, 500)

        # Establish key variables
        self._key_refs = [["F", "F#", "G", "G#", "A", "A#", "B"],
                          ["C", "C#", "D", "D#", "E", "F",
                           "F#", "G", "G#", "A", "A#", "B"],
                          ["C", "C#", "D", "D#", "E"]]

        # Frames used as general packing regions
        upper_frame = tk.Frame(master, padx=50, pady=30, bg='light grey',
                               bd=10, relief=tk.RIDGE)
        upper_frame.pack(side=tk.TOP)

        lower_frame = tk.Frame(master, padx=5, pady=5, bg='black')
        lower_frame.pack(side=tk.BOTTOM)

        # Make frame to pack both keyboards into for layout purposes
        self._keyboardFrame = tk.Frame(lower_frame, bg='dark grey', width=1100)
        self._keyboardFrame.pack(side=tk.BOTTOM)

        # Make canvas space for keys to be shown in the gui
        self._key_canvas = tk.Canvas(self._keyboardFrame, width=965,
                                     height=300, bg='dark grey')
        self._key_canvas.pack(side=tk.RIGHT)

        # Frame used to pack all relevant text labels shown on screen
        text_frame = tk.Frame(upper_frame, bg='light grey')

        # Create text labels for showing control states
        self._octaveLbl = tk.Label(text_frame, text=f"Octave:3",
                                   relief=tk.RIDGE, width=20)
        self._octaveLbl.pack(pady=5, fill=tk.X)
        self._tempoLbl = tk.Label(text_frame, text=f"Tempo: -BPM/ -ms",
                                  relief=tk.RIDGE, width=20)
        self._tempoLbl.pack(pady=5, fill=tk.X)
        self._keyModeLbl = tk.Label(text_frame, text=f"Keypress Mode: Normal",
                                    relief=tk.RIDGE, width=20)
        self._keyModeLbl.pack(pady=5, fill=tk.X)
        self._arpMultiLbl = tk.Label(text_frame, text=f"ARP Multiplier: 1.0",
                                     relief=tk.RIDGE, width=20)
        self._arpMultiLbl.pack(pady=5, fill=tk.X)
        self._volume_lbl = tk.Label(text_frame, text=f'Vol: 50%',
                                    relief=tk.RIDGE)
        self._volume_lbl.pack(pady=5, fill=tk.X)
        self._waveform_lbl = tk.Label(text_frame, text=f'Waveform: Triangle',
                                      relief=tk.RIDGE)
        self._waveform_lbl.pack(pady=5, fill=tk.X)
        self._accel_outputs = tk.Label(text_frame, text="Accel: X/Y/Z",
                                       relief=tk.RIDGE)
        self._accel_outputs.pack(pady=5, fill=tk.X)
        # Array used to bundle label objects together for passing into thread
        self._effect_labels = [self._octaveLbl, self._tempoLbl,
                               self._arpMultiLbl,
                               self._keyModeLbl, self._volume_lbl,
                               self._waveform_lbl, self._accel_outputs]

        # Establish port connection variable (inactive)
        self._port_connection = ser.Serial(
            port=None,
            baudrate=38400,
            parity=ser.PARITY_NONE,
            stopbits=ser.STOPBITS_TWO,
            timeout=0.5
        )

        serial_window = tk.Frame(upper_frame, bg='light grey', padx=10)

        self._com_lbl = tk.Label(serial_window, text='Current Port:',
                                 relief=tk.RIDGE)
        self._com_lbl.grid(column=0, row=0, padx=10, pady=10)

        # Text Entries for setting serial variables
        self._port_input = tk.Entry(serial_window, bg='light grey', width=10)
        self._port_input.grid(column=1, row=0, padx=5, pady=10)

        # Button for enabling com port and opening communications
        self._com_state = False
        self.com_enableBtn = tk.Button(serial_window, text='Enable Com',
                                       bg='tomato',
                                       command=self._togglecom_btn)
        self.com_enableBtn.grid(column=0, row=1, padx=10, pady=10)

        # Receiver activity status
        self._receiver_activity = tk.Label(serial_window,
                                           text="Receiver: Disabled",
                                           relief=tk.RIDGE)
        self._receiver_activity.grid(column=0, row=2, padx=10, pady=10)

        # Inheriting required classes for use
        # Inherit CSV class to variable for access
        serial_window.pack(side=tk.LEFT)
        text_frame.pack(side=tk.RIGHT)
        self._csv = CSV(upper_frame, self._port_connection)
        self._csv.config(bg='red', padx=20)

        # Establish thread class instance and pass com port for messages
        # Reboot variable used to signal first thread start or not
        self._receiver_reboot = False
        self._receiver_thread = ThreadCreate("Receiver", self._port_connection,
                                             self._effect_labels,
                                             self._key_refs, self._key_canvas)

        # Pack serial, effect labels and csv into frame



        # Establish master window drop down menus
        # Menu bar variable to store all future menus
        menu_bar = tk.Menu(master)
        master.config(menu=menu_bar)

        #   File menu for exit and commands
        gui_menu = tk.Menu(menu_bar)
        menu_bar.add_cascade(label='GUI', menu=gui_menu)
        gui_menu.add_command(label='Exit', command=self.exit_clicked)

        # Creating Keyboard using key variables
        # Reference keyboard canvas through self._key_canvas variable
        self.create_keys(self._key_refs, self._key_canvas)

    def create_keys(self, octave, canvas):
        # Generates the keyboard object on the canvas for the keys array
        key_position = 0
        key_width = 70
        sharp_y = 200
        single_y = 300

        for i in range(3):
            num_refs = len(octave[i])
            for x in range(num_refs):

                if "#" in octave[i][x]:
                    # Sharp keys
                    octave[i][x] = canvas.create_rectangle((key_position - 35),
                                                           0,
                                                           (key_position + 35),
                                                           sharp_y,
                                                           fill='gray30')
                else:
                    # Letter Keys
                    octave[i][x] = canvas.create_rectangle(
                        key_position, 0, (key_position + key_width),
                        single_y, fill='gray90')
                    key_position += key_width
        return

    def _togglecom_btn(self):
        """Toggle the Com button and settings"""
        # Update for current COM state and port given
        self._com_state = self._port_connection.isOpen()
        com_input = self._port_input.get()

        if "com" not in com_input.lower():
            # If com is not in the input then input invalid and ignored
            return

        # Operate according to known COM state
        if self._com_state:
            # COM port is currently enabled and must be disabled
            # Note: receiver thread must be disabled to stop error occurring
            self.com_enableBtn.config(text='Com Disabled', bg='tomato')
            self._receiver_activity.config(text="Receiver: Disabled")
            self._receiver_thread._exit_flag = True
            self._port_connection.close()

        else:
            # COM port is disabled and must be booted
            self.com_enableBtn.config(text='Com Active', bg="green3")
            self._receiver_activity.config(text="Receiver: Active")
            self._port_connection.port = com_input
            self._port_connection.open()
            if not self._receiver_reboot:
                self._receiver_thread.start()
                self._receiver_reboot = True
            else:
                self._receiver_thread.run()

    def exit_clicked(self):
        """Close the application after running shutdown protocols
                    To be shutdown:
                    - Serial COM Port
                    - Threads running
                    - GUI application (tkinter)
        """
        self._port_connection.close()
        self._master.destroy()


# ______________________________________________________________________________________________________________
# Boot for TkInter when top level main is run

if __name__ == "__main__":
    root = tk.Tk()
    app = MidiGui(root)
    root.mainloop()

# ______________________________________________________________________________________________________________
