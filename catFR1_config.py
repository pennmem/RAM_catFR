# RAM_FR configuration for NONSTIM SESSIONS ONLY.
# Other configuration in the main config file
# ALL SYSTEM2.0 CONFIGURATION OPTIONS

experiment = 'catFR1'
stim_type = 'NO_STIM'
version = '3.0'
control_pc = True
heartbeat_interval = 1000
category_states = ['CAT_%d' % i for i in range(25)]
state_list = [
    'PRACTICE',
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

# THIS IS HOW THE REST OF THE PROGRAM KNOWS THIS IS A NONSTIM SESSION
do_stim = False

numSessions = 18

nBaselineTrials = 0
nStimTrials = 0
nControlTrials = 25
