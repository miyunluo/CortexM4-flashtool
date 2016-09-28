# CortexM4-flashtool
It is a easy python flash tool for TI TM4C1294

EasyFlash.py 为命令行烧录器

optional arguments:

-h, --help            show this help message and exit

-p PORT, --port PORT  serial port number(default:COM3)

-s SIZE, --size SIZE  transfer size int one package(default:8,max:68)

-o OFFSET, --offset 	OFFSET program address offset(default:0x000000)

-t, --test            test if the device is available

-d, --debug           debug mode
  
EasyFlashv2.1.py 为图形界面烧录器，使用时自主选择即可

注意：使用COM端通信需要先用官方烧录器擦除RAM
Notion: erase the RAM first. 
