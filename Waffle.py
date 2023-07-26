import cProfile
from collections import deque
import copy
import gc
import io
from math import ceil, sqrt
import multiprocessing
import re
import threading
import time

#hardcoded variables
bannedChars = ["'","Å","â","ä","á","å","ç","é","è","ê","í","ñ","ó","ô","ö","ü","û","-"," "]
wordLen = 5
NumberOfWords = 3


#global variables
l_FullyUnhomedLetters = []
l_AllKnownLetters = []

l_AllWords = []

#functions block
def load_dict(file:str,StorageList:list[str]):
    fileDict=io.open(file, mode="r", encoding="utf-8")
    dictionary = fileDict.readlines()
    dictsize = int(len(dictionary))
    StorageList += dictionary

def build_dictionary(wordLength:int,bannedCharacters:list[str]):
    global l_AllWords

    #Load YAWL by Mendel Leo Cooper
    load_dict("Wordlists/YAWL.txt",l_AllWords)

    l_AllWords = optimize_wordlist(l_AllWords,wordLength,bannedCharacters)

    print("Answer list Loaded.")
    print("("+str(len(l_AllWords))+" words)")

def optimize_wordlist(wordList:list[str],wordLength:int,bannedCharacters:list[str]) -> list[str]:
    """
    Returns all words in \"wordList\" that are \"wordLength\" characters long and do not contain any character in \"bannedCharacters\"\n
    The new list is deduplicated and sorted alphabetically.\n"""

    newWords = []
    for word in wordList:
        word = word.strip().lower()
        if(len(word)==wordLength):
            if not any(bannedCharacter in bannedCharacters for bannedCharacter in word):
                #print(word)
                newWords.append(word)
    newWords = list(dict.fromkeys(newWords)) #dedupe the list (because evidently it needs that)
    newWords.sort() #why not have it sorted, too?
    return newWords

def reduce_Wordlist(l_WordList:list[str], l_bannedChars:list[str] = [], l_WantedLetters:list[str] = [], s_Regex:str = "") -> list[str]:
    """Takes in a list of words, and returns only the words that fit certain criteria"""
    newWords = []
    for word in l_WordList:
        if not any(bannedCharacter in l_bannedChars for bannedCharacter in word): #no banned letters
            if StrContainsAllLettersWithCount(word,l_WantedLetters): #all(needLetter in word for needLetter in neededLetters): #contains the letters we need
                if re.search(s_Regex, word):
                    newWords.append(word)
    return newWords

def StrContainsAllLettersWithCount(s_Word:str, l_Letters:list[str]) -> bool:
    #quick check to skip the hard part if I don't need to.
    #Turns out this check is slower in most cases
    #if not all(needLetter in s_word for needLetter in l_letters):
    #    return False

    for i in range(len(l_Letters)):
        #neededCount = l_letters.count(l_letters[i])
        #haveCount = s_word.count(l_letters[i])
        if s_Word.count(l_Letters[i])<l_Letters.count(l_Letters[i]):
            return False
    
    #if it got this far, it's a pass
    return True

def DeepExtend(l_OrigList:list, l_Extension:list) -> list:
    #for i in range(len(l_Extension)):
    tempCopy = copy.deepcopy(l_Extension)
    l_OrigList.extend(tempCopy)
    return l_OrigList

def AreWeDoneYet(l_HorizontalWords:list[str], l_VerticalWords:list[str]) -> bool:
    for i in range(len(l_HorizontalWords)):
        if len(l_HorizontalWords[i]) > 1:
            return False
    for i in range(len(l_VerticalWords)):
        if len(l_VerticalWords[i]) > 1:
            return False
    return True

def DisplayWaffle(l_HorizKnownLetters:list[str],l_VertKnownLetters:list[str]) -> None:
    iWordLen = len(l_HorizKnownLetters[0])
    iNumberOfWords = len(l_HorizKnownLetters)
    for Row in range(iWordLen):
        sOutput = ""
        if Row % 2 == 0: #row 0,2,4: full length words
            #Row 0 = horizword 0
            #Row 2 = horizword 1
            #Row 4 = horizword 2
            iWordIndex = round(Row / 2)
            for i in range(iWordLen):
                if l_HorizKnownLetters[iWordIndex][i] == ".":
                    sOutput += " ? "
                else:
                    sOutput += " "+l_HorizKnownLetters[iWordIndex][i]+" "
        else: #row 1,3: just 3 letters
            #Col 0 = VertWord 0
            #Col 1 = space
            #col 2 = VertWord 1
            #Col 3 = space
            #col 4 = VertWord 2
            for Col in range(iWordLen):
                if Col % 2 == 0: #column 0,2,4: letters
                    iWordIndex = round(Col / 2)
                    if l_VertKnownLetters[iWordIndex][Row] == ".":
                        sOutput += " ? "
                    else:
                        sOutput += " "+l_VertKnownLetters[iWordIndex][Row]+" "
                else: #1 or 3: spaces
                    sOutput += "   "
        print(sOutput)

def LetterIndextoWordCoords(Index:int,iWordLen:int,iNumOfWords:int) -> list:
    """Takes an integer for the index in the storage string a letter is, and converts that to a list with the Vertical and Horizontal word and index it represents"""
    l_ReturnList = [[None,None],[None,None]] #1st is horizontal [word, index], 2nd is vertical [word,index]
    #00 = [[0,0][0,0]]
    #01 = [[0,1][None,None]]
    #02 = [[0,2][1,0]]
    #03 = [[0,3][None,None]]
    #04 = [[0,4][2,0]]
    #05 = [[None,None][0,1]]
    #06 = [[None,None][1,1]]
    #07 = [[None,None][2,1]]
    #08 = [[1,0][0,2]]
    #09 = [[1,1][None,None]]
    #10 = [[1,2][1,2]]
    #...
    #20 = [[2,4][2,4]]

    iSetLength = iWordLen+iNumOfWords
    #set index = which block of 8 are we in
    iSetIndex = Index // iSetLength
    #Super Index = which part of the block of 8 are we in
    iSuperIndex = Index - (iSetIndex*iSetLength)

    if Index >= ((iSetLength * (iNumOfWords-1))+iWordLen):
        return l_ReturnList #the index isn't valid at all
    elif Index < 0:
        return l_ReturnList

    #Horizontal word:
    HorizWord = iSetIndex
    HorizIndex = iSuperIndex
    if HorizIndex >= wordLen:
        HorizWord = None
        HorizIndex = None
    
    VertWord = None
    VertIndex = None
    #vertical word:
    if iSuperIndex < iWordLen:
        #we're in the first part, where it alternates for vertical being valid
        if iSuperIndex % 2 == 0:
            #valid spot
            VertIndex = iSetIndex * 2 #the index goes up by 2 for every set, and we know we're in the first part here
            VertWord = iSuperIndex // 2
        else:
            #invalid spot, already set to None, so nothing to do
            pass
    else:
        #we're in the second part where word constantly ticks up, but index stays the same
        VertIndex = (iSetIndex * 2) + 1 #the index goes up by 2 for every set, and we know we're in the second part here
        VertWord = iSuperIndex - iWordLen

    l_ReturnList = [[HorizWord,HorizIndex],[VertWord,VertIndex]]
    return l_ReturnList

def LetterIndextoGeneralCoords(Index:int,iWordLen:int,iNumOfWords:int) -> list:
    """Takes an integer for the index in the storage string a letter is, and converts that to the coordinates it represents"""
    l_ReturnList = [None,None]
    #00 = [0,0]
    #01 = [1,0]
    #02 = [2,0]
    #03 = [3,0]
    #04 = [4,0]
    #05 = [0,1]
    #06 = [2,1]
    #07 = [4,1]
    #08 = [0,2]
    #20 = [4,4]
    #0, 6

    iSetLength = iWordLen+iNumOfWords
    #set index = which block of 8 are we in
    iSetIndex = Index // iSetLength
    #Super Index = which part of the block of 8 are we in
    iSuperIndex = Index - (iSetIndex*iSetLength)

    if Index >= ((iSetLength * (iNumOfWords-1))+iWordLen):
        return l_ReturnList #the index isn't valid at all
    elif Index < 0:
        return l_ReturnList
    x = None
    y = None
    if iSuperIndex < iWordLen:
        #we're in the first part, where it counts up normally
        x = iSuperIndex
        y = iSetIndex * 2
    else:
        #second part, x counts by 2s
        x = (iSuperIndex-iWordLen)*2
        y = (iSetIndex * 2)+1
    l_ReturnList = [x,y]
    return l_ReturnList

