from collections import deque
import copy
import io
import re

#hardcoded variables
bannedChars = ["'","Å","â","ä","á","å","ç","é","è","ê","í","ñ","ó","ô","ö","ü","û","-"," "]
wordLen = 5
NumberOfWords = 3
#Deluxe Waffle settings
#wordLen = 7
#NumberOfWords = 4


#global variables
l_HorizontalAnswers = [[] for i in range(NumberOfWords)]
l_VerticalAnswers = [[] for i in range(NumberOfWords)]
l_FullyUnhomedLetters = []
l_AllKnownLetters = []

l_VerticalKnownLetters = [["."] * wordLen for i in range(NumberOfWords)]
l_HorizontalKnownLetters = [["."] * wordLen for i in range(NumberOfWords)]

l_AllWords = []

#functions block
def load_dict(file,StorageList):
    fileDict=io.open(file, mode="r", encoding="utf-8")
    dictionary = fileDict.readlines()
    dictsize = int(len(dictionary))
    StorageList += dictionary

def build_dictionary(wordLength,bannedCharacters):
    global l_AllWords

    #Load YAWL by Mendel Leo Cooper
    load_dict("Wordlists/YAWL.txt",l_AllWords)

    l_AllWords = optimize_wordlist(l_AllWords,wordLength,bannedCharacters)

    print("Answer list Loaded.")
    print("("+str(len(l_AllWords))+" words)")

