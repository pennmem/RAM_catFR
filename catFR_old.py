#!/usr/bin/python

from pyepl.locals import *
from stim_info import *

# other modules
import random
import copy
import time
import os
import sys
import shutil
import codecs
import unicodedata

# Set the current version
MIN_PYEPL_VERSION = '1.0.0'
TEXT_EXTS = ["txt"]

def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])


class customTextPool(TextPool):
     def loadFromSourcePath(self, sourcepath, size, color, font):
        """
        """
        if os.path.isdir(sourcepath):
            for stimfile in os.listdir(sourcepath):
                name, ext = os.path.splitext(stimfile)
                ext = ext.lower()
                if not name or not ext:
                    continue
                try:
                    stimobj = self.findBy(name = name)
                except LookupError:
                    stimobj = self.append(name = name)
                if ext == ".dummy":
                    pass
                elif ext[1:] in TEXT_EXTS:
                    # load text file as TextPool
                    stimobj.content = TextPool(os.path.abspath(os.path.join(sourcepath,stimfile)))
                    #stimobj.content = display.Text(open(os.path.abspath(os.path.join(sourcepath, stimfile))).read(), size=size, color=color, font=font)
                else:
                    raise BadFileExtension, ext
        else:
            for line in codecs.open(sourcepath, "r", "utf-8"):
                textval = line.strip()
                self.append(name = textval,
                            content = display.Text(textval, size=size, color=color, font=font))   


def verifyFiles(config):
    """
    Verify that all the files specified in the config are there so
    that there is no random failure in the middle of the experiment.

    This will call sys.exit(1) if any of the files are missing.

    """
    
    # make the list of files from the config vars
    files = (config.wp,
             config.wordpools,
             config.introMovie%config.LANGUAGE,
             config.countdownMovie,
             config.practice_wordList%config.LANGUAGE,
             config.pre_practiceList%config.LANGUAGE,
             config.post_practiceList%config.LANGUAGE,
             )
    
    for f in files:
        if not os.path.exists(f):
            print "\nERROR:\nPath/File does not exist: %s\n\nPlease verify the config.\n" % f
            sys.exit(1)
    
def makeStimForms(exp, config, state):
    """ 
    Generate and compile LaTeX code containing a table with each
    trial's words spread between two rows. The header of each table
    states the type of stimulation to be used in that trial.
    """
    print 'making stim sheets'
    subj = exp.getOptions().get('subject')

    # Loop through sessions
    for session_i in range(config.numSessions):

        # Set the session, so the form goes in that folder
        exp.setSession(session_i)
        formName = '%s_catFR%d_s%d_wordlists'%(subj, 0 if not config.require_labjack else 2 if config.do_stim else 1, session_i)
        stimForm = exp.session.createFile(formName+'.tex')
       
        # Sets up the initial part of the LaTeX document
        preamble = []
        preamble.append('\\documentclass{article}')
        preamble.append('\\usepackage[margin=1in]{geometry}')
        preamble.append('\\usepackage{multirow}')
        preamble.append('\\usepackage{tabularx}')
        preamble.append('\\usepackage[utf8]{inputenc}')
        preamble.append('\\begin{document}')
        preamble.append('\\begin{center}')
        preamble.append('{\\large '+subj.replace('_','\\_')+' RAM\\_catFR%d word lists}'%(0 if not config.require_labjack else 2 if config.do_stim else 1))
        preamble.append('\\end{center}')
        document = []
        
        trial_stim = state.sessionStim[session_i]
        trial_stimType = state.sessionStim_type[session_i]
        trial_words = state.sessionList[session_i]
        
        last_stimType = None
        stimTypes_seen=0
        # Loop over trials
        for trial_i in range(config.numTrials):
            this_stimType = trial_stimType[trial_i]
            
            # block header
            if this_stimType!=last_stimType and this_stimType!=0:
                if trial_i>=10 and not already_pageBroke and not this_stimType==0:
                    already_pageBroke=True
                    document.append('\\pagebreak')
                    document.append('\\begin{center}')
                    document.append('{\\large '+subj.replace('_','\\_')+' RAM\\_catFR stimulation details}')
                    document.append('\\end{center}')
                stimTypes_seen+=1
                document.append('\\vspace{.1in}')
                document.append('\\begin{tabularx}{.8\\textwidth}{|l X|}')
                document.append('\\hline')
                document.append('\\large{\\textbf{ Block %d}} & ~\\\\'%stimTypes_seen)
                if this_stimType>0:
                    document.append('\\multicolumn{2}{|l|}{\large{\\textbf{ - Stim Location : %d }}} \\\\'%\
                            this_stimType)
                else:
                    document.append('\\multicolumn{2}{|l|}{\large{\\textbf{ - NO STIMULATION }}} \\\\')
                
                document.append('\\hline')
                document.append('\\end{tabularx}')
                document.append('')
                last_stimType = this_stimType

            this_words = trial_words[trial_i]
            this_stim = trial_stim[trial_i]
            # insert vertical space
            document.append('\\vspace{.1in}')

            # Wordlist items are centered
            centers = 'c '*(config.listLen/2)
            document.append('\\hspace{.5in}\\begin{tabular}{r||'+centers+'}')
            rowline1 = '\\multirow{2}{*}{List %d%s} & '%(trial_i+1, '' if trial_i+1>=10 else '~~')
            for i in range(len(this_words)/2):
                word = this_words[i]
                boldWord = '\\textbf{%s}'%word.name if this_stim[i] and this_stimType!=0 else word.name
                rowline1 += (' & ' if i!=0 else '') +boldWord
            rowline1 += '\\\\'
            rowline1 = unicode(rowline1,'utf-8')
            document.append(rowline1.encode('utf-8'))
            rowline2 = '\\cline{2-7}\t\t\t& '
            for i in range(len(this_words)/2,len(this_words)):
                word = this_words[i]
                boldWord = '\\textbf{%s}'%word.name if this_stim[i] and this_stimType!=0 else word.name
                rowline2 += (' & ' if i!=len(this_words)/2 else '') +boldWord
            rowline2 += '\\\\'
            rowline2 = unicode(rowline2,'utf-8')
            document.append(rowline2.encode('utf-8'))
            document.append('\\end{tabular}')
            document.append('')
           
        postamble = ['\\end{document}']

        stimForm.write('\n'.join(preamble)+'\n'+'\n'.join(document)+'\n'+'\n'.join(postamble))

        stimForm.close()

        # Make the dvi document
        os.system('cd %s; latex %s >> latexLog.txt'%(os.path.dirname(stimForm.name), stimForm.name))

        # Convert the dvi to pdf
        dviForm = exp.session.createFile(formName+'.dvi')
        dviForm.close()
        os.system('cd %s; dvipdf %s >> latexLog.txt'%(os.path.dirname(dviForm.name), dviForm.name))
        
        # Clean up unneccesary files
        os.system('cd %s; rm %s.dvi; rm %s.log; rm %s.aux'%(os.path.dirname(dviForm.name),\
            formName,formName,formName))