def CoordsToWordIndex(X:int,Y:int,iWordLen:int,iNumofWords:int) -> list:
    #0,0 = [[0,0][0,0]]
    #1,0 = [[0,1][None,None]]
    #2,0 = [[0,2][1,0]]
    #3,0 = [[0,3][None,None]]
    #4,0 = [[0,4][2,0]]
    #0,1 = [[None,None][0,1]]
    #1,1 = [[None,None][None,None]]
    #2,1 = [[None,None][1,1]]
    #3,1 = [[None,None][None,None]]
    #4,1 = [[None,None][2,1]]
    #0,2 = [[1,0][0,2]]
    #1,2 = [[1,1][None,None]]
    #2,2 = [[1,2][1,2]]
    #3,2 = [[1,3][None,None]]
    #4,2 = [[1,4][2,2]]
    #0,3 = [[None,None][0,3]]
    #1,3 = [[None,None][None,None]]
    #2,3 = [[None,None][1,3]]
    #3,3 = [[None,None][None,None]]
    #...
    #4,4 = [[2,4][2,4]]

    #if col is odd, there's no horizontal
    #if Row is odd, there's no vertical
    if Y % 2 == 0:
        #there is a horizontal
        HorizWord = Y // 2
        HorizIndex = X
    else:
        HorizIndex = None
        HorizWord = None
    if X % 2 == 0:
        #there is a vertical
        VertWord = X // 2
        VertIndex = Y
    else:
        VertIndex = None
        VertWord = None

    l_ReturnList = [[HorizWord,HorizIndex],[VertWord,VertIndex]]
    return l_ReturnList

