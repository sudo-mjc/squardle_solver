"""
This is a file for the development of pyserial and threading code, aimed for
future implementation in the GUI of the ENGG2800 project

Author: Mitchell Crawford
ENGG2800, Sem1, 2021

"""
import time
import tkinter as tk
from tkinter import messagebox
import threading
import serial as ser


class TestWin(object):
    """ A class for establishing two way communication between serial ports
    whilst embedded in a GUI window, running off the TKinter module
    """
    def __init__(self, master):
        self._master = master
        master.title("Serial Coms Control")
        master.minsize(500, 200)

        # TKinter GUI tools
        # Received Texts
        self._receivedText = tk.Label(master, text="No Current Info", relief=tk.SUNKEN, width=50)

        # Send Texts
        self._send_packing = tk.Frame(master, padx=10, pady=10)
        self._message_text = tk.Entry(self._send_packing, bg="light grey", width=50)
        self._send_message = tk.Button(self._send_packing, text='Send Text', command=self.message_send)

        # GUI packing
        self._receivedText.pack(side=tk.TOP, pady=20)
        self._send_message.pack(side=tk.LEFT, padx=10)
        self._message_text.pack(side=tk.LEFT)
        self._send_packing.pack(side=tk.TOP)

        # Establish class variables
        self._message_entered = ""
        self._com_port = 'COM3'

        # Open Com port
        self._com_connect = ser.Serial(
            port=self._com_port,
            baudrate=4800,
            parity=ser.PARITY_NONE,
            stopbits=ser.STOPBITS_ONE,
            timeout=0.5
        )

        if self._com_connect.isOpen():
            # If returns true then notify the user that com connection is established
            print(">> Connection Open <<")

        else:
            # Connection is not open and program must exit
            print(">> Connection Error <<")
            messagebox.showerror("Connection Error", f'An error occurred when opening {self._com_port}')
            self._master.destroy()

        # initiate thread
        com_thread = EstThread(1, "receive", self._com_connect,
                               self._receivedText, self._master)
        com_thread.start()

    def message_send(self):
        # Sends the text over the provided serial port
        self._message_entered = self._message_text.get()

        try:
            self._com_connect.write((self._message_entered + '\r\n').encode('ascii'))
            self._message_text.delete(0, len(self._message_entered))

        except ser.SerialException:
            messagebox.showerror("Failed to write", f'Text failed to send via {self._com_connect.port}')
# __________________________________________________________________________________________


class EstThread (threading.Thread):
    """
    Class to establish parallel thread to run serial read direct this to the main
    GUI class
    """
    def __init__(self, threadID, name, com_port, text_display, master_window):
        threading.Thread.__init__(self, daemon=True)
        self._threadID = threadID
        self._thread_name = name
        self._com_port = com_port
        self._text_display = text_display
        self._master = master_window

        # General variables
        self._info_received = ''
        self._info_prefix = ''
        self._info_data = ''
        self._exitFlag = 0

    def run(self):
        print(f'Thread {self._thread_name} beginning')
        while not self._exitFlag:

            # Check for waiting bits in the buffer
            waiting_bits = self._com_port.inWaiting()

            if waiting_bits != 0:
                self._info_received = self._com_port.read(waiting_bits).strip().decode('utf-8')

                if self._info_received == 'exit':
                    print("Matched")
                    self._exitFlag = 1
                else:
                    self._info_prefix = int(self._info_received[0:1])
                    self._info_data = self._info_received[2:6]
                    self._info_note = self._info_received[3:6]
                    self._text_display.config(text=f'{self._info_received}, {self._info_data}, {self._info_prefix}')

                if self._info_prefix < 8:
                    # Control Change
                    self.control_change(self._info_prefix, self._info_data)

                else:
                    # Note Control
                    if self._info_prefix == 9:
                        # Note On
                        print(self._info_note)

                    elif self._info_prefix == 0:
                        # Note Off
                        print(self._info_note)

            time.sleep(0.1)
            # Check if the com port has been lost
            self.check_port()

        print(f'Thread {self._thread_name} exiting')
        self._master.destroy()

    def control_change(self, prefix, data):
        # Used to determine appropriate changes to labels
        if prefix == 1:
            # Octave Shift (UP or Down)
            if data == "00XX":
                print("OS UP")
            else:
                print("OS DOWN")
        elif prefix == 2:
            # Tempo Change (Time value)
            print(data)
        elif prefix == 3:
            # Control Change
            print(data)
        elif prefix == 3:
            # ARP Multiplier
            print(data)
        elif prefix == 5:
            # Mode select
            if data == "XX00":
                print("NORMAL MODE")
            else:
                print("ARP MODE")

    def check_port(self):
        # Checks the current state of the COM port
        if not self._com_port.isOpen():
            messagebox.showerror("Connection Error", "The connection was lost!")
            self._exitFlag = True


# TKinter Boot_____________________________________________________________________________

if __name__ == "__main__":
    root = tk.Tk()
    app = TestWin(root)
    root.mainloop()
