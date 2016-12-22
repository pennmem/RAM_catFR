function [ events_split, unique_values ] = splitEventsBy( events, field )
%SPLITBY Summary of this function goes here
%   Detailed explanation goes here
if ischar(events(1).(field))
    unique_values = unique({events.(field)});
else
    unique_values = unique([events.(field)]);
end
events_split = cell(size(unique_values));
for i=1:length(events)
    if iscell(unique_values)
        index = strcmp(unique_values,events(i).(field));
         events_split{index} = [events_split{index} events(i)];
    else
        index = unique_values==events(i).(field);
         events_split{index} = [events_split{index} events(i)];
    end
    
   

end