def CoordsToStringIndex(X:int,Y:int,iWordLen:int,iNumofWords:int) -> int:
    iIndex = 0
    iIndex += (Y // 2) * (iWordLen+iNumofWords) #add in previous sets of 2 rows (Helpful if row is >= 2)
    if Y % 2 == 1: #odd row: 1,3
        iIndex += iWordLen #add in the previous row of 5
        iIndex += (X // 2)
    else:
        iIndex += X
    return iIndex

def SetLetters(sLetters:str,sColors:str,lHorizLetters:list,lVertLetters:list,lUnhomed:list):
    lFDsFound = []
    lUnhomed.clear()
    if not len(sLetters) == len(sColors):
        raise ValueError("Letters and Colors must be the same length.")
    iWordLen = len(lHorizLetters[0])
    iNumOfWords = len(lHorizLetters)
    for i in range(len(sColors)):
        if sColors[i] == "g":
            l_LetterIndexes = LetterIndextoWordCoords(i,iWordLen,iNumOfWords)
            if l_LetterIndexes[0][0] != None:
                lHorizLetters[l_LetterIndexes[0][0]][l_LetterIndexes[0][1]] = sLetters[i]
            if l_LetterIndexes[1][0] != None:
                lVertLetters[l_LetterIndexes[1][0]][l_LetterIndexes[1][1]] = sLetters[i]
        elif sColors[i] == "y":
            currChar = sLetters[i]
            #check for "funky dingo" situations!
            lCoords = LetterIndextoWordCoords(i,iWordLen,iNumOfWords)
            lCrossroads = [] #fill with arrays holding the [x,y] of every crossroads in this word
            if lCoords[0][0] != None: #horizontal word
                y = lCoords[0][0] * 2
                for x in range(iWordLen):
                    if isCrossroad(x,y):
                        lCrossroads.append([x,y])
            if lCoords[1][0] != None: #vertical word
                x = lCoords[1][0] * 2
                for y in range(iWordLen):
                    if isCrossroad(x,y):
                        lCrossroads.append([x,y])
            #now: if the letter appears in both the vertical and horizontal, and both are yellow, we MIGHT have a funky dingo, and one of those letters should be added to "unhomed"
            #HOWEVER: if the letter appears in both, but only one is yellow, it CANNOT be at that crossroads. Maybe reduce the words here or let the actual reducer figure that out.
            #if the letter only appears on one side: we can't be sure. It's not a funky dingo, but the letter can be in that spot. No harm, no foul. Nothing to do or say, really.
            for j in range(len(lCrossroads)):
                currentCoords = lCrossroads[j]
                if [currentCoords[0],currentCoords[1],currChar] not in lFDsFound:
                    if len(PossibleFunkyDingos(sLetters,sColors,iWordLen,iNumOfWords,currentCoords[0],currentCoords[1],currChar))>0:
                        lUnhomed.append(currChar) #there's a possible funkydingo, so we might have an extra one of these letters around.
                        lFDsFound.append([currentCoords[0],currentCoords[1],currChar])
                        break #once we find one, we don't need to keep trying.
            pass
        else:
            lUnhomed.append(sLetters[i])

def PossibleFunkyDingos(sLetters:str,sColors:str,iWordLen:int, iNumOfWords:int, xCoord:int, yCoord:int, FindChar:str = None) -> list[str]:
    """Takes in the current board state, takes an index in the boardstate to work on, and an optional character to exclusively search for.\n
    Will then return a list of all possible funkyDingo situations for that crossroads"""
    #now: if the letter appears in both the vertical and horizontal, and both are yellow, we MIGHT have a funky dingo, and one of those letters should be added to "unhomed"
    #HOWEVER: if the letter appears in both, but only one is yellow, it CANNOT be at that crossroads. Maybe reduce the words here or let the actual reducer figure that out.
    #if the letter only appears on one side: we can't be sure. It's not a funky dingo, but the letter can be in that spot. No harm, no foul. Nothing to do or say, really.
    wordCoords = CoordsToWordIndex(xCoord,yCoord,iWordLen,iNumOfWords)
    if wordCoords[0][0] == None or wordCoords[1][0] == None:
        return [] #it's not even a crossroads, obviously not.
    elif sColors[CoordsToStringIndex(xCoord,yCoord,iWordLen,iNumOfWords)] == "g":
        return [] #it can't be a funkydingo because the crossroad is set...
    elif FindChar != None and sLetters[CoordsToStringIndex(xCoord,yCoord,iWordLen,iNumOfWords)] == FindChar:
        return [] #if it's not green, but the crossroads IS the letter we're concerned about, then we know it can't be that letter, so no FD.
    
    verticalYelChars = []
    HorizontalYelChars = []
    VerticalHasChar = False
    HorizontalHasChar = False
    for x in range(iWordLen):
        strIndex = CoordsToStringIndex(x,yCoord,iWordLen,iNumOfWords)
        if sColors[strIndex] == "y" and x != xCoord:
            if FindChar == None:
                HorizontalYelChars.append(sLetters[strIndex])
            elif sLetters[strIndex] == FindChar:
                HorizontalHasChar = True
                break
    for y in range(iWordLen):
        strIndex = CoordsToStringIndex(xCoord,y,iWordLen,iNumOfWords)
        if sColors[strIndex] == "y" and y != yCoord:
            if FindChar == None:
                verticalYelChars.append(sLetters[strIndex])
            elif sLetters[strIndex] == FindChar:
                VerticalHasChar = True
                break
    if VerticalHasChar and HorizontalHasChar:
        #POSSIBLE FUNKY DINGO!
        return [FindChar]
    elif FindChar == None:
        lOverlap = list(set(HorizontalYelChars) & set(verticalYelChars))
        if len(lOverlap) > 0:
            #Possible FunkyDingo(s)!
            return lOverlap
    return [] #if it gets here without returning, it's not possible.

def isCrossroad(x:int,y:int) -> bool:
    if x % 2 == 0 and y % 2 == 0:
        #both are even, and thus are crossroads.
        return True
    else:
        return False

def PossibleLettersAtLocation(X:int,Y:int,sLetters:str,sColors:str,lHorizLetters:list,lVertLetters:list,lHorizAnswers:list,lVertAnswers:list,lUnHomed:list):
    #if the letter is set in Hor/VertLetters, just return that
    #Otherwise: Find yellow letters that HAVE to be in that word (Yellows at [0,1] and [0,3] have to be in Horizontal word 0)
    #find yellow letters that COULD be in the word (connected rows/collumns)
    #add unhomed letters (Make sure they're not in that row/collumn)
    #dedupe
    #cross-reference with valid answers
    iWordLen = len(lHorizLetters[0])
    iNumOfWords = len(lHorizAnswers)

    l_WordLocations = CoordsToWordIndex(X,Y,iWordLen,iNumOfWords)
    if l_WordLocations[0][0] != None:
        if lHorizLetters[l_WordLocations[0][0]][l_WordLocations[0][1]] != ".":
            return [lHorizLetters[l_WordLocations[0][0]][l_WordLocations[0][1]]]
    elif l_WordLocations[1][0] != None:
        if lVertLetters[l_WordLocations[1][0]][l_WordLocations[1][1]] != ".":
            return [lVertLetters[l_WordLocations[1][0]][l_WordLocations[1][1]]]

    lAllowedLetters = []
    lNotAllowed = [] #to store stuff like the letter in the spot right now
    iLetterListLoc = CoordsToStringIndex(X,Y,iWordLen,iNumOfWords)
    lNotAllowed.append(sLetters[iLetterListLoc]) #if it's not set, then it's not green, and it can't be this letter.
    #check horizontal
    if l_WordLocations[0][0] != None:
        for i in range(iWordLen):
            iLetterIndex = CoordsToStringIndex(i,Y,iWordLen,iNumOfWords)
            if sColors[iLetterIndex] == "y":
                lAllowedLetters.append(sLetters[iLetterIndex])
                #if not i == X:
                #    if sLetters[iLetterIndex] in lNotAllowed:
                #        #Probably in here by mistake, remove it from notallowed
                #        del lNotAllowed[lNotAllowed.index(sLetters[iLetterIndex])]
            elif not sColors[iLetterIndex] == "g": #if it's not yellow or green it's a white
                if not sLetters[iLetterIndex] in lAllowedLetters:
                    lNotAllowed.append(sLetters[iLetterIndex])
    #check vertical
    if l_WordLocations[1][0] != None:
        for i in range(iWordLen):
            iLetterIndex = CoordsToStringIndex(X,i,iWordLen,iNumOfWords)
            if sColors[iLetterIndex] == "y":
                lAllowedLetters.append(sLetters[iLetterIndex])
                #if not i == Y:
                #    if sLetters[iLetterIndex] in lNotAllowed:
                #        #Probably in here by mistake, remove it from notallowed
                #        del lNotAllowed[lNotAllowed.index(sLetters[iLetterIndex])]
            elif not sColors[iLetterIndex] == "g": #if it's not yellow or green it's a white
                if not sLetters[iLetterIndex] in lAllowedLetters: #could simply be the second occurance
                    lNotAllowed.append(sLetters[iLetterIndex])
    lAllowedLetters.extend(lUnHomed)
    
    #find letters in possible answers
    lHorizAnsLetters = []
    if l_WordLocations[0][0] != None:
        leng = len(lHorizAnswers[l_WordLocations[0][0]])
        for i in range(leng):
            Char = lHorizAnswers[l_WordLocations[0][0]][i][l_WordLocations[0][1]]
            if not Char in lHorizAnsLetters:
                lHorizAnsLetters.append(Char)
    lVertAnsLetters = []
    if l_WordLocations[1][0] != None:
        leng = len(lVertAnswers[l_WordLocations[1][0]])
        for i in range(leng):
            Char = lVertAnswers[l_WordLocations[1][0]][i][l_WordLocations[1][1]]
            if not Char in lVertAnsLetters:
                lVertAnsLetters.append(Char)

    #find the crossover of all these lists
    l_CrossoverOfAnswers = []
    if (not lHorizAnsLetters == []) and (not lVertAnsLetters == []):
        #both are valid lists, find the crossover:
        l_CrossoverOfAnswers = list(set(lHorizAnsLetters) & set(lVertAnsLetters))
    elif not lHorizAnsLetters == []:
        l_CrossoverOfAnswers = lHorizAnsLetters
    elif not lVertAnsLetters == []:
        l_CrossoverOfAnswers = lVertAnsLetters
    
    l_Crossover = list(set(l_CrossoverOfAnswers) & set(lAllowedLetters))
    for i in range(len(l_Crossover)-1,-1,-1):
        if l_Crossover[i] in lNotAllowed:
            del l_Crossover[i]
    
    return l_Crossover

def ReducePossibleWords(sLetters:str,sColors:str,lHorizLetters:list,lVertLetters:list,l_HorizontalAnswers:list,l_VerticalAnswers:list,lUnHomed:list):
    iWordLen = len(l_HorizontalAnswers[0][0])
    iNumOfWords = len(l_HorizontalAnswers)
    DirtyBit = True
    while DirtyBit: #it's possible that reductions in answerlists on one side could impact the other, and why pass that up?
        DirtyBit = False
        #horizontal words
        for AnswerListIndex in range(iNumOfWords):
            yCoord = AnswerListIndex * 2
            sRegex = ""
            lRequiredLetters = []
            for x in range(wordLen):
                lPossibleLetters = PossibleLettersAtLocation(x,yCoord,sLetters,sColors,lHorizLetters,lVertLetters,l_HorizontalAnswers,l_VerticalAnswers,lUnHomed)
                if not lPossibleLetters == []: #this shouldn't ever be true, but *shrug*
                    sRegex+="["
                    for i in range(len(lPossibleLetters)):
                        sRegex+= lPossibleLetters[i]
                    sRegex+="]"
                    if len(lPossibleLetters) == 1:
                        lAffectedWords = CoordsToWordIndex(x,yCoord,iWordLen,iNumOfWords)
                        if lAffectedWords[0][0] != None:
                            lHorizLetters[lAffectedWords[0][0]][lAffectedWords[0][1]] = lPossibleLetters[0]
                        if lAffectedWords[1][0] != None:
                            lVertLetters[lAffectedWords[1][0]][lAffectedWords[1][1]] = lPossibleLetters[0]
                else:
                    print("ERROR!")
                    raise RuntimeError("There are no possible letters found at ["+str(x)+","+str(yCoord)+"]")

                if sColors[CoordsToStringIndex(x,yCoord,iWordLen,iNumOfWords)] == "g":
                    lRequiredLetters.append(sLetters[CoordsToStringIndex(x,yCoord,iWordLen,iNumOfWords)]) #add the greens in case there's a double letter
                if x % 2 == 1: #odd x: 1,3: If it's yellow, it HAS to be in this word
                    if sColors[CoordsToStringIndex(x,yCoord,iWordLen,iNumOfWords)] == "y":
                        lRequiredLetters.append(sLetters[CoordsToStringIndex(x,yCoord,iWordLen,iNumOfWords)])
            newWordlist = reduce_Wordlist(l_HorizontalAnswers[AnswerListIndex], [], lRequiredLetters, sRegex)
            if not newWordlist == l_HorizontalAnswers[AnswerListIndex]:
                    DirtyBit = True
                    l_HorizontalAnswers[AnswerListIndex].clear()
                    DeepExtend(l_HorizontalAnswers[AnswerListIndex],newWordlist)
        #vertical words
        for AnswerListIndex in range(iNumOfWords):
            xCoord = AnswerListIndex * 2
            sRegex = ""
            lRequiredLetters = []
            for y in range(wordLen):
                lPossibleLetters = PossibleLettersAtLocation(xCoord,y,sLetters,sColors,lHorizLetters,lVertLetters,l_HorizontalAnswers,l_VerticalAnswers,lUnHomed)
                if not lPossibleLetters == []: #this shouldn't ever be true, but *shrug*
                    sRegex+="["
                    for i in range(len(lPossibleLetters)):
                        sRegex+= lPossibleLetters[i]
                    sRegex+="]"
                    if len(lPossibleLetters) == 1:
                        lAffectedWords = CoordsToWordIndex(xCoord,y,iWordLen,iNumOfWords)
                        if lAffectedWords[0][0] != None:
                            lHorizLetters[lAffectedWords[0][0]][lAffectedWords[0][1]] = lPossibleLetters[0]
                        if lAffectedWords[1][0] != None:
                            lVertLetters[lAffectedWords[1][0]][lAffectedWords[1][1]] = lPossibleLetters[0]
                else:
                    print("ERROR!")
                    raise RuntimeError("There are no possible letters found at ["+str(xCoord)+","+str(y)+"]")
                if y % 2 == 1: #odd y: 1,3: If it's yellow, it HAS to be in this word
                    if sColors[CoordsToStringIndex(xCoord,y,iWordLen,iNumOfWords)] == "y":
                        lRequiredLetters.append(sLetters[CoordsToStringIndex(xCoord,y,iWordLen,iNumOfWords)])
            newWordlist = reduce_Wordlist(l_VerticalAnswers[AnswerListIndex], [], lRequiredLetters, sRegex)
            if not newWordlist == l_VerticalAnswers[AnswerListIndex]:
                    DirtyBit = True
                    l_VerticalAnswers[AnswerListIndex].clear()
                    DeepExtend(l_VerticalAnswers[AnswerListIndex],newWordlist)
    #done reducing: do some cleanup:
    #write out all known letters:
    SetKnownLetters(l_HorizontalAnswers,l_VerticalAnswers, lHorizLetters, lVertLetters)

def BitListInc(BitList:list[int],MaxValues:list[int]) -> list:
    """Increments Bitlist like a binary counter, but MaxValues holds the (noninclusive) maximum for each position"""
    BitList[len(BitList)-1] += 1
    for i in range(len(BitList)-1,0,-1):
        if BitList[i] >= MaxValues[i]:
            BitList[i] = 0
            BitList[i-1] += 1
    if BitList[0] >= MaxValues[0]:
        #Overflow!
        BitList[0] = 0
        return None
    return BitList

def ReduceByPlaying_Extensible(sLetters:str,l_HorizontalAnswers:list,l_VerticalAnswers:list,lHorizLetters:list,lVertLetters:list):
    """Will try to see what combinations are actually possible and removing the words that aren't"""
    iWordLen = len(l_HorizontalAnswers[0][0])
    iNumOfWords = len(l_HorizontalAnswers)
    AllLetters = []
    for i in range(len(sLetters)):
        AllLetters.append(sLetters[i])
    lHorizAnsReduced = [[] for i in range(len(l_HorizontalAnswers))]
    lVertAnsReduced = [[] for i in range(len(l_VerticalAnswers))]
    RI = [0]*iNumOfWords
    CI = [0]*iNumOfWords
    RIMax = []
    for i in range(len(l_HorizontalAnswers)):
        RIMax.append(len(l_HorizontalAnswers[i]))
    CIMax = []
    for i in range(len(l_VerticalAnswers)):
        CIMax.append(len(l_VerticalAnswers[i]))

    while RI != None:
        tempFreeLetters = []
        DeepExtend(tempFreeLetters,AllLetters)
        try:
            for i in range(len(RI)):
                for char in l_HorizontalAnswers[i][RI[i]]:
                    del tempFreeLetters[tempFreeLetters.index(char)]
            for i in range(len(CI)):
                for r in range(len(l_VerticalAnswers[i][CI[i]])):
                                    if r % 2 == 1: 
                                        char = l_VerticalAnswers[i][CI[i]][r]
                                        del tempFreeLetters[tempFreeLetters.index(char)] #only delete the odd characters, as they're unaccounted for elsewhere
                                    else:
                                        lAffectedSections = CoordsToWordIndex(i*2,r,iWordLen,iNumOfWords)
                                        WordCheck = RI[lAffectedSections[0][0]]
                                        if l_VerticalAnswers[i][CI[i]][r] != l_HorizontalAnswers[lAffectedSections[0][0]][WordCheck][lAffectedSections[0][1]]:
                                            raise ValueError("This play is not possible.")
            #if we get here, that means this set of words is a valid play
            for i in range(len(RI)):
                lHorizAnsReduced[i].append(l_HorizontalAnswers[i][RI[i]])
            for i in range(len(CI)):
                lVertAnsReduced[i].append(l_VerticalAnswers[i][CI[i]])
        except:
            pass
        #do the incrementing
        CI = BitListInc(CI,CIMax)
        if CI == None:
            CI = [0]*iNumOfWords
            RI = BitListInc(RI,RIMax)

    #at this point, we know the valid plays
    #dedupe the lists
    for i in range(len(lHorizAnsReduced)):
        lHorizAnsReduced[i] = list(set(lHorizAnsReduced[i]))
        l_HorizontalAnswers[i].clear()
        DeepExtend(l_HorizontalAnswers[i],lHorizAnsReduced[i])
    for i in range(len(lVertAnsReduced)):
        lVertAnsReduced[i] = list(set(lVertAnsReduced[i]))
        l_VerticalAnswers[i].clear()
        DeepExtend(l_VerticalAnswers[i],lVertAnsReduced[i])
    SetKnownLetters(l_HorizontalAnswers,l_VerticalAnswers, lHorizLetters, lVertLetters)

def SetKnownLetters(l_HorizontalAnswers:list[str], l_VerticalAnswers:list[str], lHorizLetters:list[str], lVertLetters:list[str]):
    iNumOfWords = len(l_HorizontalAnswers)
    iWordLen = len(l_HorizontalAnswers[0][0])
    for WordListIndex in range(iNumOfWords):
        if len(l_HorizontalAnswers[WordListIndex]) == 1:
            y = WordListIndex * 2
            for x in range(iWordLen):
                lAffectedWords = CoordsToWordIndex(x,y,iWordLen,iNumOfWords)
                if lAffectedWords[0][0] != None:
                    lHorizLetters[lAffectedWords[0][0]][lAffectedWords[0][1]] = l_HorizontalAnswers[WordListIndex][0][x]
                if lAffectedWords[1][0] != None:
                    lVertLetters[lAffectedWords[1][0]][lAffectedWords[1][1]] = l_HorizontalAnswers[WordListIndex][0][x]
        if len(l_VerticalAnswers[WordListIndex]) == 1:
            x = WordListIndex * 2
            for y in range(iWordLen):
                lAffectedWords = CoordsToWordIndex(x,y,iWordLen,iNumOfWords)
                if lAffectedWords[0][0] != None:
                    lHorizLetters[lAffectedWords[0][0]][lAffectedWords[0][1]] = l_VerticalAnswers[WordListIndex][0][y]
                if lAffectedWords[1][0] != None:
                    lVertLetters[lAffectedWords[1][0]][lAffectedWords[1][1]] = l_VerticalAnswers[WordListIndex][0][y]

def SolutionAsString(l_HorizLetters:list[str],l_VertLetters:list[str]) -> str:
    sOutput = ""
    iWordLen = len(l_HorizLetters[0])
    iNumOfWords = len(l_HorizLetters)
    for Row in range(iWordLen):
        if Row % 2 == 0: #even row, full length
            for i in range(len(l_HorizLetters[Row//2])):
                sOutput += l_HorizLetters[Row//2][i]
        else: #odd row, only vertical fills
            for i in range(iNumOfWords):
                sOutput += l_VertLetters[i][Row]
    return sOutput

def GetPerfectSwaps(lCurrentState:list[str], sTarget:str) -> list[int,int]:
    lReturnList = []
    for i in range(len(lCurrentState)-1): #no point in checking the last one, it was already checked against everyone else
        if lCurrentState[i] != sTarget[i] and sTarget[i] != ".":
            wantedChar = sTarget[i]
            haveChar = lCurrentState[i]
            #get all possibilities
            for j in range(i+1,len(lCurrentState)): #only look forward. if it was behind us it would've been found already
                if lCurrentState[j] != sTarget[j]: #unlocked char
                        if lCurrentState[j] == wantedChar and sTarget[j] == haveChar: #obvious swap, they belong in each other's spot
                            newSwap = [i,j]
                            newSwapReverse = [j,i]
                            if not (newSwap in lReturnList or newSwapReverse in lReturnList): #already know this swap
                                lReturnList.append(newSwap)
    return lReturnList

def GetOnlyOccuranceSwaps(lCurrentState:list[str], sTarget:str) -> list[int,int]:
    #Returns a list of swaps that only one letter of that kind is movable
    lReturnList = []
    lOutOfPlaceLetters = []
    for i in range(len(lCurrentState)):
        if lCurrentState[i] != sTarget[i]:
            lOutOfPlaceLetters.append(lCurrentState[i])

    for i in range(len(lOutOfPlaceLetters)):
        if lOutOfPlaceLetters.count(lOutOfPlaceLetters[i]) == 1:
            index = lCurrentState.index(lOutOfPlaceLetters[i])
            while lCurrentState[index] == sTarget[index]: #if this index is actually solved
                    index = lCurrentState.index(lOutOfPlaceLetters[i],index+1) #find the next index

            if sTarget[index] != ".":
                haveChar = lCurrentState[index]
                #there's only one place it can go if we get here, so just find it
                iIndexToPut = sTarget.index(haveChar)
                while lCurrentState[iIndexToPut] == sTarget[iIndexToPut]: #in case there's multiple letters, but this is the only unlocked one
                    iIndexToPut = sTarget.index(haveChar,iIndexToPut+1) #find the next index
                #index found. prepare the swap.
                newSwap = [index,iIndexToPut]
                newSwapReverse = [iIndexToPut,index]
                if not (newSwap in lReturnList or newSwapReverse in lReturnList): #already know this swap. Shouldn't be possible, but whatevs
                    lReturnList.append(newSwap)
    return lReturnList

def GetAllSwaps(lCurrentState:list[str], sTarget:str) -> list[int,int]:
    lSwaps = []
    for i in range(len(lCurrentState)-1):
        if lCurrentState[i] != sTarget[i] and sTarget[i] != ".":
            wantedChar = sTarget[i]
            haveChar = lCurrentState[i]
            #l_Indexes = []
            
            for j in range(i+1,len(lCurrentState)):
                if lCurrentState[j] == wantedChar and sTarget[j] != wantedChar: #this is an out of place character and it's a character we're looking for
                    newSwap = [i,j]
                    newSwapReverse = [j,i]
                    if not (newSwap in lSwaps or newSwapReverse in lSwaps): #already know this swap
                        lSwaps.append(newSwap)
                    #l_Indexes.append(j)

            #for k in range(len(l_Indexes)):
            #    newSwap = [i,l_Indexes[k]]
            #    newSwapReverse = [l_Indexes[k],i]
            #    if not (newSwap in lSwaps or newSwapReverse in lSwaps): #already know this swap
            #        lSwaps.append(newSwap)
            #
            #    if sTarget[l_Indexes[k]] == haveChar: #obvious swap, they belong in each other's spot
            #        newSwap = [i,l_Indexes[k]]
            #        newSwapReverse = [l_Indexes[k],i]
            #        if not (newSwap in lSwaps or newSwapReverse in lSwaps): #already know this swap
            #            lSwaps.append(newSwap)
            #    elif sTarget[l_Indexes[k]] == ".":
            #        #Swap is indeterminate, don't do it yet.
            #        pass
            #    elif len(l_Indexes) == 1: #or (k == len(l_Indexes)-1):
            #        #kinda have to make this swap. it's the only possible option, or we've tried all the others.
            #        newSwap = [i,l_Indexes[k]]
            #        newSwapReverse = [l_Indexes[k],i]
            #        if not (newSwap in lSwaps or newSwapReverse in lSwaps): #already know this swap
            #            lSwaps.append(newSwap)
    return lSwaps

def GetPossibleSwaps_NoBoardState(lCurrentState:list[str], sTarget:str) -> list[int,int]:
    #check for perfect swaps, if none, find last resort swaps, if none, then you can feed them garbage.
    lReturnList = [] #[fromIndex,ToIndex] for each index
    lReturnList = GetPerfectSwaps(lCurrentState, sTarget)
    if len(lReturnList) > 0:
        return lReturnList
    #only get here if there's no perfect swaps left
    lReturnList = GetOnlyOccuranceSwaps(lCurrentState, sTarget)
    if len(lReturnList) > 0:
        return lReturnList
    #Finally: we must acept our fate and return any swap that works
    lReturnList = GetAllSwaps(lCurrentState, sTarget)
    return lReturnList

def BFS_SP(graph:dict[int,list], start:int, goal:int) ->list[int]:
    explored = []
     
    # Queue for traversing the
    # graph in the BFS
    queue = [[start]]
     
    # If the desired node is
    # reached
    if start == goal:
        return [start]
     
    # Loop to traverse the graph
    # with the help of the queue
    while queue:
        path = queue.pop(0)
        node = path[-1]
         
        # Condition to check if the
        # current node is not visited
        if node not in explored:
            neighbours = graph[node]
             
            # Loop to iterate over the
            # neighbours of the node
            for neighbour in neighbours:
                new_path = list(path)
                new_path.append(neighbour)
                queue.append(new_path)
                 
                # Condition to check if the
                # neighbour node is the goal
                if neighbour == goal:
                    return new_path
            explored.append(node)
 
    # Condition when the nodes
    # are not connected
    return None

def GetMinimumSwaps_graph_NBS(sLetters:str,l_HorizLetters:list[str],l_VertLetters:list[str]) -> list[int,int,str,int,int,str]:
    #have a set representing the connections
    #have a set of arrays holding the swaps, the current total cost, and the array setup at the moment.
    #if the array setup isn't the answer, add more options to it
    #once all nodes have been processed to their options or are a complete state, find the one with the lowest cost.
    #Follow the graph backwards to find the list of swaps neccesary
    iWordLen = len(l_HorizLetters[0])
    iNumOfWords = len(l_HorizLetters)
    sTarget = SolutionAsString(l_HorizLetters,l_VertLetters)
    lBoardState = []
    lTarget = []
    for char in sLetters:
        lBoardState.append(char)
    for char in sTarget:
        lTarget.append(char)
    
    #states = [[startingarray],[boardstate1]]
    #swaps = [[FromIndex,ToIndex],[FromIndex, ToIndex]]
    #setConnections = {0:[1,2],1:[2],2:[]}
    #setSwapIndexes = {0:[0,1],1:[2],2:[]} #0 connects to state[1] via swap[0] and state[2] via swap[1], 1 connects to state[2] via swap[2]
    setConnections = {0:[]}
    setSwapIndexes = {0:[]}
    lStates = deque()
    lStates.append(lBoardState)
    #for char in lBoardState:
    #    lStates[0].append(char) #Wish I could've just said lStates = [lBoardState], but that makes a shallow copy that causes problems :D
    lSwaps = deque()
    qToBeProcessed = deque([0])
    goalIndex = None
    #iNextBigWarn = 0
    #LastUpdateConnections = 0
    #LastUpdateTime = time.time()
    while len(qToBeProcessed):
            #if len(qToBeProcessed) > 200 and iNextBigWarn <= 0:
            #    print("\n")
            #    print("Queue is",len(qToBeProcessed),"items long now.")
            #    print(len(setConnections),"unique states have been found.")
            #    timeElapsed = time.time()-LastUpdateTime
            #    CurrConnections = 0
            #    for lis in setConnections:
            #        CurrConnections += len(setConnections[lis])
            #    NewConnections = CurrConnections - LastUpdateConnections
            #    print(NewConnections,"new connections.")
            #    print("(~",NewConnections/timeElapsed,"new connections/sec)")
            #    LastUpdateTime = time.time()
            #    LastUpdateConnections = CurrConnections
            #    iNextBigWarn = len(qToBeProcessed)//4
            #elif iNextBigWarn >= 1:
            #    iNextBigWarn -= 1

            iCurrentNode = qToBeProcessed.popleft() #FIFO
            #while qToBeProcessed.count(iCurrentNode): #in case it got added multiple times. Shouldn't be possible, but... eh. It also adds another 2% to the processing time, so I'm removing it.
            #    print("Duplicate Removed.")
            #    qToBeProcessed.remove(iCurrentNode)
            #lPossibleMoves = GetPossibleSwaps_NoBoardState(lStates[iCurrentNode],sTarget)
            #instead of calling the function, I've brought it in to do a bit more to it:
            lPossibleMoves = GetPerfectSwaps(lStates[iCurrentNode], sTarget)
            if len(lPossibleMoves) > 0:
                #only use one perfect swap so it can't balloon out. Verify the coords don't damage other perfect swaps if possible.
                #if the length is just one, it should pass right through.
                if len(lPossibleMoves) > 1:
                    #lAllSwapSpots = []
                    #for i in range(len(lPossibleMoves)):
                    #    lAllSwapSpots.append(lPossibleMoves[i][0])
                    #    lAllSwapSpots.append(lPossibleMoves[i][1])
                    #selectedSwap = []
                    #for i in range(len(lPossibleMoves)):
                    #    iFrom = lPossibleMoves[i][0]
                    #    iTo = lPossibleMoves[i][1]
                    #    if lAllSwapSpots.count(iFrom) == 1 and lAllSwapSpots.count(iTo) == 1:
                    #        break
                    ##When the code gets here: it either found a non-interferring swap, OR it's the last swap in the list, and none were non-interferring. Either way, just take it.
                    #all that code was removed because: by the time it gets here from smart solve, ALL new perfect swaps will be interferring since only one move is made at a time, so only one perfect swap can reveal itself.
                    lPossibleMoves = [lPossibleMoves[0]] #make it the only swap. 
            
            else:
                #only get here if there's no perfect swaps left
                lPossibleMoves = GetOnlyOccuranceSwaps(lStates[iCurrentNode], sTarget)
                if len(lPossibleMoves) == 0:
                    #Finally: we must acept our fate and return any swap that works
                    lPossibleMoves = GetAllSwaps(lStates[iCurrentNode], sTarget)


            lScratchState = []
            lScratchState = copy.deepcopy(lStates[iCurrentNode])
            #DeepExtend(lScratchState,lStates[iCurrentNode])
            for move in lPossibleMoves:
                swapIndex = None
                stateIndex = None

                #get swapIndex
                swapOrder1 = [move[0],move[1]]
                swapOrder2 = [move[1],move[0]]
                if swapOrder1 in lSwaps:
                    swapIndex = lSwaps.index(swapOrder1)
                elif swapOrder2 in lSwaps:
                    swapIndex = lSwaps.index(swapOrder2)
                else:
                    swapIndex = len(lSwaps)
                    lSwaps.append(swapOrder1)

                #get stateIndex
                LetterFrom = lScratchState[move[0]]
                LetterTo = lScratchState[move[1]]
                lScratchState[move[0]] = LetterTo
                lScratchState[move[1]] = LetterFrom
                if lScratchState in lStates:
                    stateIndex = lStates.index(lScratchState)
                else:
                    lTempState = copy.deepcopy(lScratchState)
                    #DeepExtend(lTempState,lScratchState)
                    stateIndex = len(lStates)
                    lStates.append(lTempState)
                if lScratchState == lTarget and goalIndex == None:
                    print("Goal Found!")
                    goalIndex = stateIndex
                #fix the state back to original
                lScratchState[move[1]] = LetterTo
                lScratchState[move[0]] = LetterFrom
                
                #now fill in the connections.
                setConnections[iCurrentNode].append(stateIndex) #we now know this node can find this new state
                setSwapIndexes[iCurrentNode].append(swapIndex) #via this swap
                if setConnections.get(stateIndex) == None:
                    #this state didn't exist before. add it.
                    setConnections[stateIndex] = []
                    setSwapIndexes[stateIndex] = []
                    #set it to be searched eventually:
                    qToBeProcessed.append(stateIndex)
                #the reverse is also true
                setConnections[stateIndex].append(iCurrentNode)
                setSwapIndexes[stateIndex].append(swapIndex)
    #using this graph, find the fastest path through it
    solution = BFS_SP(setConnections, 0, goalIndex)
    #now make that list of states into something usable.
    SolutionSwaps = []
    LastState = 0
    for i in range(1,len(solution)):
        swapNum = setConnections[LastState].index(solution[i])
        fromIndex = lSwaps[setSwapIndexes[LastState][swapNum]][0]
        toIndex = lSwaps[setSwapIndexes[LastState][swapNum]][1]

         #always make sure the "from" info is going to make the green. Looks more natural.
        if not sTarget[toIndex] == lBoardState[fromIndex]: #it shouldn't be 0 to 1, should be 1 to 0
            #swap the info
            fromIndex = lSwaps[setSwapIndexes[LastState][swapNum]][1]
            toIndex = lSwaps[setSwapIndexes[LastState][swapNum]][0]
           
        fromCoords = LetterIndextoGeneralCoords(fromIndex,iWordLen,iNumOfWords)
        toCoords = LetterIndextoGeneralCoords(toIndex,iWordLen,iNumOfWords)
        fromChar = lBoardState[fromIndex]
        toChar = lBoardState[toIndex]

        SolutionSwaps.append([fromCoords[0],fromCoords[1],fromChar,toCoords[0],toCoords[1],toChar])
        lBoardState[fromIndex] = toChar
        lBoardState[toIndex] = fromChar
        LastState = solution[i]
    return SolutionSwaps

def SmartSolve(sLetters:str,l_HorizLetters:list,l_VertLetters:list) -> list[int,int,str,int,int,str]:
    #Iterative solving:
    #do perfect swaps, do neccesary swaps, check for perfect swaps again, THEN feed it to the graph solver

    iWordLen = len(l_HorizLetters[0])
    iNumOfWords = len(l_HorizLetters)
    sTarget = SolutionAsString(l_HorizLetters,l_VertLetters)
    lBoardState = []
    lTarget = []
    for char in sLetters:
        lBoardState.append(char)
    for char in sTarget:
        lTarget.append(char)
    lSwaps = []

    bMorePossibleSwaps = True
    iPerf = 0
    iLastResort = 0

    while bMorePossibleSwaps:
        bMorePossibleSwaps = False
        #perfect swaps:
        lTemp = GetPerfectSwaps(lBoardState, sTarget)
        while len(lTemp) > 0:
            bMorePossibleSwaps = True
            iPerf += len(lTemp)
            #populate those perfect swaps, making sure to verify they're good (it's possible a previous perfect swap invalidates a different one)
            for i in range(len(lTemp)):
                fromIndex = lTemp[i][0]
                toIndex = lTemp[i][1]
                if lBoardState[fromIndex] != lTarget[fromIndex] and lBoardState[toIndex] != lTarget[toIndex]: #both places are unlocked
                    if lBoardState[fromIndex] == lTarget[toIndex] and lBoardState[toIndex] == lTarget[fromIndex]: #but they want to be where the other is
                        #perform the swap
                        fromCoords = LetterIndextoGeneralCoords(fromIndex,iWordLen,iNumOfWords)
                        toCoords = LetterIndextoGeneralCoords(toIndex,iWordLen,iNumOfWords)
                        fromChar = lBoardState[fromIndex]
                        toChar = lBoardState[toIndex]

                        lSwaps.append([fromCoords[0],fromCoords[1],fromChar,toCoords[0],toCoords[1],toChar])

                        lBoardState[fromIndex] = toChar
                        lBoardState[toIndex] = fromChar
            #in case there was any error, check if there's new perfect swaps to perform
            lTemp = GetPerfectSwaps(lBoardState, sTarget)

        #Swaps of last resort:
        lTemp = GetOnlyOccuranceSwaps(lBoardState, sTarget)
        if len(lTemp)>0:
            iLastResort += 1
            bMorePossibleSwaps = True
        
            #populate those swaps, making sure to verify they're good (it's possible a previous swap invalidates a different one)
            #one at a time, in case they reveal a perfect swap
            i=0
            fromIndex = lTemp[i][0]
            toIndex = lTemp[i][1]
            if lBoardState[fromIndex] != lTarget[fromIndex] and lBoardState[toIndex] != lTarget[toIndex]: #both places are unlocked
                if lBoardState[fromIndex] == lTarget[toIndex] or lBoardState[toIndex] == lTarget[fromIndex]: #but one wants to be where the other is
                    #find which one is going to turn green and make it the "from" coord.
                    if lBoardState[fromIndex] == lTarget[toIndex]:
                        fromCoords = LetterIndextoGeneralCoords(fromIndex,iWordLen,iNumOfWords)
                        toCoords = LetterIndextoGeneralCoords(toIndex,iWordLen,iNumOfWords)
                        fromChar = lBoardState[fromIndex]
                        toChar = lBoardState[toIndex]
                    else:
                        fromCoords = LetterIndextoGeneralCoords(toIndex,iWordLen,iNumOfWords)
                        toCoords = LetterIndextoGeneralCoords(fromIndex,iWordLen,iNumOfWords)
                        fromChar = lBoardState[toIndex]
                        toChar = lBoardState[fromIndex]

                    #perform the swap
                    lSwaps.append([fromCoords[0],fromCoords[1],fromChar,toCoords[0],toCoords[1],toChar])
                    lBoardState[fromIndex] = toChar
                    lBoardState[toIndex] = fromChar
        #we loop back at this point, search for perfects, then search for more last resorts

    print(iPerf,"perfect swaps and",iLastResort,"last resort swaps found.")
    #all obvious swaps have been performed. Send it to the graph solver. CORRECTION: if it hasn't already been solved. Which I found out sometimes it can be
    sNewBoardState = ""
    for letter in lBoardState:
        sNewBoardState+=letter
    if sNewBoardState != sTarget: #verify it's not already solved
        print("Sending reduced problem to graph solver.")
        lTemp = GetMinimumSwaps_graph_NBS(sNewBoardState,l_HorizLetters,l_VertLetters)
        lSwaps.extend(lTemp)
    return lSwaps


     



    



#program
if __name__ == '__main__':
    #cProfile.run("GetMinimumSwaps_graph('cininraiaeuaatretsacdstfrminespeuceliret',[['finance'], ['actress'], ['termite'], ['culprit']],[['frantic'], ['natural'], ['needier'], ['easiest']],[['f', 'i', 'n', 'a', 'n', 'c', 'e'], ['a', 'c', 't', 'r', 'e', 's', 's'], ['t', 'e', 'r', 'm', 'i', 't', 'e'], ['c', 'u', 'l', 'p', 'r', 'i', 't']],[['f', 'r', 'a', 'n', 't', 'i', 'c'], ['n', 'a', 't', 'u', 'r', 'a', 'l'], ['n', 'e', 'e', 'd', 'i', 'e', 'r'], ['e', 'a', 's', 'i', 'e', 's', 't']])")
    #cProfile.run("GetMinimumSwaps_graph_NBS('cininraiaeuaatretsacdstfrminespeuceliret',[['f', 'i', 'n', 'a', 'n', 'c', 'e'], ['a', 'c', 't', 'r', 'e', 's', 's'], ['t', 'e', 'r', 'm', 'i', 't', 'e'], ['c', 'u', 'l', 'p', 'r', 'i', 't']],[['f', 'r', 'a', 'n', 't', 'i', 'c'], ['n', 'a', 't', 'u', 'r', 'a', 'l'], ['n', 'e', 'e', 'd', 'i', 'e', 'r'], ['e', 'a', 's', 'i', 'e', 's', 't']])")
    #cProfile.run("SmartSolve('ceninraitcuaatretsacestfrminespiuaelired',[['f', 'i', 'n', 'a', 'n', 'c', 'e'], ['a', 'c', 't', 'r', 'e', 's', 's'], ['t', 'e', 'r', 'm', 'i', 't', 'e'], ['c', 'u', 'l', 'p', 'r', 'i', 't']],[['f', 'r', 'a', 'n', 't', 'i', 'c'], ['n', 'a', 't', 'u', 'r', 'a', 'l'], ['n', 'e', 'e', 'd', 'i', 'e', 'r'], ['e', 'a', 's', 'i', 'e', 's', 't']])")
    
    FirstLoop = True
    l_HorizontalAnswers = [[["First"],["Loop"]]]
    l_VerticalAnswers = [[["First"],["Loop"]]]

    while(AreWeDoneYet(l_HorizontalAnswers,l_VerticalAnswers) == False):
        print("\n")
        s_Waffle = input("Enter Your setup: ").lower()
        s_Colors = input("Enter the colors for them (G=Green, Y=Yellow, .=White): ").lower()
        if FirstLoop:
            #Deluxe Waffle settings
            #s_Waffle 5x5 length = 21
                #5x3 + 3x2
            #s_Waffle 7x7 length = 40
                #7x4 + 4x3
                #general: wordlen*ciel(wordlen/2) + ciel(wordlen/2)*floor(wordlen/2)
                    #or: wordlen*ciel(wordlen/2) + floor((wordlen/2)^2)
            #9x9 = 45+20 = 65
            #sLength = x*ciel(x/2)+ciel(x/2)*floor(x/2)
            #sLen = WordLen*NumOfWords + NumOfWords*(Wordlen//2)
            #sLen = NumOfWords(WordLen + WordLen//2)
            # =NumOfWords((WordLen * 1.5)-0.5)
            #sLen/NumOfWords = (1.5*WordLen)-0.5
            #NumOfWords = 2*sLen/(3*WordLen - 1)
            #NumOfWords = 2*WordLen - 1
            #WordLen = 1/3(2*sqrt(3*sLen+1)-1)

            #max number of swaps:
                #5x5=10
                #7x7=20
                #10+((WordLen-5)*5)


            iSLength = len(s_Waffle)
            wordLen = ceil(2*sqrt(3*iSLength + 1)-1)//3 #it should be x.0 anyways, but we can't have a float floating around.
            #wordLen = 3*iSLength
            #wordLen += 1
            #wordLen = 2*sqrt(wordLen)
            #wordLen -= 1
            #wordLen = wordLen//3 #broken up if the runtime doesn't compute properly

            NumberOfWords = ceil(wordLen/2)
            iMaxSwaps = 10+((wordLen-5)*5)

            print("That looks like",NumberOfWords,"horizontal words, each",wordLen,"characters long, and up to",iMaxSwaps,"Swaps!")

            #bDeluxe = True
            #if bDeluxe:
            #    wordLen = 7
            #    NumberOfWords = 4
            l_HorizontalAnswers = [[] for i in range(NumberOfWords)]
            l_VerticalAnswers = [[] for i in range(NumberOfWords)]
            l_VerticalKnownLetters = [["."] * wordLen for i in range(NumberOfWords)]
            l_HorizontalKnownLetters = [["."] * wordLen for i in range(NumberOfWords)]

            build_dictionary(wordLen,bannedChars)
            #lists loaded. Fill the lists.
            for i in range(NumberOfWords):
                DeepExtend(l_HorizontalAnswers[i],l_AllWords)
                DeepExtend(l_VerticalAnswers[i],l_AllWords)
            FirstLoop = False

        try:
            SetLetters(s_Waffle,s_Colors,l_HorizontalKnownLetters,l_VerticalKnownLetters,l_FullyUnhomedLetters)
        except:
            print("Those lists need to be the same length")
            continue
        
        startTime = time.time()
        print("Solving waffle...")
        ReducePossibleWords(s_Waffle,s_Colors,l_HorizontalKnownLetters,l_VerticalKnownLetters,l_HorizontalAnswers,l_VerticalAnswers,l_FullyUnhomedLetters)
        ReduceByPlaying_Extensible(s_Waffle,l_HorizontalAnswers,l_VerticalAnswers,l_HorizontalKnownLetters,l_VerticalKnownLetters)
        print("Waffle solved in ",time.time()-startTime)

        print("Horizontal words:")
        for i in range(len(l_HorizontalAnswers)):
            if len(l_HorizontalAnswers[i]) > 1:
                print("Row "+str(i+1)+": "+str(len(l_HorizontalAnswers[i]))+" words remaining.")
                if len(l_HorizontalAnswers[i]) < 15:
                    print(str(l_HorizontalAnswers[i]))
            else:
                print("Row "+str(i+1)+" answer: "+str(l_HorizontalAnswers[i][0]))
        print("\n")
        print("Vertical words:")
        for i in range(len(l_VerticalAnswers)):
            if len(l_VerticalAnswers[i]) > 1:
                print("Column "+str(i+1)+": "+str(len(l_VerticalAnswers[i]))+" words remaining.")
                if len(l_VerticalAnswers[i]) < 15:
                    print(str(l_VerticalAnswers[i]))
            else:
                print("Column "+str(i+1)+" answer: "+str(l_VerticalAnswers[i][0]))

        print("\n")
        print("Known Letters:")
        DisplayWaffle(l_HorizontalKnownLetters,l_VerticalKnownLetters)

        gc.disable() #speeds this section up by a decent margin!
        startTime = time.time()
        print("Starting Smart Solver...")
        l_Swaps = SmartSolve(s_Waffle,l_HorizontalKnownLetters,l_VerticalKnownLetters)
        print("Smart Solver took ",time.time()-startTime)
        gc.enable()
        
        if (len(l_Swaps) > iMaxSwaps):
            print("WARNING: this is "+str(len(l_Swaps))+" swaps!")
        else:
            print(str(len(l_Swaps))+" swaps proposed:")
        for i in range(len(l_Swaps)):
            print("Swap #"+str(i+1)+": \""+str(l_Swaps[i][2])+"\"("+str(l_Swaps[i][0]+1)+","+str(l_Swaps[i][1]+1)+") to \""+str(l_Swaps[i][5])+"\"("+str(l_Swaps[i][3]+1)+","+str(l_Swaps[i][4]+1)+")")

        for y in range(wordLen):
            for x in range(wordLen):
                lPossibleLetters = PossibleLettersAtLocation(x,y,s_Waffle,s_Colors,l_HorizontalKnownLetters,l_VerticalKnownLetters,l_HorizontalAnswers,l_VerticalAnswers,l_FullyUnhomedLetters)
                if len(lPossibleLetters)>1:
                    print("Possible Letters at ("+str(x)+","+str(y)+") :"+str(lPossibleLetters))

    print("Done!") #normally I'd print out the answer here, but that's already done.



#s_Waffle = "aplttdeeeeoddsgerrsny"
#s_Colors = "gy..g.ygy.g.....g...g"
#s_Waffle = "eeatslrtehuugloarntay"
#s_Colors = "g.yyg...y.g.y...g.gyg"
#s_Waffle = "scalkneletiafamnfigel"
#s_Colors = "gyg.g.y.y.gy.y.ygg..g"
#s_Waffle = "teerotmechuraordebtvt"
#s_Colors = "g.y.g..y..g...y.g.y.g"
#s_Waffle = "fsaefpteltsnofuntaury"
#s_Colors = "g...g.y...gyy.yggg..g"
#s_Waffle = "gacuelorrnlawloaymmay"
#s_Colors = "gyy.g..yy.gg..gyg..yg"
#s_Waffle = "mlnedtlrnidueooularoy"
#s_Colors = "g.y.gy...gg..y.yg.gyg"
#s_Waffle = "cldarahdxopeulivreeey"
#s_Colors = "g...g..y..g.y...g.y.g"
#s_Waffle = "stcaluwtlldeariaetelh"
#s_Colors = "g...g..yy.g.y...gyy.g"
#vertical Solution for ^ is "slate"
#100
#s_Waffle = "mmkoyeuiaomerropahcln"
#s_Colors = "g.y.g.y.ygg.y...g...g"
#101
#s_Waffle = "gbpptodennisewrasnerd"
#s_Colors = "g...gyyyy.g.g...gyg.g"
#118 (first I did)
#s_Waffle = "tcteebhrcetsotahoeolr"
#s_Colors = "g...g.y.ygg....ygyy.g"
#121
#s_Waffle = "peetdruaattloepvlaara"
#s_Colors = "g.y.g...y.gy....gg.yg"
#127
#s_Waffle = "vueieteiiimlivasdeotr"
#s_Colors = "gy..g...y.g..y.ygg.yg"
#128
#s_Waffle = "leaoriyaeeeeakkglatwn"
#s_Colors = "gyy.g..gygg...y.g.y.g"
#129
#s_Waffle = "clemhavsssiseurasdkry"
#s_Colors = "g.y.gyyyy.gg....gy..g"
#130 (5/31/22)
#s_Waffle = "mrteybdeenoieldrtnaad"
#s_Colors = "g.yyg...y.g.g.g.gyy.g"
#131
#s_Waffle = "spudyiumtoilmuwolpmoy"
#s_Colors = "g.y.gy.y.yg.g...gyg.g"
#142
#s_Waffle = "wmcrnaagoimtocaetoesh"
#s_Colors = "g...g.g.yygyy.y.g.y.g"
#144
#s_Waffle = "gdtldeqpriueeeaettreh"
#s_Colors = "g...gy.yyygyy...gy.yg"
#145
#s_Waffle = "adshdebglkaiurkomznae"
#s_Colors = "g.y.g..yy.g...gygy.yg"
#148
#s_Waffle = "feluslasnitrlltohaocy"
#s_Colors = "g.y.g.y.yygyy...g.y.g"
#150
#s_Waffle = "sidrntttaroaaannfcofy"
#s_Colors = "gy..g.y.gyg.y..gg.y.g"
#154
#s_Waffle = "pslaerooaucluuekasael"
#s_Colors = "gyyyg....ygy..g.g.y.g"
#159
#s_Waffle = "cvsdeaeaelphhmaftrsle"
#s_Colors = "g.y.gyyy.ggg..y.g.y.g"
#160
#s_Waffle = "rfulydjrdoodrixoeeepl"
#s_Colors = "g.y.g...y.g.yy.ygy.yg"
#164
#s_Waffle = "noaeevooesrolcpglishe"
#s_Colors = "g.y.gyyyyygyy...g.y.g"
#188
#s_Waffle = "eehacvavunltvsiherwey"
#s_Colors = "g.g.g.g.y.g.yy.ygy.yg"
#202
#s_Waffle = "nlacevdrideobleariany"
#s_Colors = "g.y.g.g.yygyy...g.y.g"
#203
#s_Waffle = "pelreegagndisugeleray"
#s_Colors = "g..ygy..yyg...gyggy.g"
#204
#s_Waffle = "camrmqeneauloolatlday"
#s_Colors = "gy.yg.y.y.g.yyyygy.yg"
#207
#s_Waffle = "dbluyiegladoeeritalld"
#s_Colors = "g.g.gyy...g.gy.ygyy.g"
#215
#s_Waffle = "fenedletltsiuraelipox"
#s_Colors = "g...gyyy.ygy.y.yg.y.g"
#218
#s_Waffle = "mleireaaenaeemrktkcon"
#s_Colors = "g.y.gg.gy.g.y...gyyyg"
#219
#s_Waffle = "gsnpyuvtmniotmuuetrry"
#s_Colors = "gyy.g...y.gy...ygy.gg"
#220
#s_Waffle = "tahleteeeeftudeihnrrr"
#s_Colors = "g.y.gygyy.g.y...g.y.g"
#221
#s_Waffle = "apemthspeoknraletnade"
#s_Colors = "ggy.g...yygy..gyg.y.g"
#222 (40% failure rate! - https://twitter.com/thatwafflegame/status/1565427900173672454 )
#s_Waffle = "singtraeeotolmfrlplso"
#s_Colors = "g.y.g...y.g.yyyyg...g"
#231
#s_Waffle = "mtottplaloolssidhrroy"
#s_Colors = "g...gyyg.gg.y...g.yyg"
#300
#s_Waffle = "agdrmlrueianeuloeibrr"
#s_Colors = "g.y.g.y..ygy.g.gg.y.g"
#335
#s_Waffle = "dbjurmgoerneafimgouey"
#s_Colors = "g...g.ygy.g.y.ygg.y.g"
#537
#s_Waffle = "nouddycioastlamoriral"
#s_Colors = "ggy.g...y.g.yyyyg..gg"
#538
#s_Waffle = "crdegdtlieirireirnoly"
#s_Colors = "g.y.gyyyyygyy...g.y.g"
#540
#s_Waffle = "mnlodlserainhugorbwuy"
#s_Colors = "gy.yg.g.y.g.y.y.gy.yg"
#541
#s_Waffle = "dratmuidRTIITTERoeepa"
#s_Colors = "g.yyg..yyyg..g..g.gyg"
#542
#s_Waffle = "rdnnneeneianiisangety"
#s_Colors = "g.y.gy.y.ygy.y.yg.g.g"
#543
#s_Waffle = "paueoivgwnolhnlaeknnt"
#s_Colors = "gy..g..y.ygyyg..g..gg"
#544
#s_Waffle = "zsyeyrokesatipenalbbs"
#s_Colors = "gyyygygyy.g.y...g.y.g"
#545
#s_Waffle = "daeinrtdcnepmecihigee"
#s_Colors = "gy.gg...y.gy.y.yg.yyg"
#547
#s_Waffle = "bneyhacmunicretettsha"
#s_Colors = "g.y.gyy..gg..yyygy.yg"
#548
#s_Waffle = "bzilerrtaratsaoalpeir"
#s_Colors = "gy.yg.y.yygyy...g.y.g"
#549
#s_Waffle = "SYIKFNEWLVOLAIFELRRYR"
#s_Colors = "g.gyg...y.g..y.gg.yyg"
#550
#s_Waffle = "cneocalalabemyioprmlr"
#s_Colors = "gy.ygyyyyygyy...g...g"

#s_Waffle = "peetdruaattloepvlaara"
#s_Colors = "g.y.g...y.gy....gg.yg"
#s_Waffle = "peetdruapetaltoalarva"
#s_Colors = "g.y.g...ggggg.y.ggggg"

#deluxe waffle: wordlen = 7, numofwords = 4
#s_Waffle = "dgentxrersottpaelssemlilosanenerlleecetd"
#s_Colors = "y.g.g.yyy..g.g.gygy...gygyg.g....yyg.gyy"
#s_Waffle = "sivroybdoctmsbotgrnsersdaiiserouuieesesu"
#s_Colors = "yyg.g.y....gygyg.g...ygyg.gyg..yyy.gyg.."
#Deluxe #5:
#s_Waffle = "ruorglcupugorttaaenhtrsephoutotruetsearh"
#s_Colors = "yyg.g..y...gyg.g.g...yg.g.gyg..y.yygygyy"
#Deluxe #6:
#s_Waffle = "cespnbsanesaeoatddsanirilrapemlenstdgeee"
#s_Colors = "yyg.gyyy..ygyg.gyg....g.g.g.gy..yy.g.g.y"
#Deluxe #9: (56% failure rate: https://twitter.com/thatwafflegame/status/1554936152184000518?s=20 )
#s_Waffle = "ceninraitcuaatretsacestfrminespiuaelired"
#s_Colors = "yygyg.yy...g.ggg.g..yyg.ggg.g......gyg.."
    #perfect swaps: cininraitcuaatretsacestfrminespeuaelired / ygg.g.yy...g.ggg.g..yyg.ggg.g..g...gyg..
    #to solve in ~5 seconds (instead of 39.36hrs - 220,954 STATES): cininraiaeuaatretsacdstfrminespeuceliret / ygg.g.yygg.g.ggg.g..gyg.ggg.g..g.g.gyg.g
#Deluxe #10:
#s_Waffle = "autasedrnionfrrafapdyeooieiynnivsenrpgoa"
#s_Colors = "y.g.g.yy...g.g.g.g.ggygyg.g.g....y.g.gyy"
#Deluxe #12:
#s_Waffle = "nesrfautegssaahitneplndtpmuaeluioolrbeer"
#s_Colors = "..g.gyy.y..g.g.gygyggyg.gyg.g....y.g.g.y"
#Deluxe #13:
#s_Waffle = "asiipeonlmsaecetrcsnegdrsmiaseminoaritda"
#s_Colors = "yyg.gy.y...g.ggg.g.y..g.ggg.g...y.yg.gyy"
#Deluxe #14:
#s_Waffle = "twsruldrlrferumiiedelelngroskueaabeevmrg"
#s_Colors = "y.gyg.y.yy.g.g.g.gy..yg.gyg.gy..y.yg.gy."
#Deluxe #15:
#s_Waffle = "maoxeyvuopsertvattvdsrerooiceartyrnrtnbn"
#s_Colors = "..g.g.y.y..gyg.g.g.ggyg.g.g.g...yyygyg.."
#Deluxe #25:
#s_Waffle = "mirtieibpnlatglleceanapsteeetuiexdnalsrn"
#s_Colors = "y.gygyy....g.g.gygygg.g.g.g.g...yy.gyg.."
#Deluxe #30:
#s_Waffle = "mllnpoelygyibpliadeoeoaeettlrnearaidsrrc"
#s_Colors = "..g.gyy...yg.ggg.gy.yyg.ggg.gy.yy..g.g.."
#Deluxe #59:
#s_Waffle = "uotsntidnxdelpvadnoprsenieeeteaeghlgetis"
#s_Colors = "y.g.gy..y.ygyg.g.g.gg.gyg.g.g..y.y.gygyy"
#Deluxe #60:
#s_Waffle = "memlidnvrcssbspeuteionaciateraerdvneoaci"
#s_Colors = ".yg.g.y....g.gggygyy..g.ggg.gy.yy..g.g.."
#Deluxe #61:
#s_Waffle = "negeapareordiippddafpelmterdlurateadrlte"
#s_Colors = "y.g.g...y.yg.ggg.gy.yyg.ggg.gyyyyy.gyg.y"

#Waffle royale - new: 6 total words, 2 are 7 letters long, 4 are 5 letters. it is the center words that are extra long.
#shape:
#      1
#  2 3 4 5 6
#  7   8   9
#0 1 2 3 4 5 6
#  7   8   9
#  0 1 2 3 4
#      5

#Royale 67
#s_Waffle = "idaeiogicigupacrnnglossee"
#s_Colors = "gg..yg.yyyy.g.y..y.g.y.gg"
#Royale 68 2023-07-17
#s_Waffle = "ealvissgumhiumdsphiereltg"
#s_Colors = "???" (5 green, 7 yellow)
#	"solution": "###D####AMISS##M#V#I#UPSURGE#L#L#H##EIGHT####E###",
#	"words": [
#		"AMISS",
#		"AMPLE",
#		"UPSURGE",
#		"DIVULGE",
#		"EIGHT",
#		"SIGHT"
#	],
#Royale 69 (nice) (2023-07-18)
#s_Waffle = "absorwieuaomdrelbetnayeyn"
#s_Colors = "gg.y.gyy.y...yy....g..ygg"
#Royale 71
#s_Waffle = "bsgsueetaahrurtodfeptsmsd"
#s_Colors = "gg.yyg...yyyg.y....g.y.gg"
#Royale 72
#s_Waffle = "lfnlxdirewgetehaioitneeli"
#s_Colors = ".g..yg..y..ygyy....gyy.gy"
#Royale 73
#s_Waffle = "safehgedmremndorgsieeboew"
#s_Colors = "gg.y.gy..yy..y..y..g..ygg"
#Royale 74
#s_Waffle = "psjvcenuaurniftiimneoutig"
#s_Colors = "gg.y.g.....yyyyyy..g.y.gg"
#Royale 75
#s_Waffle = "eobninlrnneotaiiaamegdbyn"
#s_Colors = "gg...g..yy..gyy....g.yygg"
#Royale 76
#s_Waffle = "erieitototbaloltehamtlsys"
#s_Colors = ???
#	"solution": "###A####ROBOT##E#O#E#TALLEST#L#I#T##MISTY####H###",
#	"words": [
#		"ROBOT",
#		"REALM",
#		"TALLEST",
#		"ABOLISH",
#		"MISTY",
#		"TESTY"
#	],
#	"green": 7,
#	"yellow": 7,