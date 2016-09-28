import logging
import argparse
import struct
import binascii
import sys
import os.path
import serial
import time
class Programmer:
    def __init__(self,conn,opts):
        self.conn = conn
        self.size = opts.size
        self.offset = opts.offset
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
        else:   print "The device is not available!"
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
        
def main():
    ##############################collect parameters##############################
    #set the default port according to system
    if sys.platform == 'win32':
        port = "COM3"
    else:
        port = "/dev/ttyUSB0"

    parser = argparse.ArgumentParser(
        description = ("A commnd line flash programmer for"
                       +"EK-TM4C1294XL LaunchPad\n"
                       +"https://github.com/miyunluo"))
    #the binary file or hex file
    parser.add_argument("image",help="code image(bin/hex)",
                        type = argparse.FileType("rb"),nargs='?')
    #port number
    parser.add_argument("-p","--port",
                        help = "serial port number(default:%s)"%port,
                        default = port)
    #transfer size
    parser.add_argument("-s","--size",
                        help = "transfer size int one package(default:8,max:68)",
                        default = 8)
    #address offset
    parser.add_argument("-o","--offset",
                        help = "program address offset(default:0x000000)",
                        type=lambda x: int(x,0),
                        default = 0x0)
    #ping
    parser.add_argument("-t","--test",
                        help = "test if the device is available",
                        action = "store_true")
    #debug
    parser.add_argument("-d","--debug",
                        help = "debug mode",
                        action="store_true")
    opts = parser.parse_args()

    ##############################do with those args##############################
    if(opts.debug):
        opts.loglevel = logging.DEBUG
    else:
        opts.loglevel = logging.CRITICAL
    opts.size = min(opts.size,68)
    logging.basicConfig(format=("%(levelname)s:"
                                +"[%(relativeCreated)d]"
                                +"%(message)s"),
                        level = opts.loglevel)
    ##############################start to connect##############################
    print("Try to connect to %s at baudrate 115200(stable)"%opts.port)
    try:
        with serial.Serial(port = opts.port,
                           baudrate = 115200,
                           timeout = 1) as conn:
            program = Programmer(conn,opts)
            if opts.test:
                program.ping()
            if opts.image!=None:
                program.download()
                opts.image.close()
                print "Download completed!"
        conn.close()
    except:
        print "Device is not connected successfully."

if __name__ == "__main__":
    main()
    
