import logging
import argparse
import struct
import binascii
import sys
import os.path
import serial
import time
from Tkinter import *
import tkFileDialog
class Programmer:
    def __init__(self,conn,opts):
        self.conn = conn
        self.size = opts.size
        self.offset = opts.offset
        #print self.offset
        if opts.image:
            self.code = bytearray(opts.image.read())
            if os.path.splitext(opts.image.name)[1] in (".hex",".ihx"):
                code = self.hex2bin()
        else:   self.code = None
    def read(self,num):
        result = bytearray(self.conn.read(num))
        logging.debug("receive: " + " ".join(["%02X" % i for i in result]))
        return result
    def write(self,string):
        logging.debug("write: " + " ".join(["%02X" % i for i in string]))
        self.conn.write(string)
    def send(self,string):
        string = string.split()
        for i in range(len(string)):
            string[i] = binascii.a2b_hex(string[i])
        self.write(bytearray(string))
    def ping(self):
        self.send('03 20 20')
        if self.read(2)=='\x00\xcc':    print "The device is ready!"
        else:
            print "The device is not available!"
            raise Exception("The device is not available!")
    def test(self):
        self.send('03 23 23')
        self.read(5)
    def reset(self):
        self.send('cc 03 25 25')
        self.read(2)
    def packet(self,command):
        check_sum = sum(command) % 0x100
        self.write(bytearray('\xcc'))
        self.write(bytearray(struct.pack('<H',len(command)+2)[0]))
        self.write(bytearray(struct.pack('<H',check_sum)[0]))
        self.write(command)
        self.read(2)
        self.test()
    def download(self):
        data = self.code
        if(self.offset==0x0):
            self.send('55 55')
            self.read(2)
        self.ping()
        self.test()
        self.packet('\x21'+bytearray(struct.pack('<LL',len(data),self.offset)[::-1]))
        while(len(data)!=0):
            length = min(self.size,len(data))
            self.packet('\x24'+data[:length])
            data = data[length:]
        self.reset()
    def hex2bin(self):
        result = bytearray()
        for rec in self.code.splitlines():
            hexstr = str(rec)
            hexstr = hexstr.strip()
            size = int(hexstr[1:3],16)
            if int(hexstr[7:9],16) != 0:
                continue    
            for h in range( 0, size):
                b = int(hexstr[9+h*2:9+h*2+2],16)
                result += struct.pack('B',b)
        self.code = bytearray(result)
        



class Opts:
    def __init__(self,size,image,offset,port):
        self.size = min(size,68)
        self.image = open(image,'rb')
        self.offset = 0
        times = 0
        while(offset!=0):
            tmp = offset%10
            for i in range(times):
                tmp = tmp*16
            self.offset = self.offset + tmp
            offset = offset/10
            times += 1
        self.port = port
        self.loglevel = logging.CRITICAL
        logging.basicConfig(format=("%(levelname)s:"
                                +"[%(relativeCreated)d]"
                                +"%(message)s"),
                        level = self.loglevel)

def main2():
    root = Tk()
    root.title("easyFlash GUI v2.1")
    root.geometry("300x167")
    port = StringVar()
    image = StringVar()
    offset = IntVar()
    size = IntVar()
    
    def program():
        opts = Opts(size.get(),image.get(),offset.get(),port.get())
        try:
            with serial.Serial(port = port.get(),
                               baudrate = 115200,
                               timeout = 1) as conn:
                program = Programmer(conn,opts)
                if cmp(image.get(),"")!=0:
                    program.download()
                    opts.image.close()
                    print "Download completed!"
            conn.close()
        except:
            print "Device is not connected successfully."
    def browse():
        image.set(tkFileDialog.askopenfilename(parent=root,title='Pick a directory'))
    Label(root,text="Port Number:").place(x=10,y=5)
    OptionMenu(root, port, "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9", "COM10", "COM11", "COM12", "COM13", "COM14", "COM15", "COM16", "COM17", "COM18", "COM19", "COM20").place(x=215,y=0)
    Label(root,text="Image Location:").place(x=10,y=35)
    Entry(root,textvariable = image,width=35).place(x=10,y=55)
    Button(root,text="Browse",command=browse).place(x=240,y=50)
    Label(root,text="Program Address Offset:  0x").place(x=10,y=90)
    Entry(root,textvariable = offset,width=10).place(x=160,y=90)
    Label(root,text="Transfer Size:").place(x=10,y=110)
    Entry(root,textvariable = size).place(x=100,y=110)
    Button(root,text="Program",command = program).place(x=235,y=135)

    port.set("COM3")
    offset.set(0)
    size.set(8)

    root.mainloop()
    
if __name__ == "__main__":
    main2()
    