def groupAndShuffle(L, groups, groupIndex=0):
    """
    Shuffles the list L while keeping groups together

    groups can be a list of different levels of groups
    if groups is [[A,A,A,A,B,B,B,B], [1,1,2,2,1,1,2,2]]
    it will keep all As together, and then all A1s together, etc.
    """

    # Just in case someone passes in a group with only one level
    if not isinstance(groups[0], list) and not isinstance(groups[0], tuple):
        groups = [groups,]

    # Will ignore any groups at inidces higher than groupIndex. 
    # Will group in this call by the group at groupIndex, then recursively
    # at lower groups
    mainGroup = groups[groupIndex]
    uniqueGroups = set(mainGroup)

    # Zip the list and all of the groups togther
    zipList = zip(L, *groups)
    
    # groupedList[i] is the entirety of the ith group, shuffled
    groupedList = []
    for group in uniqueGroups:
        # Get only the items in this group
        thisZip = [item for item in zipList if item[groupIndex+1]==group]

        # If there are lower levels of groups to sort by:
        if groupIndex+1<len(groups): 
            # Get back the L and groups for the items in this group
            unzipped  = zip(*thisZip)
            thisL = unzipped[0]
            thisG = unzipped[1:]
            # Call again on the lower group
            (thisL, thisG) = groupAndShuffle(thisL, thisG, groupIndex+1 )
            thisZip = zip(thisL, *thisG)
        else:
            # Otherwise just shuffle this group
            random.shuffle(thisZip)

        groupedList.append(thisZip)
    
    
    # Shuffle the groupedList, then flatten
    random.shuffle(groupedList)
    shuffledList = []
    for group in groupedList:
        shuffledList.extend(group)

    # Get back the List and Groups
    unzipped = zip(*shuffledList)
    return unzipped[0], unzipped[1:]

def setupStimCats(num_cats):
    stim_cats = {0:range(num_cats),
                 1:range(num_cats),
                 2:range(num_cats)}
    random.shuffle(stim_cats[0])
    random.shuffle(stim_cats[1])
    random.shuffle(stim_cats[2])

    return stim_cats

def stimTimesFromOrder(order, stimFirst):
    numToStimTimes = {0:0,1:0,2:0}
    for i, item in enumerate(order):
        if i%2==1 ^ stimFirst:
            numToStimTimes[item]+=1
    
    return numToStimTimes

