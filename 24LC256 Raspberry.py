import smbus
import time

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
import serial

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import subprocess

# Raspberry Pi pin configuration:
RST = None     # on the PiOLED this pin isnt used
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Load default font.
font = ImageFont.load_default()

bus = smbus.SMBus(1) #creamos una variable bus a SMBus(1)
address = 0x50       #Direccion a la memoria en i2c

def MemoryWrite(targetAddress, data):
    bus.write_i2c_block_data(address,0x00,[targetAddress,data])
    time.sleep(0.01)

def MemoryRead(targetAddress):
    time.sleep(0.01)
    bus.write_i2c_block_data(address,0x00,[targetAddress])
    time.sleep(0.01)
    return bus.read_byte(address)

def esPrimo(num):
    if num > 1:
        for ite in range(2, int(num/2)+1):
            if (num % ite) == 0:
                return False
            else:
                return True
    else:
        return False

print("[NOTA] Tomar en cuenta que las primeras 20 localidades son de 0 a 19...")

#Guardamos los 20 datos
i,n = 0,20
while i < n:
   dataIn = input("Ingresa el numero " + str(i+1) + ": ")
   MemoryWrite(i,dataIn)
   i = i + 1

print("")
print("")

i,n,resP,resN,resPr,resM3 = 0,20,0x00,0x00,0x01,0x00

prcsP = ""
prcsN = ""
prcsPr = ""
prcsM3 = ""

while i < n:
    readVal = MemoryRead(i)

    #Sumar localidades pares y guardar en localidad 21
    if (i % 2) == 0:
        resP = resP + readVal
        prcsP = prcsP + str(readVal) + " + "
    #Restamos localidades nones y guardamos en localidad 22
    else:
        resN = resN - readVal
        prcsN = prcsN + str(readVal) + " - "

    #Multiplicamos las localidades primas y guardamos en localidad 23
    if esPrimo(i):
        resPr = resPr * readVal
        prcsPr = prcsPr + str(readVal) + " * "

    #Se elevan al cuadrado las localidades multiplo de 3 y se guardan en localidad 24
    if (i % 3) == 0:
        resM3 = resM3 + (readVal*readVal)
        prcsM3 = prcsM3 + str(readVal) + "^2 + "

    i = i + 1

prcsP = prcsP[:-2]
prcsN = prcsN[:-2]
prcsPr = prcsPr[:-2]
prcsM3 = prcsM3[:-2]


print("Localidades Pares (Sumadas): ")
print(str(prcsP) + " = " + str(resP))
print("")
print("Localidades Nones (Restadas): ")
print(str(prcsN) + " = " + str(resN))
print("")
print("Localidades Primas (Multiplicadas): ")
print(str(prcsPr) + " = " + str(resPr))
print("")
print("Localidades Multiplo de 3 (Elevadas al cuadrado): ")
print(str(prcsM3) + " = " + str(resM3))

MemoryWrite(21, resP)
MemoryWrite(22, resN)
MemoryWrite(23, resPr)
MemoryWrite(24, resM3)

#Escribir resultados en pantalla OLED
draw.text((x, top),       "Pares: " + str(MemoryRead(21)),   font=font, fill=255)
draw.text((x, top+8),     "Nones: " + str(MemoryRead(22)),   font=font, fill=255)
draw.text((x, top+16),    "Prims: " + str(MemoryRead(23)),   font=font, fill=255)
draw.text((x, top+25),    "Mult3: " + str(MemoryRead(24)),   font=font, fill=255)

disp.image(image)
disp.display()

print("Resultados mostrados en OLED...")
print("")
print("")

#Escribir nuevos valores en localidades 21-24
i = 21
while i <= 24:
    dataIn = input("Ingresa un numero para la localidad " + str(i) + ": ")
    MemoryWrite(i,dataIn)
    i = i + 1
print("")

#Limpiar display
draw.rectangle((0,0,width,height), outline=0, fill=0)

#imprimir resultado de localidades Pares + nuevos valores localidades 21-24
respNueva = resP + MemoryRead(21) + MemoryRead(22) + MemoryRead(23) + MemoryRead(24)

print("Resultado de suma final mostrado en OLED...")
draw.text((x, top),       "Suma Nueva: ",   font=font, fill=255)
draw.text((x, top+8),     str(respNueva),        font=font, fill=255)

disp.image(image)
disp.display()