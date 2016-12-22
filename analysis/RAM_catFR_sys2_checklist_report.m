function RAM_catFR_sys2_checklist_report( events )
%CHECKLIST_REPORT Summary of this function goes here
%   Detailed explanation goes here

%% 12 word lists
WORD_events = events(strcmp({events.type},'WORD'));
[subjEvents, ~] = splitEventsBy(WORD_events, 'subject');
listLength = [];
for s = 1:length(subjEvents)
    this_subjEvents = subjEvents{s};
    sessionEvents = splitEventsBy(this_subjEvents, 'session');
    for se = 1:length(sessionEvents)
        this_sessEvents = sessionEvents{se};
        listEvents = splitEventsBy(this_sessEvents, 'list');
        for l = 1:length(listEvents)
            this_listEvents = listEvents{l};
            listLength = [listLength length(this_listEvents)];
        end
    end
end
fprintf(['****** LIST LENGTH *******' stats(listLength)]);

%% 25 lists per session 

WORD_events = events(strcmp({events.type},'WORD'));
[subjEvents, ~] = splitEventsBy(WORD_events, 'subject');
nLists = [];
for s = 1:length(subjEvents)
    this_subjEvents = subjEvents{s};
    un_sessions = unique([this_subjEvents.session]);
    for se = 1:length(sessionEvents)
        this_sess_events = sessionEvents{se};
        nLists = [nLists length(unique([this_sess_events.list]))];
    end
end
fprintf(['****** 25 lists per session *******' stats(nLists)]);

%% 10 second countdown
COUNTDOWN_START_events = events(strcmp({events.type},'COUNTDOWN_START'));
COUNTDOWN_END_events = events(strcmp({events.type}, 'COUNTDOWN_END'));

countdown_length = [COUNTDOWN_END_events.mstime] - [COUNTDOWN_START_events.mstime];

fprintf(['****** 10 second countdown (ms) *******' stats(countdown_length)]);

%% UNIQUE WORDS PER SESSION
WORD_events = events(strcmp({events.type},'WORD'));
subjEvents = splitEventsBy(WORD_events, 'subject');
numUniqueWords = [];
for subj_i = 1:length(subjEvents)
    this_subjEvents = subjEvents{subj_i};
    sessEvents = splitEventsBy(this_subjEvents, 'session');
    for sess_i = 1:length(sessEvents)
        numUniqueWords(end+1) = length(unique({sessEvents{sess_i}.item}));
    end
end
   
fprintf(['******* 300 UNIQUE WORDS PER SESSION *******',stats(numUniqueWords)]);     


%% 1600+750 to 1000 (2350-2600) between word presentations
WORD_events_mask = strcmp({events.type},'WORD');
delays =[];
for i=find(WORD_events_mask)
    if strcmp(events(i+2).type,'WORD')
        delays(end+1) = events(i+2).mstime - events(i).mstime;
    end
end

fprintf(['******* 2350-2600ms BETWEEN WORDS *******',stats(delays)]);

%% 20(+) second distractor
DISTRACT_events = events(strcmp({events.type},'DISTRACT_START') | strcmp({events.type},'DISTRACT_END'));
delays = [];
for i=1:length(DISTRACT_events)
    if strcmp({DISTRACT_events(i).type},'DISTRACT_START') && ...
            strcmp({DISTRACT_events(i+1).type},'DISTRACT_END')
        delays(end+1) = DISTRACT_events(i+1).mstime - DISTRACT_events(i).mstime;
    end
end
fprintf(['******* 20+ SECOOND DISTRACTOR TIME (ms) *******',stats(delays)]);

%% 30s retrieval
REC_events = events(strcmp({events.type},'REC_START') | strcmp({events.type},'REC_END'));
delays = [];
for i=1:length(REC_events)
    if strcmp({REC_events(i).type},'REC_START') && ...
            strcmp({REC_events(i+1).type},'REC_END')
        delays(end+1) = REC_events(i+1).mstime - REC_events(i).mstime;
    end
end
fprintf(['******* 30 SECOND RECALL TIME (ms) *******',stats(delays)]);
        

%% STIM LISTS INTERLEAVED
TRIAL_events = events(strcmp({events.type},'TRIAL'));
stimLists = [TRIAL_events.stimList];
bySession = reshape(stimLists, 25, [])';

fprintf('****** STIM LISTS INTERLEAVED? *******\n');
disp(bySession);

%% CATEGORY PAIRINGS NOT REPEATED WITHIN TWO SESSIONS
WORD_events = events(strcmp({events.type}, 'WORD'));
unique_sessions = unique([WORD_events.session]);
unique_categories = unique([WORD_events.categoryNum]);
pairings = zeros(length(unique_categories));
for sess_i = 1:length(unique_sessions)
    sess_events = WORD_events([WORD_events.session]==unique_sessions(sess_i));
    unique_lists = unique([sess_events.list]);
    for list_i = 1:length(unique_lists)
        list_cats = unique([sess_events([sess_events.list]==unique_lists(list_i)).categoryNum]);
        for cat1 = list_cats
            for cat2 = list_cats(list_cats~=cat1)
                pairings(cat1+1, cat2+1) = pairings(cat1+1, cat2+1)+1;
            end
        end
    end
end

fprintf('****** Maximum category pairings ****** \n\t%d\n', max(pairings(:)));
    
function strstats = stats(list)
strstats = sprintf('\n\tMEAN:%.1f\n\tMIN:%d\n\tMAX:%d\n',...
    nanmean(list(~isnan(list))),...
    min(list(~isnan(list))),...
    max(list(~isnan(list))));