def good_cats(cats_in_lists, i, cats_left):
    if i>=len(cats_in_lists):
        return cats_left
    else:
        used_cats = cats_in_lists[i]
    bad_cats = []
    for list_cats in cats_in_lists:
        if any([used_cat in list_cats for used_cat in used_cats]):
            bad_cats.extend(list_cats)
    cats_left = [good_cat for good_cat in cats_left if good_cat not in bad_cats]
    return cats_left

def prepare(exp, config, video):
    """
    Prepare the trials...
    """
    # seed the random number generator with the subject so that the sessions
    # will be predictable
    random.seed(exp.getOptions().get('subject'))

    # Print status messages so they can be seen after program exits
    print '******* PREPARING TRIALS IN ' + \
            ('ENGLISH' if config.LANGUAGE=='EN' else 'SPANISH') + \
            '*******'
    print '( if this is not correct, \n'+\
           'delete the subject folder in \n' + \
           '/Users/exp/RAM/data/catFR/%s )'%exp.getOptions().get('subject')

    # Also display on screen
    video.clear('black')
    video.showCentered(Text('******* PREPARING TRIALS IN ' + \
            ('ENGLISH' if config.LANGUAGE=='EN' else 'SPANISH') + \
            '*******\n' + \
            'if this is not correct, \nquit the experiment, \n'+\
            'then delete the subject folder in \n' + \
            '/Users/exp/RAM/data/catFR/%s'%exp.getOptions().get('subject')))
    
    video.updateScreen()
    # Pause for a few seconds to give a chance to cancel
    clock = PresentationClock()
    clock.delay(5000)
    clock.wait()

    # Get info from config
    num_lists = config.numTrials
    list_length = config.listLen
    num_cats = config.numCats
    words_per_cat = config.wordsPerCat
    cats_per_list = config.catsPerList
    num_sessions = config.numSessions
   
    # Copy the word pool to the sessions dir
    shutil.copy(config.wp, exp.session.fullPath())
    # Make copy of wordpool without accents:
    noAccents_wp = [remove_accents(line.strip()) \
            for line in codecs.open(config.wp,'r','utf-8').readlines()]
    open(os.path.join(exp.session.fullPath(), config.noAcc_wp),'w').write('\n'.join(noAccents_wp))

    # The order in which categories can be placed. 
    # Categories never follow the same category twice
    orders = [(0,1,2,0,2,1), (0,1,2,1,0,2)]

    # stimTimeToNum[(order, stimFirst)][X] contains the number (0, 1, or 2) in order
    # that will be stimulated X.
    stimTimeToNum = {}
    for order in orders:
        for stim in [True, False]:
            stimTimeToNum[(order, stim)] = stimTimesFromOrder(order, stim)
    
    # Get the wordpools
    categories = customTextPool(config.wordpools)
    
    # Used to xor with list_stim_first to determine if stim is on or off for first category
    sess_stim_first = [True, False] * (num_sessions/2)
    random.shuffle(sess_stim_first)

    # The number of trials of each stim type
    numEachStimType = config.numTrials/len(config.stimLocs)
    # The number of trials with stimulation (assumes one type of stim is no stim)
    numStimTrials = config.numTrials-numEachStimType  

    # sessionList[s][t][w] contains the wth word on the tth list of session s
    sessionList = []
    sessionCat = []
    sessionCatNum = []
    sessionStim = []
    sessionStim_type = []
    
    # Loop over sessions
    for sess_num in range(num_sessions):
        
        # If stimming, assign each of the stim types in order (will shuffle later)
        if config.do_stim:
            trialStim_type = []
            for stimType in config.stimLocs:
                trialStim_type.extend([stimType]*numEachStimType)
        else:
            # Otherwise, just assign 0 to all trials
            trialStim_type = [0]*config.numTrials
        
        # Every other trial
        if sess_num%2==0:
            # Words stimmed last session aren't stimmed now
            stim_words = []
            # Categories that appeared together last session don't appear together now
            last_cats_in_lists = []

        # Gonna mess with the pools, so make a deep copy
        unused_categories = copy.deepcopy(categories)
        
        # The numbers of the categories appearing in each list.
        cats_in_lists = []
        
        # Number of stimulation times in a list to category number. 
        stim_cats = setupStimCats(num_cats)

        list_num = 0

        # If it fails, try again
        REDO = False

        # xor with sess_stim_first to determine if first word of list is stimulated
        # keep in order, will shuffle later. Ensures counterbalancing
        list_stim_first = [True, False] * (numStimTrials/2)
        if numStimTrials%2!=0:
            list_stim_first.append(True)

        # Loop over the lists, assigning the categories that will be placed in them
        while list_num < num_lists:

            # First time through, categories are in the order no stim, 1 stim, 2 stim
            # second time through, reverse order.
            # Ensures that a category has enough stim words on the second session
            # (stim_cats is shuffled, so just taking the first one works)
            if sess_num%2==0:
                first_cat = stim_cats[0].pop(0)
            else:
                first_cat = stim_cats[2].pop(0)
            
            # start building the list
            cats_in_lists.append([first_cat])
            
            # looping over the number of categories in a list
            for cat_num in range(1, cats_per_list):
                
                # like above, gotta switch 0 and 2 on the second session. 
                if sess_num%2==0:
                    true_cat_num = cat_num
                else:
                    true_cat_num = 0 if cat_num==2 else 2 if cat_num==0 else 1
                
                # cats_to_use are categories that haven't appeared with a category in the current list yet
                cats_to_use = good_cats(cats_in_lists+last_cats_in_lists, list_num,  stim_cats[true_cat_num])
                
                # If it doesn't work, try again
                if len(cats_to_use)==0:
                    REDO = True
                    break
                
                # Remove the cat num from stim_cats, and append to this list
                this_cat = stim_cats[true_cat_num].pop(stim_cats[true_cat_num].index(cats_to_use.pop(0)))
                cats_in_lists[-1].append(this_cat)
            
            # If it didn't work, restart.
            if REDO:
                list_num=0
                REDO = False
                cats_in_lists = []
                stim_cats = setupStimCats(num_cats)
            else:
                list_num +=1

        # If it's an even session, store categories from last session so they won't appear in the same list again
        if sess_num%2==0:
            last_cats_in_lists = cats_in_lists

        # Choose the orders to use. These can be shuffled right away - not counterbalanced.
        unused_orders = orders*(num_lists/len(orders))
        while len(unused_orders) < num_lists:
            unused_orders.append(random.choice(orders))
        random.shuffle(unused_orders)

        # Order the category numbers
        cat_order = []

        # Gotta keep track of which stim trial you're on for list_stim_first.
        stim_trialNum = 0

        # loop over the categories and orders
        for i, (list_cats, stim_type, this_order) in \
                enumerate(zip(cats_in_lists, trialStim_type, unused_orders)):
            
            # If you're actually stimming on this trial
            if stim_trialNum<len(list_stim_first) and stim_type>0:
                # That first True is neccesary because below, I test if cat_num%2==0 
                # could have changed it below, but decided to add it here instead
                stim_first = True ^ list_stim_first[stim_trialNum] ^ sess_stim_first[sess_num]
            else:
                stim_first = True

            # gives what number in this_order corresponds to the number of times that the category
            # is being stimulated
            stimTimes_order_dict = stimTimeToNum[(this_order, \
                                             stim_first ^ sess_stim_first[sess_num])]

            # like this_order, but the numbers now correspond to how many times that item will be stimulated
            stimTimes_order = [stimTimes_order_dict[num] for num in this_order]

            # the actual order in which the categories will be presented
            true_order = [list_cats[stimTimes] for stimTimes in stimTimes_order]
            cat_order.append(true_order)
            
            if stim_type>0:
                stim_trialNum+=1

        # Information for this session only.
        trialStim = []
        trialLists = []
        trialCat = []
        trialCatNum = []
        stim_trialNum = 0
        
        
        # loop over the categories in each list
        for list_num, list_cats in enumerate(cat_order):

            # info for this list only
            this_list = []
            this_stim = []
            this_catName = []
            this_catNum = []

            #loop over the categories in this list
            for cat_num, cat in enumerate(list_cats):

                # Get the words in this category. Shuffle.
                this_cat = unused_categories[cat]['content']
                random.shuffle(this_cat)
                
                
                if stim_trialNum>=len(list_stim_first):
                    # Gotta pretend it's a stim trial even when it's not, or else there
                    # won't be enough stim trials on the first session to fill the stim
                    # trials on the second session
                    stim_word = cat_num%2==0
                else:
                    stim_word = sess_stim_first[sess_num] ^ \
                                list_stim_first[stim_trialNum] ^\
                                cat_num%2==0
                
                # This is where it specifies if the word is ACTUALLY being stimulated.
                if stim_word and config.do_stim and trialStim_type[list_num]>0:
                    new_stim = [True,True]
                else:
                    new_stim = [False,False]

                # If it's the first session, grab any word from the category
                if sess_num%2==0:
                    new_words = [this_cat.pop(), this_cat.pop()]
                    if stim_word:
                        stim_words.extend(new_words)
                else:
                    # Otherwise, you can only use words that were stimmed/not stimmed last 
                    # session. 
                    word1 = this_cat.pop(0)
                    tried = 0

                    # try each word in turn, seeing if it's in the right list
                    # (bad way of doing this, I know. It works, though)
                    while not (stim_word ^ (word1 in stim_words)) and tried < len(this_cat):
                        this_cat.append(word1)
                        word1 = this_cat.pop(0)
                        tried += 1
                    
                    # Do the same with the second word
                    word2 = this_cat.pop(0)
                    while not (stim_word ^ (word2 in stim_words)) and tried < len(this_cat):
                        this_cat.append(word2)
                        word2 = this_cat.pop(0)
                    
                    # check to make sure it worked. If not, we have a problem.
                    if not (stim_word ^ (word2 in stim_words)):
                        print 'OOPS. Can\'t make the lists correctly for some reason.'
                        exit()

                    # Found the words to use
                    new_words = [word1, word2]
                
                # Store the information 
                this_catNum.extend([cat]*2)
                this_catName.extend([unused_categories[cat]['name']]*2)
                this_list.extend(new_words)
                this_stim.extend(new_stim)
            
            if trialStim_type[list_num]>0:
                stim_trialNum+=1

            trialLists.append(this_list)
            trialStim.append(this_stim)
            trialCat.append(this_catName)
            trialCatNum.append(this_catNum)

        # Group the trials by stim type 
        trial = zip(trialLists, trialStim, trialStim_type, trialCat, trialCatNum)
        
        # get the part of the stim type we want to group by:
        type = [t if t!=0 else random.choice(config.non0_stimLocs) for t in trialStim_type]
        
        # GROUP AND SHUFFLE.
        (trial, _) = groupAndShuffle(trial, type)
        (trialList, trialStim, trialStim_type, trialCat, trialCatNum) = zip(*trial)

        # Write the lists out to file
        for trialNum in range(config.numTrials):
            exp.setSession(sess_num)
            thisTrial = trialList[trialNum]
            listFile = exp.session.createFile('%d.lst'%trialNum)
            listFile.write('\n'.join([remove_accents(word.name.decode('utf-8')) for word in thisTrial]))
            listFile.close()

        sessionList.append(trialList)
        sessionStim.append(trialStim)
        sessionStim_type.append(trialStim_type)
        sessionCat.append(trialCat)
        sessionCatNum.append(trialCatNum)

    # Save the state 
    exp.saveState(exp.restoreState(),
                  trialNum = 0,
                  practiceDone = False,
                  sessionList = sessionList,
                  sessionStim = sessionStim,
                  sessionStim_type = sessionStim_type,
                  sessionCat = sessionCat,
                  sessionCatNum = sessionCatNum,
                  lastStimTime = 0,
                  sessionNum = 0,
                  language='spanish' if config.LANGUAGE=='SP' else 'english',
                  LANG=config.LANGUAGE
                  )

    # make the wordlist files
    state = exp.restoreState()

    video.clear('black')
    video.showCentered(Text('Making word list files. \n This may take a moment...'))
    video.updateScreen()
    makeStimForms(exp, config, state)

        
