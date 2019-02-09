

local time = os.datetable()

if (event.type == 'interrupt' and event.iid == 'update') or
   ((event.type == 'on' or event.type == 'off') and event.pin == '%activation-pin%') then

   port.%output-port% = pin.%activation-pin% and mem.activations[%input%]
else
    mem.activations = {%activations%}
end

interrupt(%interval%, 'update')
