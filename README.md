## Minetest digital clock

If your aim is to build a digital clock in-game on a minetest game with mesecons and without digilines mod, you can do it only
using only lua micro-controllers


The next pictures shows the digital clock finished

![alt screenshot 1](images/screenshot2.png)
![alt screenshot 2](images/screenshot1.png)
![alt screenshot 3](images/screenshot3.png)
![alt screenshot 4](images/screenshot4.png)


## How to build it

The display have 4 digits (the clock shows the server time with hh-mm format). <br>
Each digit has 5x3 pixels (5 rows and 3 columns). <br>
Each of this individual pixels can be manipulated (turn on/off) by a micro-controller (depending on the digit it's going to display) <br>


All micro-controllers must be programmed with lua code. Here it's an example:

```lua
local time = os.datetable()

if (event.type == 'interrupt' and event.iid == 'update') or
   ((event.type == 'on' or event.type == 'off') and event.pin.name == 'C') then

   port.a = pin.c and mem.states[math.floor(time.hour / 10) + 1]
   
   interrupt(60 * (60 - time.min) + (60 - time.sec), 'update')

elseif event.type == 'program' then
    mem.states = {true, true, true, true, true, true, true, true, true, true}
    interrupt(1, 'update')
end
```
