import machine
import onewire
import ds18x20
import time
import ujson
from machine import Pin
from picographics import PicoGraphics, DISPLAY_TUFTY_2040
from pimoroni import Button
import os

# setup probe

ds_pin = machine.Pin(4)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
time.sleep(1)
roms = ds_sensor.scan()
print('Found DS devices: ', roms)

# setup onboard LED

led = Pin(25, Pin.OUT)


# define button

button_b = Button(8, invert=False)



# setup display

display = PicoGraphics(display=DISPLAY_TUFTY_2040)

WIDTH, HEIGHT = display.get_bounds()
display.set_backlight(1)
display.update()


# define colours

WHITE = display.create_pen(255, 255, 255)
BLACK = display.create_pen(0, 0, 0)
RED = display.create_pen(255, 0, 0)

# start temp probe

ds_sensor.convert_temp()
time.sleep(0.8)
temperature = ds_sensor.read_temp(roms[0])

# open data file load saved max and min temp values or create data.txt file if not present

led.value(1)
if 'data.txt' in os.listdir():
    file = open('data.txt', 'r')
    data = ujson.load(file)
else: 
    file = open('data.txt', 'w')
    data = {'max_temp': temperature, 'min_temp': temperature}
    file.write(ujson.dumps(data))
file.close()
led.value(0)



while True:
  ds_sensor.convert_temp()
  time.sleep(0.8)
  
  temperature = ds_sensor.read_temp(roms[0])
  print(temperature)
  
  # display temperature on screen
  
  display.set_pen(WHITE)
  display.clear()
  if temperature > 28:
      display.set_pen(RED)
  else:
      display.set_pen(BLACK)
  display.set_font("bitmap8")
  display.text(f"{temperature:.2f}°C", 30, int(HEIGHT/2 - 32), scale=8)
  display.set_pen(BLACK)
  display.text(f"Min {data['min_temp']:.2f}°C", 30, HEIGHT - 70, scale=3)
  display.text(f"Max {data['max_temp']:.2f}°C", 30, HEIGHT - 35, scale=3)
  
  # save Max/Min value if there any change.
  
  if temperature > data['max_temp']: data['max_temp'] = temperature
  if temperature < data['min_temp']: data['min_temp'] = temperature
  display.update()
  
  # button pressed? reset Max/Min value if held until refresh
  
  if button_b.is_pressed:
      data['max_temp'] = temperature
      data['min_temp'] = temperature
      
  # update data file
  
  led.value(1)
  file = open('data.txt', 'w')
  file.write(ujson.dumps(data))
  file.close()
  
  
  # flash LED
  
  led.value(1)
  time.sleep(1)
  led.value(0)
  time.sleep(3)
  
