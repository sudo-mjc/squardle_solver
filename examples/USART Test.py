"""
PySerial test script for reading information and sending returns to the AVR

Author: Mitchell Crawford
ENGG2800 Sem1, 2021
"""
import time
import tkinter as tk
from tkinter import messagebox
import serial as serial

class SerialCom(object):

    def __init__(self, master):

        self._master = master
        master.title("Serial Port Control")
        master.minsize(500, 200)

        self._receiveLbl = tk.Label(master, text="No Current Info", relief=tk.SUNKEN,
                                    width=50)
        self._sendInfo = tk.Frame(master, padx=10, pady=10)
        self._sendText = tk.Entry(self._sendInfo, bg='light grey', width=50)
        self._sendBtn = tk.Button(self._sendInfo, text='Send text',
                                  command=self.text_send)
        self._receiveBtn = tk.Button(master, text='Receive Text', command=self.text_read)
        self._sendBtn.pack(side=tk.LEFT, padx=20)
        self._sendText.pack(side=tk.RIGHT)
        self._receiveLbl.pack(side=tk.TOP, pady=10, padx=10)
        self._receiveBtn.pack(side=tk.TOP, pady=5)
        self._sendInfo.pack(side=tk.TOP)

        self._connection = serial.Serial(
            port='COM3',
            baudrate=9600,
            parity=serial.PARITY_ODD,
            stopbits=serial.STOPBITS_TWO,
            bytesize=serial.EIGHTBITS,
            timeout=0.5
        )

        if self._connection.isOpen():
            print(">> Connection is open <<")
            self._connection.flushInput()

        else:
            print(">> CONNECTION ERROR <<")
            messagebox.showerror("Connection Error", )
            self.close_app()

        root.after(1000, self.text_read())

    def text_send(self):
        data = self._sendText.get()
        try:
            self._connection.write((data + '\r\n').encode('ascii'))
            self._sendText.delete(0, len(self._sendText.get()))

        except serial.SerialException:
            messagebox.showerror("Invalid Error", "Text cannot be send!")

    def bounce_back(self):
        print("___LOOP___")
        root.after(1000, self.text_read())

    def text_read(self):
        waiting_bits = self._connection.inWaiting()
        if waiting_bits != 0:
            info_receive = self._connection.read(waiting_bits).decode('ascii')
            self._receiveLbl.config(text=f'{info_receive}')
            print(info_receive)

        else:
            root.update()
            root.after(1000, self.bounce_back())

    def close_app(self):
        self._connection.close()
        self._master.destroy()


# TkInter BOOT_____________________________________________________________________

if __name__ == "__main__":
    root = tk.Tk()
    app = SerialCom(root)
    root.mainloop()
