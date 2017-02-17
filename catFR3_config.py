# THIS FILE SETS THE CONFIGURATIONS
# FOR FR IN SYSTEM 2.0

# ALL SYSTEM2.0 CONFIGURATION OPTIONS
experiment = 'catFR3'
stim_type = 'CLOSED_STIM'
version = '3.0.0'
control_pc = True
heartbeat_interval = 1000
category_states = ['CAT_%d' % i for i in range(25)]
state_list = [ 
    'PRACTICE',
    'STIM ENCODING',
    'NON-STIM ENCODING',
    'RETRIEVAL',
    'DISTRACT',
    'INSTRUCT',
    'COUNTDOWN',
    'WAITING',
    'WORD',
    'ORIENT',
    'MIC TEST',
 ] + category_states

require_labjack = False

do_stim = True

numSessions = 10

nStimTrials = 11
nBaselineTrials = 3
nControlTrials = 11

# %s will be replaced by config.LANGUAGE
wordList_dir = 'pools_%s/stim_lists'
