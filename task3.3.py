from machine import Pin
import time

# ===== IMPORT YOUR CLASSES =====
from fifo import Fifo
from filefifo import Filefifo

# ===== CONFIG =====
WINDOW = 128
DATA_SIZE = 1000

# ===== LOAD DATA FROM FILE =====
ff = Filefifo(DATA_SIZE, name="data.txt")

data = []
for _ in range(DATA_SIZE):
    data.append(ff.get())

# ===== MIN / MAX =====
min_val = min(data)
max_val = max(data)

print("Data loaded")
print("Min:", min_val, "Max:", max_val)

# ===== FIFO FOR ENCODER EVENTS =====
fifo = Fifo(32)

# ===== ROTARY ENCODER SETUP =====
pin_clk = Pin(14, Pin.IN, Pin.PULL_UP)
pin_dt  = Pin(15, Pin.IN, Pin.PULL_UP)

last_clk = pin_clk.value()

# ===== INTERRUPT HANDLER =====
def encoder_isr(pin):
    global last_clk
    clk = pin_clk.value()
    
    if clk != last_clk:  # detect edge,seems to be better than comparing to 0 or 1
        if pin_dt.value() != clk:
            direction = +1   # clockwise
        else:
            direction = -1   # counterclockwise
        
        try:
            fifo.put(direction)
        except:
            pass  # ignore overflow
    
    last_clk = clk

# attach interrupt
pin_clk.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=encoder_isr)

# ===== SCROLLING LOGIC =====
index = 0

def display_window(idx):
    window = data[idx:idx+WINDOW]
    
    # simple text output (replace with OLED later)
    print("\nIndex:", idx)
    print(window[:8], "...", window[-8:])  # shortened view

# initial display
display_window(index)

# ===== MAIN LOOP =====
while True:
    if fifo.has_data():
        step = fifo.get()
        
        index += step
        
        # clamp bounds
        if index < 0:
            index = 0
        elif index > DATA_SIZE - WINDOW:
            index = DATA_SIZE - WINDOW
        
        display_window(index)
    
    time.sleep_ms(10)