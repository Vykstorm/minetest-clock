%header%

local time = os.datetable()

if (event.type == 'interrupt' and event.iid == 'update') or
   ((event.type == 'on' or event.type == 'off') and event.pin.name == '%ACTIVATION_PIN%') then

   {% if always_enabled %}
   port.%output_port% = mem.states[%input%]
   {% else %}
   port.%output_port% = pin.%activation_pin% and mem.states[%input%]
   {% end %}
   interrupt(%interval%, 'update')

elseif event.type == 'program' then
    mem.states = {%states%}
    interrupt(1, 'update')
end