def optimize_wordlist(wordList,wordLength,bannedCharacters) -> list:
    """
    Returns all words in \"wordList\" that are not \"wordLength\" characters long or contains any of \"bannedCharacters\"\n
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

def reduce_Wordlist(l_WordList, l_bannedChars = [], l_WantedLetters = [], s_Regex = "") -> list:
    """Takes in a list of words, and returns only the words that fit certain criteria"""
    newWords = []
    for word in l_WordList:
        if not any(bannedCharacter in l_bannedChars for bannedCharacter in word): #no banned letters
            if StrContainsAllLettersWithCount(word,l_WantedLetters): #all(needLetter in word for needLetter in neededLetters): #contains the letters we need
                if re.search(s_Regex, word):
                    newWords.append(word)
    return newWords

def StrContainsAllLettersWithCount(s_Word, l_Letters) -> bool:
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

def AreWeDoneYet(l_HorizontalWords, l_VerticalWords) -> bool:
    for i in range(len(l_HorizontalWords)):
        if len(l_HorizontalWords[i]) > 1:
            return False
    for i in range(len(l_VerticalWords)):
        if len(l_VerticalWords[i]) > 1:
            return False
    return True

def DisplayWaffle(l_HorizKnownLetters,l_VertKnownLetters) -> None:
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

def PossibleFunkyDingos(sLetters,sColors,iWordLen, iNumOfWords, xCoord, yCoord, FindChar = None) -> list:
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

def ReduceByPlaying(sLetters:str,l_HorizontalAnswers:list,l_VerticalAnswers:list,lHorizLetters:list,lVertLetters:list):
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
    
    for R0 in range(len(l_HorizontalAnswers[0])):
        for R1 in range(len(l_HorizontalAnswers[1])):
            for R2 in range(len(l_HorizontalAnswers[2])):
                for C0 in range(len(l_VerticalAnswers[0])):
                    for C1 in range(len(l_VerticalAnswers[1])):
                        for C2 in range(len(l_VerticalAnswers[2])):
                            tempFreeLetters = []
                            DeepExtend(tempFreeLetters,AllLetters)
                            try:
                                for char in l_HorizontalAnswers[0][R0]:
                                    del tempFreeLetters[tempFreeLetters.index(char)]
                                for char in l_HorizontalAnswers[1][R1]:
                                    del tempFreeLetters[tempFreeLetters.index(char)]
                                for char in l_HorizontalAnswers[2][R2]:
                                    del tempFreeLetters[tempFreeLetters.index(char)]
                                for i in range(len(l_VerticalAnswers[0][C0])):
                                    if i % 2 == 1: 
                                        char = l_VerticalAnswers[0][C0][i]
                                        del tempFreeLetters[tempFreeLetters.index(char)] #only delete the odd characters, as they're unaccounted for elsewhere
                                    else:
                                        lAffectedSections = CoordsToWordIndex(0,i,iWordLen,iNumOfWords)
                                        if lAffectedSections[0][0] == 0:
                                            WordCheck = R0
                                        elif lAffectedSections[0][0] == 1:
                                            WordCheck = R1
                                        elif lAffectedSections[0][0] == 2:
                                            WordCheck = R2
                                        if l_VerticalAnswers[0][C0][i] != l_HorizontalAnswers[lAffectedSections[0][0]][WordCheck][lAffectedSections[0][1]]:
                                            raise ValueError("This play is not possible.")
                                for i in range(len(l_VerticalAnswers[1][C1])):
                                    if i % 2 == 1: 
                                        char = l_VerticalAnswers[1][C1][i]
                                        del tempFreeLetters[tempFreeLetters.index(char)] #only delete the odd characters, as they're unaccounted for elsewhere
                                    else:
                                        lAffectedSections = CoordsToWordIndex(2,i,iWordLen,iNumOfWords)
                                        if lAffectedSections[0][0] == 0:
                                            WordCheck = R0
                                        elif lAffectedSections[0][0] == 1:
                                            WordCheck = R1
                                        elif lAffectedSections[0][0] == 2:
                                            WordCheck = R2
                                        if l_VerticalAnswers[1][C1][i] != l_HorizontalAnswers[lAffectedSections[0][0]][WordCheck][lAffectedSections[0][1]]:
                                            raise ValueError("This play is not possible.")
                                for i in range(len(l_VerticalAnswers[2][C2])):
                                    if i % 2 == 1: 
                                        char = l_VerticalAnswers[2][C2][i]
                                        del tempFreeLetters[tempFreeLetters.index(char)] #only delete the odd characters, as they're unaccounted for elsewhere
                                    else:
                                        lAffectedSections = CoordsToWordIndex(4,i,iWordLen,iNumOfWords)
                                        if lAffectedSections[0][0] == 0:
                                            WordCheck = R0
                                        elif lAffectedSections[0][0] == 1:
                                            WordCheck = R1
                                        elif lAffectedSections[0][0] == 2:
                                            WordCheck = R2
                                        if l_VerticalAnswers[2][C2][i] != l_HorizontalAnswers[lAffectedSections[0][0]][WordCheck][lAffectedSections[0][1]]:
                                            raise ValueError("This play is not possible.")
                                #if we get here, that means this set of words is a valid play
                                lHorizAnsReduced[0].append(l_HorizontalAnswers[0][R0])
                                lHorizAnsReduced[1].append(l_HorizontalAnswers[1][R1])
                                lHorizAnsReduced[2].append(l_HorizontalAnswers[2][R2])
                                lVertAnsReduced[0].append(l_VerticalAnswers[0][C0])
                                lVertAnsReduced[1].append(l_VerticalAnswers[1][C1])
                                lVertAnsReduced[2].append(l_VerticalAnswers[2][C2])
                            except:
                                pass
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

def SetKnownLetters(l_HorizontalAnswers, l_VerticalAnswers, lHorizLetters, lVertLetters):
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

def SolutionAsString(l_HorizLetters,l_VertLetters) -> str:
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

def GetMinimumSwaps(sLetters,l_HorizAnswers,l_VertAnswers,l_HorizLetters,l_VertLetters) -> list:
    iWordLen = len(l_HorizAnswers[0][0])
    iNumOfWords = len(l_HorizAnswers)
    sTarget = SolutionAsString(l_HorizLetters,l_VertLetters)
    lScratch = []
    for char in sLetters:
        lScratch.append(char)
    l_Steps = [] #will contain list of: [FromX, FromY, FromLetter, ToX, ToY, ToLetter]
    notDone = True
    while notDone:
        notDone = False
        for i in range(len(lScratch)):
            if lScratch[i] != sTarget[i] and sTarget[i] != ".":
                notDone = True
                wantedChar = sTarget[i]
                haveChar = lScratch[i]
                l_Indexes = []
                #get all possibilities
                for j in range(len(lScratch)):
                    if lScratch[j] == wantedChar and sTarget[j] != wantedChar: #this is an out of place character and it's a character we're looking for
                        l_Indexes.append(j)
                for k in range(len(l_Indexes)):
                    indexOfWanted = l_Indexes[k]
                    if sTarget[indexOfWanted] == haveChar: #obvious swap, they belong in each other's spot
                        fromCoords = LetterIndextoGeneralCoords(indexOfWanted,iWordLen,iNumOfWords)
                        toCoords = LetterIndextoGeneralCoords(i,iWordLen,iNumOfWords)
                        l_Steps.append([fromCoords[0],fromCoords[1],wantedChar,toCoords[0],toCoords[1],haveChar])
                        lScratch[i] = wantedChar
                        lScratch[indexOfWanted] = haveChar
                        break
                    elif sTarget[indexOfWanted] == ".":
                        #Swap is indeterminate, don't do it yet.
                        notDone = False #in case this was the last one holding it back.
                    elif len(l_Indexes) == 1: #or (k == len(l_Indexes)-1):
                        #kinda have to make this swap. it's the only possible option, or we've tried all the others.
                        fromCoords = LetterIndextoGeneralCoords(indexOfWanted,iWordLen,iNumOfWords)
                        toCoords = LetterIndextoGeneralCoords(i,iWordLen,iNumOfWords)
                        l_Steps.append([fromCoords[0],fromCoords[1],wantedChar,toCoords[0],toCoords[1],haveChar])
                        lScratch[i] = wantedChar
                        lScratch[indexOfWanted] = haveChar


    return l_Steps

def GetPossibleSwaps(lCurrentState, sTarget) -> list:
    for Loop in range(2):
        lReturnList = [] #[fromIndex,ToIndex,NewBoardState] for each index
        iOutOfPlace = 0
        for i in range(len(lCurrentState)):
                if lCurrentState[i] != sTarget[i] and sTarget[i] != ".":
                    iOutOfPlace += 1
                    wantedChar = sTarget[i]
                    haveChar = lCurrentState[i]
                    l_IndexesOfWantedChar = []
                    lTempList = [] #only holds current state swaps. Useful if we're only looking for perfects
                    PerfectOnly = False
                    #get all possibilities
                    for j in range(len(lCurrentState)):
                        if lCurrentState[j] == wantedChar and sTarget[j] != wantedChar: #this is an out of place character and it's a character we're looking for
                            l_IndexesOfWantedChar.append(j)
                    for k in range(len(l_IndexesOfWantedChar)):
                        indexOfWanted = l_IndexesOfWantedChar[k]
                        if sTarget[indexOfWanted] != ".":
                            if sTarget[indexOfWanted] == haveChar: #obvious swap, they belong in each other's spot
                                if PerfectOnly == False:
                                    lTempList = [] #clear out all the non-perfect swaps
                                    PerfectOnly = True
                                lNewBoardState = []
                                DeepExtend(lNewBoardState,lCurrentState)
                                lNewBoardState[indexOfWanted] = haveChar
                                lNewBoardState[i] = wantedChar
                                lTempList.append([i,indexOfWanted,lNewBoardState])
                            elif PerfectOnly == False:
                                if len(l_IndexesOfWantedChar) == 1 or Loop == 1:
                                    lNewBoardState = []
                                    DeepExtend(lNewBoardState,lCurrentState)
                                    lNewBoardState[indexOfWanted] = haveChar
                                    lNewBoardState[i] = wantedChar
                                    lTempList.append([i,indexOfWanted,lNewBoardState])
                    lReturnList.extend(lTempList)
        if len(lReturnList) > 0: #if it didn't find any perfect swaps, we'll loop again and find all swaps.
            return lReturnList
    return lReturnList

def BFS_SP(graph, start, goal):
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

def GetMinimumSwaps_graph(sLetters,l_HorizAnswers,l_VertAnswers,l_HorizLetters,l_VertLetters) -> list:
    #have a set representing the connections
    #have a set of arrays holding the swaps, the current total cost, and the array setup at the moment.
    #if the array setup isn't the answer, add more options to it
    #once all nodes have been processed to their options or are a complete state, find the one with the lowest cost.
    #Follow the graph backwards to find the list of swaps neccesary
    iWordLen = len(l_HorizAnswers[0][0])
    iNumOfWords = len(l_HorizAnswers)
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
    lStates = [lBoardState]
    lSwaps = []
    qToBeProcessed = deque([0])
    goalIndex = None
    while len(qToBeProcessed):
            iCurrentNode = qToBeProcessed.popleft()
            while qToBeProcessed.count(iCurrentNode): #in case it got added multiple times. Shouldn't be possible, but... eh.
                qToBeProcessed.remove(iCurrentNode)
            lPossibleMoves = GetPossibleSwaps(lStates[iCurrentNode],sTarget)
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
                state = move[2]
                if state in lStates:
                    stateIndex = lStates.index(state)
                else:
                    stateIndex = len(lStates)
                    lStates.append(state)
                if state == lTarget and goalIndex == None:
                    print("Goal Found!")
                    goalIndex = stateIndex
                
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
        fromIndex = min(lSwaps[setSwapIndexes[LastState][swapNum]])
        toIndex = max(lSwaps[setSwapIndexes[LastState][swapNum]])
        fromCoords = LetterIndextoGeneralCoords(fromIndex,iWordLen,iNumOfWords)
        toCoords = LetterIndextoGeneralCoords(toIndex,iWordLen,iNumOfWords)
        fromChar = lBoardState[fromIndex]
        toChar = lBoardState[toIndex]

        SolutionSwaps.append([fromCoords[0],fromCoords[1],fromChar,toCoords[0],toCoords[1],toChar])
        lBoardState[fromIndex] = toChar
        lBoardState[toIndex] = fromChar
        LastState = solution[i]
    return SolutionSwaps
                


    


     



    



#program
build_dictionary(wordLen,bannedChars)

#lists loaded. Fill the lists.
for i in range(NumberOfWords):
    DeepExtend(l_HorizontalAnswers[i],l_AllWords)
    DeepExtend(l_VerticalAnswers[i],l_AllWords)

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

#s_Waffle = "peetdruaattloepvlaara"
#s_Colors = "g.y.g...y.gy....gg.yg"
#s_Waffle = "peetdruapetaltoalarva"
#s_Colors = "g.y.g...ggggg.y.ggggg"

#deluxe waffle: wordlen = 7, numofwords = 4
#s_Waffle = "sivroybdoctmsbotgrnsersdaiiserouuieesesu"
#s_Colors = "yyg.g.y....gygyg.g...ygyg.gyg..yyy.gyg.."

while(AreWeDoneYet(l_HorizontalAnswers,l_VerticalAnswers) == False):
    print("\n")
    s_Waffle = input("Enter Your setup: ").lower()
    s_Colors = input("Enter the colors for them (G=Green, Y=Yellow, .=White): ").lower()

    try:
        SetLetters(s_Waffle,s_Colors,l_HorizontalKnownLetters,l_VerticalKnownLetters,l_FullyUnhomedLetters)
    except:
        print("Those lists need to be the same length")
        continue

    ReducePossibleWords(s_Waffle,s_Colors,l_HorizontalKnownLetters,l_VerticalKnownLetters,l_HorizontalAnswers,l_VerticalAnswers,l_FullyUnhomedLetters)
    ReduceByPlaying_Extensible(s_Waffle,l_HorizontalAnswers,l_VerticalAnswers,l_HorizontalKnownLetters,l_VerticalKnownLetters)
    #ReduceByPlaying(s_Waffle,l_HorizontalAnswers,l_VerticalAnswers,l_HorizontalKnownLetters,l_VerticalKnownLetters)

    print("Possible Horizontal words:")
    for i in range(len(l_HorizontalAnswers)):
        if len(l_HorizontalAnswers[i]) > 1:
            print("Row "+str(i+1)+": "+str(len(l_HorizontalAnswers[i]))+" words remaining.")
            if len(l_HorizontalAnswers[i]) < 15:
                print(str(l_HorizontalAnswers[i]))
        else:
            print("Row "+str(i+1)+" answer: "+str(l_HorizontalAnswers[i][0]))
    print("\n")
    print("Possible Vertical words:")
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

    l_Swaps = GetMinimumSwaps_graph(s_Waffle,l_HorizontalAnswers,l_VerticalAnswers,l_HorizontalKnownLetters,l_VerticalKnownLetters)
    #l_Swaps = GetMinimumSwaps(s_Waffle,l_HorizontalAnswers,l_VerticalAnswers,l_HorizontalKnownLetters,l_VerticalKnownLetters)
    if len(l_Swaps) > 10:
        print("WARNING: this is more than 10 swaps required!")
    else:
        print(str(len(l_Swaps))+" swaps proposed:")
    for i in range(len(l_Swaps)):
        print("Swap #"+str(i+1)+": \""+str(l_Swaps[i][2])+"\"("+str(l_Swaps[i][0])+","+str(l_Swaps[i][1])+") to \""+str(l_Swaps[i][5])+"\"("+str(l_Swaps[i][3])+","+str(l_Swaps[i][4])+")")

    for y in range(wordLen):
        for x in range(wordLen):
            lPossibleLetters = PossibleLettersAtLocation(x,y,s_Waffle,s_Colors,l_HorizontalKnownLetters,l_VerticalKnownLetters,l_HorizontalAnswers,l_VerticalAnswers,l_FullyUnhomedLetters)
            if len(lPossibleLetters)>1:
                print("Possible Letters at ("+str(x)+","+str(y)+") :"+str(lPossibleLetters))

print("Done!") #normally I'd print out the answer here, but that's already done.