def checkStimParams(state, config):
    """
    Checks to make sure that the stim parameters exist for this session if it is
    a stimulation session.

    Returns:
        False if stim params are not set
        True if they are
    """
    
    try:
        if config.do_stim and state.stimParams[state.sessionNum]!=None:
            return True
    except:
        waitForAnyKey(showable=Text('NO STIM PARAMS DETECTED.\n Please enter stimulation info first'))
        return False

    if config.do_stim:
        waitForAnyKey(showable=Text('NO STIM PARAMS DETECTED.\n Please enter stimulation info first'))
        return False
    else:
        return True


def runPracticeList(exp, state, video, config, clock, log, mathlog):
    """
    Runs a subject in a single practice list (encoding + recall)
    """
    if state.practiceDone:
        bc = ButtonChooser(Key('Y'),Key('N'))
        (_,button,_) = Text('Practice list already ran.\nPress Y to run again\nPress N to skip').\
                present(bc = bc)
        if button==Key('N'):
            return
    
    
    waitForAnyKey(clock, Text(codecs.open(config.pre_practiceList%state.LANG, encoding='utf-8').read()))

    practiceList = [line.strip() for line in codecs.open(config.practice_wordList%state.LANG, encoding='utf-8').readlines()]
    random.shuffle(practiceList)
    
    countdown(config, log, clock, video)

    # display the "cross-hairs"
    timestamp = flashStimulus(Text(config.orientText, size = config.wordHeight),
                  clk=clock,
                  duration=config.wordDuration)
    

    clock.delay(config.PauseBeforeWords, jitter = config.JitterBeforeWords)   


    ### ENCODING
    for word in practiceList:
        clock.delay(config.ISI, config.Jitter)
        timestamp = Text(word, size=config.wordHeight).present(clk=clock, duration=config.wordDuration)
        log.logMessage(('PRACTICE_WORD\t%s'%(word)).encode('utf-8'), timestamp)
    
    if config.doMathDistract and not config.fastConfig:
        log.logMessage('PRACTICE_DISTRACT_START',clock.get())
        mathDistract(clk=clock,
                mathlog=mathlog,
                numVars=config.MATH_numVars,
                maxProbs = config.MATH_maxProbs,
                plusAndMinus = config.MATH_plusAndMinus,
                minDuration = config.MATH_minDuration,
                textSize = config.MATH_textSize)
        log.logMessage('PRACTICE_DISTRACT_END',clock.get())

    clock.delay(config.PauseBeforeRecall, jitter=config.JitterBeforeRecall)
    
    startText = video.showCentered(Text(config.recallStartText, size=config.wordHeight))
    video.updateScreen(clock)
    
    # create the beeps
    startBeep = Beep(config.startBeepFreq,
                     config.startBeepDur,
                     config.startBeepRiseFall)
    stopBeep = Beep(config.stopBeepFreq,
                    config.stopBeepDur,
                    config.stopBeepRiseFall)


    ts = startBeep.present(clock)
    video.unshow(startText)
    video.updateScreen(clock)
    log.logMessage('PRACTICE_REC_START', ts)
    clock.delay(config.recallDuration)
    ts = stopBeep.present(clock)
    log.logMessage('PRACTICE_REC_END', ts)
    
    state.practiceDone = True
    exp.saveState(state)
    waitForAnyKey(clock, Text(codecs.open(config.post_practiceList%state.LANG, encoding='utf-8').read()))

