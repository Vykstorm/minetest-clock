

local time = os.datetable()

if (event.type == 'interrupt' and event.iid == 'update') or
   ((event.type == 'on' or event.type == 'off') and event.pin == '%activation-pin%') then

   port.%output-port% = pin.%activation-pin% and mem.activations[%input%]
   interrupt(%interval%, 'update')

elseif event.type == 'program' then
    mem.activations = {%activations%}
    interrupt(1, 'update')
end