def playWholeMovie(video, movieFile, clock):
    """
    Plays any movie file, centered on the screen
    """
    movieObject = Movie(movieFile)
    movieShown = video.showCentered(movieObject)
    video.playMovie(movieObject)
    clock.delay(movieObject.getTotalTime())
    clock.wait()
    video.stopMovie(movieObject)
    video.unshow(movieShown)


def countdown(config, log,clock, video):
    """
    Shows the countdown video, centered.
    """
    video.clear('black')
    log.logMessage('COUNTDOWN_START',clock)
    playWholeMovie(video, config.countdownMovie, clock)

    log.logMessage('COUNTDOWN_END',clock)



def checkSessNum(exp, state):
    """
    Manual check of the session number
    returns True if check passes, False otherwise
    """
    bc = ButtonChooser(Key('Y'),Key('N'))
    subj = exp.getOptions().get('subject')
    (_,button,_) = Text('Running %s in session %d of catFR%d \n(%s).\n Press Y to continue, N to quit'%\
                       (subj,
                        state.sessionNum+1,
                        0 if not config.require_labjack else 2 if config.do_stim else 1,
                        state.language
                       )).present(bc=bc)
    if button==Key('Y'):
        return True
    else:
        return False
    
def run(exp, config, video):
    """
    Run a session of free recall.
    """

    # set priority
    # TODO: ASK JONATHAN WHAT THIS DOES.
    if config.doRealtime:
        setRealtime(config.rtPeriod,config.rtComputation,config.rtConstraint)
    
    # verify that we have all the files
    verifyFiles(config)
    
    # get the state
    state = exp.restoreState()
    
    # set up the session
    # have we run all the sessions
    if state.sessionNum >= len(state.sessionList):
        print "No more sessions!"
        return

    # set the session number
    exp.setSession(state.sessionNum)
    
    # get session specific config
    sessionconfig = config.sequence(state.sessionNum)

    # create tracks...
    audio = AudioTrack("audio")
    keyboard = KeyTrack("keyboard")
    log = LogTrack("session")
    mathlog = LogTrack("math")
    eeg = EEGTrack('eeg', autoStart = False)
    eeg.startService()
    eeg.startLogging()

    # get a presentation clock
    clock = PresentationClock()
     
    #### CHECK IF SESSION SHOULD BE SKIPPED
    if state.trialNum!=0:
        bc = ButtonChooser(Key('SPACE') & Key('RETURN'), Key('ESCAPE'))
        video.clear('black')
        (_,button,timestamp) = Text(
                'Session %d was previously started\n'%(state.sessionNum+1)+\
                'Press SPACE + RETURN to skip session\n'+\
                'Press ESCAPE to continue'\
                ).present(clock, bc=bc)
        if 'AND' in button.name:
            log.logMessage('SESSION_SKIPPED',timestamp)
            state.sessionNum+=1
            state.trialNum=0
            state.practiceDone=False
            exp.saveState(state)
            waitForAnyKey(clock, Text('Session skipped. \n Restart RAM_catFR to run next session'))
            exit()   
    timestamp = clock.get()
    
    video.clear('black')

    if not checkStimParams(state, config):
        exit(1)

    if not checkSessNum(exp, state):
        exit(1)

    if config.require_labjack:
        if not eeg.labjack:
            waitForAnyKey(clock, Text("SYNC BOX REQUIRED,\nBUT CANNOT FIND LABJACK.\nENSURE USB CONNECTION AND RESTART EXPERIMENT\n"+
                  "(to disable requiring sync box, edit line\n"+
                  "reqire_labjack=True to require_labjack=False\n"+
                  "in config.py)", size=.05))
            exit(1)

    if config.do_stim:
        if not eeg.labjack:
            waitForAnyKey(clock, Text("STIM SESSION,\nBUT CANNOT FIND LABJACK.\nENSURE USB CONNECTION AND RESTART EXPERIMENT", size=.05))
            exit(1)

        # Get the stimulation parameters
        stimParams = state.stimParams[state.sessionNum]
    

     # Get stim parameters for this session
    trialStim = state.sessionStim[state.sessionNum]
    trialStim_type = state.sessionStim_type[state.sessionNum]
    trialCat = state.sessionCat[state.sessionNum]
    trialCatNum = state.sessionCatNum[state.sessionNum]
    # Get the lists for this session
    trialList = state.sessionList[state.sessionNum]

    for firstStim_type in trialStim_type:
        if firstStim_type!=0:
            break
    


    # log start and version number
    log.logMessage('SESS_START\t%s\t%s\tv_%s' % \
            (state.sessionNum + 1, \
             'NO_RECORD_SESSION' if not config.require_labjack else 'STIM_SESSION' if config.do_stim else 'NONSTIM_SESSION',\
             str(config.catFR_VERSION_NUM)), timestamp)
    
    # Test microphone
    soundgood = micTest(2000,1.0)
    if not soundgood:
        #quit
        return

    # do instructions on first trial of each session
    if state.trialNum==0:
        runPracticeList(exp, state, video, config, clock, log, mathlog)

    # So the experiment can pause and display a different message when stim changes
    lastStim_type = firstStim_type

    # present each trial in the session
    while state.trialNum < len(trialList):

        # Stimulation type for this trial
        thisStim_type = trialStim_type[state.trialNum]
        
        # load trial specific config
        # TODO: ASK JONAATHAN WHAT THIS DOES.
        trialconfig = sessionconfig.sequence(state.trialNum)

        # create the beeps
        startBeep = Beep(trialconfig.startBeepFreq,
                         trialconfig.startBeepDur,
                         trialconfig.startBeepRiseFall)
        stopBeep = Beep(trialconfig.stopBeepFreq,

                        trialconfig.stopBeepDur,
                        trialconfig.stopBeepRiseFall)

        # Clear to start
        video.clear("black")

        # show the current trial and wait for keypress
        if not config.fastConfig:
            if lastStim_type==thisStim_type or thisStim_type==0:
                # show the current trial and wait for keypress
                timestamp = waitForAnyKey(clock,Text("Press any key for Trial #%d" % (state.trialNum + 1)))
            else:
                bc = ButtonChooser(Key('SPACE') & Key('RETURN'))
                (_,_,timestamp) = Text('Stimulation parameters are changing \n'+\
                        'Set stim manager to program:\nLoc%d_uAmp%04d'%\
                        (thisStim_type, float(stimParams[thisStim_type-1]['AMPLITUDE'])*1000)+\
                        'When finished, \npress SPACE + RETURN for trial #%d' %\
                        (state.trialNum+1)).present(clock, bc = bc)
                lastStim_type = thisStim_type

        else:
            timestamp = clock.get()
        # Log the start of the trial
        log.logMessage('TRIAL\t%d\t%s\t%s' % \
                (state.trialNum + 1, 'STIM_PARAM',thisStim_type),timestamp)
        
        # COUNT DOWN FROM TEN
        countdown(config, log, clock, video)

        # display the "cross-hairs"
        timestamp = flashStimulus(Text(trialconfig.orientText, size = trialconfig.wordHeight),
                      clk=clock,
                      duration=trialconfig.wordDuration)
        

        clock.delay(trialconfig.PauseBeforeWords, jitter = trialconfig.JitterBeforeWords)

        # log the flash
        log.logMessage('ORIENT', timestamp)
        
        # start them words
        for n, (eachWord, eachStim) in enumerate(\
                zip(trialList[state.trialNum],
                    trialStim[state.trialNum])):
            
            # Stim if this is really a stim trial
            eachStim = eachStim and (thisStim_type!=0)

            # get word specific config
            wordconfig = trialconfig.sequence(n)

            # create the stimtext if needed
            if wordconfig.presentationType == 'text':
                eachWord.text = Text(getattr(eachWord,wordconfig.presentationAttribute),
                                     size = wordconfig.wordHeight)
             
            # Check to make sure stim hasn't happened within the length of the stim,
            # so that the trigger doesn't happen twice
            
            if config.do_stim and eachStim and \
                    ((clock.get()-(config.stim_length*1000)) > state.lastStimTime or config.fastConfig):
                clock.delay(wordconfig.ISI-trialconfig.prestimulus_stim, \
                        jitter = wordconfig.Jitter)
               
                clock.wait()
                # DO NOT STIM if running in fast mode
                if not config.fastConfig:
                    eeg.timedStim(config.stim_length, config.stim_freq)

                clock.tare()
                state.lastStimTime = clock.get()
                log.logMessage('STIM_ON',state.lastStimTime)
                clock.delay(trialconfig.prestimulus_stim)
            else:
                clock.delay(wordconfig.ISI, wordconfig.Jitter)
               
            # present the word
            #timestamp = Text((getattr(eachWord,
            #                    wordconfig.presentationAttribute,\
            #                    )).encode('utf-8'),
            #                    size=wordconfig.wordHeight).present(clk = clock,
            #                                                        duration = wordconfig.wordDuration,
            #                                                         )
            timestamp = Text(unicode(eachWord.name,'utf-8'),\
                              size=wordconfig.wordHeight).present(clk = clock,
                                                                  duration = wordconfig.wordDuration,
                                                                  )


            # log the word
            log.logMessage('WORD\t%s\t%s\t%d\t%s\t%d\t%s' %\
                    (wordconfig.presentationType,\
                    unicode(eachWord.name,'utf-8').encode('utf-8'),\
                    n,\
                    'STIM' if eachStim else 'NO_STIM',\
                    trialCatNum[state.trialNum][n],
                    trialCat[state.trialNum][n]), timestamp
                    )

            # Add optional distractor after each word
            if wordconfig.continuousDistract and not config.fastConfig:
                mathDistract(clk = clock,
                             mathlog = mathlog,
                             numVars = trialconfig.MATH_numVars,
                             maxProbs = trialconfig.MATH_maxProbs,
                             plusAndMinus = trialconfig.MATH_plusAndMinus,
                             minDuration = trialconfig.MATH_minDuration,
                             textSize = trialconfig.MATH_textSize)
                
            
        # do the math distract
        if trialconfig.doMathDistract and not trialconfig.continuousDistract and not config.fastConfig:
            log.logMessage('DISTRACT_START',clock.get())
            mathDistract(clk = clock,
                         mathlog = mathlog,
                         numVars = trialconfig.MATH_numVars,
                         maxProbs = trialconfig.MATH_maxProbs,
                         plusAndMinus = trialconfig.MATH_plusAndMinus,
                         minDuration = trialconfig.MATH_minDuration,
                         textSize = trialconfig.MATH_textSize)
            log.logMessage('DISTRACT_END',clock.get())

        # Pause before recall
        clock.delay(trialconfig.PauseBeforeRecall, jitter = trialconfig.JitterBeforeRecall)
        
        # show the recall start indicator
        startText = video.showCentered(Text(trialconfig.recallStartText, size = trialconfig.wordHeight))
        video.updateScreen(clock)

        # record recall
        startBeep.present(clock)
        
        # hide rec start text
        video.unshow(startText)
        video.updateScreen(clock)

        # Record responses
        (rec,timestamp) = audio.record(trialconfig.recallDuration,str(state.trialNum),t=clock)
        end_timestamp = stopBeep.present(clock)

        # log the recstart
        log.logMessage('REC_START' % (),timestamp)
        log.logMessage('REC_END' % (), end_timestamp)
        
        # update the trialnum state
        state.trialNum += 1

        # save the state after each trial
        exp.saveState(state)

    # save the state when the session is finished
    exp.saveState(state, trialNum = 0, sessionNum = state.sessionNum + 1, practiceDone = False)

    # Done
    timestamp = waitForAnyKey(clock,Text("Thank you!\nYou have completed the session."))
    log.logMessage('SESS_END',timestamp)

    # Catch up
    clock.wait()


# only do this if the experiment is run as a stand-alone program (not imported as a library)
if __name__ == "__main__":
    # make sure we have the min pyepl version
    checkVersion(MIN_PYEPL_VERSION)
    
    # start PyEPL, parse command line options, and do subject housekeeping
    exp = Experiment(use_eeg = False)
    exp.parseArgs()
    exp.setup()
    
    # allow users to break out of the experiment with escape-F1 (the default key combo)
    exp.setBreak()
    
    # get subj. config
    config = exp.getConfig()
    
    # NOTE: NOW HAVE TO START VIDEO BEFORE PREPARE SO IT CAN DISPLAY EN/SP
    video = VideoTrack("video")

    # if there was no saved state, run the prepare function
    if not exp.restoreState() or not hasattr(exp.restoreState(), 'trialNum'):
        prepare(exp, config, video)

    # now run the subject
    run(exp, config, video)
    
