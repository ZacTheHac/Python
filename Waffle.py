import copy
import io
import string
import re
import statistics
import math
import random
from xmlrpc.client import boolean

#hardcoded variables
bannedChars = ["'","Å","â","ä","á","å","ç","é","è","ê","í","ñ","ó","ô","ö","ü","û","-"," "]
wordLen = 5
NumberOfWords = 3


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
    load_dict("Wordlists/YAWL_5_letter_only.txt",l_AllWords)

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

def genStats(l_WordList, l_WordStats = None, l_LetterStats = None, noisy = False) -> None:
    """Pulls words from l_WordList and outputs how common certain letters are in l_LetterStats (Including duplicate letters), and l_WordStats (one instance counted per word)
    Setting either output list as None skips that calculation.
    noisy will output extra info to the console."""
    #note: to replace lists, you have to modify them directly. assigning them breaks the initial link, so you don't modify the original

    if l_LetterStats != None:
        totalChars=0
        #clear array
        for i in range(len(l_LetterStats)):
            l_LetterStats[i] = 0
        for word in l_WordList:
            for char in word:
                try:
                    ind = string.ascii_letters.index(char)
                    l_LetterStats[ind] += 1
                    totalChars += 1
                except ValueError:
                    print("Non-ascii character found: "+char)
        if noisy:
            maxCount = max(l_LetterStats)
            #find all instances of that count
            maxLetters = [i for i, j in enumerate(l_LetterStats) if j == maxCount]
            #normalize the indexes into characters
            for i in range(len(maxLetters)):
                maxLetters[i] = chr(maxLetters[i]+97)
            if len(maxLetters) > 1:
                letters = ""
                for letter in maxLetters:
                    letters += letter
                    letters += ", "
                print("Most common letters are: "+letters+"with "+str(maxCount)+" occurrences each.")
            else:
                print("Most common letter is: "+str(maxLetters[0])+" with "+str(maxCount)+" occurrences.")

            minCount = min(l_LetterStats)
            minLetters = [i for i, j in enumerate(l_LetterStats) if j == minCount]
            for i in range(len(minLetters)):
                minLetters[i] = chr(minLetters[i]+97)
            if len(minLetters) > 1:
                letters = ""
                for letter in minLetters:
                    letters += letter
                    letters += ", "
                print("The least common letters are: "+letters+"with only "+str(minCount)+" occurances each.")
            else:
                print("The least common letter is: "+str(minLetters[0])+" with only "+str(minCount)+" occurances.")


            print("Total characters counted: "+str(totalChars))

    #more useful counts: only count one instance per word
    if l_WordStats != None:
        charsSeen = []
        for i in range(len(l_WordStats)):
            l_WordStats[i] = 0
        for word in l_WordList:
            for char in word:
                try:
                    if char not in charsSeen:
                        charsSeen.append(char)
                        ind = string.ascii_letters.index(char)
                        l_WordStats[ind] += 1
                except ValueError:
                    print("Non-ascii character found: "+char)
            charsSeen = []
        if noisy:
            maxCount = max(l_WordStats)
            #find all instances of that count
            maxLetters = [i for i, j in enumerate(l_WordStats) if j == maxCount]
            #normalize the indexes into characters
            for i in range(len(maxLetters)):
                maxLetters[i] = chr(maxLetters[i]+97)

            if len(maxLetters) > 1:
                letters = ""
                for letter in maxLetters:
                    letters += letter
                    letters += ", "
                print("Most common letters are: "+letters+" in "+str(maxCount)+" words each.")
            else:
                print("Most common letter is: "+str(maxLetters[0])+" in "+str(maxCount)+" words.")

            minCount = min(l_WordStats)
            minLetters = [i for i, j in enumerate(l_WordStats) if j == minCount]
            for i in range(len(minLetters)):
                minLetters[i] = chr(minLetters[i]+97)
            if len(minLetters) > 1:
                letters = ""
                for letter in minLetters:
                    letters += letter
                    letters += ", "
                print("The least common letters are: "+letters+"in only "+str(minCount)+" words each.")
            else:
                print("The least common letter is: "+str(minLetters[0])+" in only "+str(minCount)+" words.")

def IUI_a_FWL_Breakout(s_WordAttempt:str, l_Answers:list, l_UnknownPositions:list, l_GreyCharacters:list, s_Result:str, s_Yellows:str ) -> bool:

    if len(s_Result) < len(s_WordAttempt):
        print("You're that lazy? Going to assume the rest are grey.")
        s_Result = s_Result.ljust(len(s_WordAttempt),".")
    elif len(s_Result) > len(s_WordAttempt):
        print("That response is too long. I'm going to assume that was erroneous.")
        return False
    l_InputYellows = []
    for char in s_Yellows:
        l_InputYellows.append(char)
    
    s_FilterString = ""
    l_TempGreenLetters = []
    l_TempYellowLetters = []
    l_TempGreyLetters = []
    l_TempGreyLettersFiltered = []
    for i in range(len(s_Result)):
        if s_Result[i].isalpha():
            #green letter: best outcome
            l_TempGreenLetters.append(s_Result[i])
            s_FilterString += s_Result[i]
        else:
            #could be actual grey, could just be a yellow.
            if s_WordAttempt[i] in l_InputYellows:
                l_TempYellowLetters.append(s_WordAttempt[i])
                del l_InputYellows[l_InputYellows.index(s_WordAttempt[i])] #remove it so it's not double-counted later.
                s_FilterString += "[^"+s_WordAttempt[i]+"]"
            else:
                l_TempGreyLetters.append(s_WordAttempt[i])
                s_FilterString += "[^"+s_WordAttempt[i]+"]"
    l_TempYellowLetters.extend(l_InputYellows)
    #check for double letters while filling out bannedChars
    l_FoundAll = []
    for i in range(len(l_TempGreyLetters)):
        if l_TempGreyLetters[i] in l_TempYellowLetters: #we have to check for yellow first or it'll fullban the letter despite not knowing the position. (see: eerie y.g.g for scree)
            print("Looks like there's no more \""+l_TempGreyLetters[i]+"\"s in the word.")
            #We don't know where it goes, so fullban isn't possible, and we already added it to filter string. so just remove the entry
            l_TempGreyLetters[i] = ""
        elif l_TempGreyLetters[i] in l_TempGreenLetters:
            print("Looks like there's no more \""+l_TempGreyLetters[i]+"\"s in the word.")
            l_FoundAll.append(l_TempGreyLetters[i])
            l_TempGreyLetters[i] = ""
        else:
            l_TempGreyLettersFiltered.append(l_TempGreyLetters[i])
    for i in range(len(l_TempGreenLetters)):
        if l_TempGreenLetters[i] not in l_TempYellowLetters: #squareword tells us if there's more by putting it in yellow still.
            print("Looks like there's no more \""+l_TempGreenLetters[i]+"\"s in the word.")
            l_FoundAll.append(l_TempGreenLetters[i])
    #for those we know that we have all positions, filter all other positions with that letter
    if(len(l_FoundAll) != 0):
        s_foundAll = ""
        for char in l_FoundAll:
            s_foundAll += char
        i_strLen = len(s_FilterString)
        i=0
        while i < i_strLen:
            indexOf = s_FilterString.find("[^",i)
            if indexOf != -1:
                indexOf += 2 #to make sure it goes after the filter character
                s_FilterString = str_Insert(s_FilterString,indexOf,s_foundAll)
                #refresh the values
                i_strLen = len(s_FilterString)
                i = indexOf + len(l_FoundAll)
            else:
                #no more in the word
                i=i_strLen
    #additional filters done

    #check if the input is possible
    if len(reduce_Wordlist(l_Answers, l_TempGreyLettersFiltered, l_TempYellowLetters, s_FilterString)) < 1:
        print("Check that input again. There's no words left if that's the case.")
        return False

    #make sure the green letters are in unknownPositions so they can pad double letters
    for char in l_TempGreenLetters:
        if char not in l_UnknownPositions:
            l_UnknownPositions.append(char)
        else:
            i_neededCount = (l_TempYellowLetters.count(char) + l_TempGreenLetters.count(char)) - l_UnknownPositions.count(char)
            #if unknownPositions.count(char) < (l_YellowLetters.count(char) + l_GreenLetters.count(char)):
            for i in range(i_neededCount):
                l_UnknownPositions.append(char)
    #Finally, put the yellow letters into unknownPositions, being careful to only double up on confirmed double letters
    for char in l_TempYellowLetters:
        if char not in l_UnknownPositions:
            l_UnknownPositions.append(char)
        else:
            i_neededCount = max(((l_TempYellowLetters.count(char) + l_TempGreenLetters.count(char)) - l_UnknownPositions.count(char)),0)
            #if unknownPositions.count(char) < (l_YellowLetters.count(char) + l_GreenLetters.count(char)):
            for i in range(i_neededCount):
                l_UnknownPositions.append(char)
    
    l_GreyCharacters.extend(l_TempGreyLettersFiltered)

    l_TempAnswers = reduce_Wordlist(l_Answers, l_GreyCharacters, l_UnknownPositions, s_FilterString)
    l_Answers.clear()
    l_Answers.extend(l_TempAnswers)
    return True

def InterrogateUserForInfo_and_FilterWordlist() -> None:
    global l_HorizontalAnswers
    global l_VerticalAnswers
    global l_KnownLetters
    global l_KnownBadLetters
    global wordLen

    while True:
        s_WordAttempt = input("Enter the word you tried: ").lower()
        if (len(s_WordAttempt) != wordLen):
            print("That word isn't the length we're looking for. I'm going to assume that was erroneous.")
        else:
            break
    for i in range(len(l_HorizontalAnswers)):
        if len(l_HorizontalAnswers[i]) > 1:
            while True:
                print("Row "+str(i+1)+":")
                s_Result = input("What does the row look like now? [. for grey]: ").lower()
                s_Yellows = input("What yellows do you have now? ").lower()
                if IUI_a_FWL_Breakout(s_WordAttempt,l_HorizontalAnswers[i],l_KnownLetters[i],l_KnownBadLetters[i],s_Result,s_Yellows) == True:
                    if len(l_HorizontalAnswers[i]) == 1:
                        print("Row "+str(i+1)+" is \""+str(l_HorizontalAnswers[i][0])+"\"")
                    break
        else:
            print("Row "+str(i+1)+" is \""+str(l_HorizontalAnswers[i][0])+"\"")

def str_Insert(s_Original, i_index, s_Insert) -> str:
    """Returns a string with s_Insert placed at i_index"""
    return s_Original[:i_index]+s_Insert+s_Original[i_index:]

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

def mostCommonLetters(i_MaxLetters:int, i_MinCount:int, i_MaxCount:int, l_WordList:list[str] = None, l_LetterCounts:list[int] = None, l_2DLetterList:list = None, l_IgnoredLetters:list[str] = None, noisy:bool = True) -> list:
    """Returns the most common letters in the wordlist. \n
    i_MaxLetters = maximum number of letters to return (will return fewer if fewer exist)\n
    i_MinCount = The Lowest number of hits that this function will return, inclusive. \n
    i_MaxCount = the highest number of hits the letter can have to be returned, exclusive. Useful for ignoring letters that are in every word.\n
        l_WordList = the wordlist to operate on. Can provide this or: \n
        l_LetterCounts = a list of how common letters are, with the index of the list referring to their ASCII offset from 97 (a) or finally:\n
        l_2DLetterList = an array of 2 arrays that contains the character in [i][0], and its count in [i][1] \n
            Set values to None if they're unused\n"""

    l_CombinedList = [[0 for x in range(2)] for y in range(26)]

    if l_2DLetterList is None:
        #have to make the list myself
        if l_LetterCounts is None:
            #calculate with genstats and build
            l_LetterCounts = [0] * 26
            genStats(l_WordList,l_LetterCounts)
        
        for i in range(26):
            l_CombinedList[i][0] = chr(i+97)
            l_CombinedList[i][1] = l_LetterCounts[i]
            #to access: [i][0] is the letter, [i][1] is the count
    else:
        l_CombinedList = l_2DLetterList
        

    #sort the list via the counts, in reverse order because I like the largest values on the left
    l_CombinedList = sorted(l_CombinedList, key=lambda x: x[1], reverse=True)

    if i_MinCount != None:
        #make a list of values that are all greater than or equal to the minimum count
        for i in range(len(l_CombinedList)-1,-1,-1): #iterate backwards so the index doesn't change on me
            if l_CombinedList[i][1] < i_MinCount:
                del l_CombinedList[i]
            else:
                break #once we hit a non-zero value, we know there's no more zeros as the list is sorted.

    if i_MaxCount != None:
        for i in range(len(l_CombinedList)):
            if l_CombinedList[0][1] >= i_MaxCount:
                del l_CombinedList[0]
            else:
                break #all the top words are gonna be at the front of the list. if one is below that length, we know there are no more.
            #technically, there could be more known letters after the check fails once, but realistically, if we're not filtering, we probably just want the top unknown result.

    if l_IgnoredLetters != None:
        for i in range(len(l_CombinedList)-1,-1,-1): #iterate backwards so the index doesn't change on me
            if l_CombinedList[i][0] in l_IgnoredLetters:
                del l_CombinedList[i]

    #at this point, all zero counts and max counts (assuming filterMaxCounts is set) are removed. The list is also sorted.
    #just need to trim it to final size
    if len(l_CombinedList)>i_MaxLetters:
        l_CombinedList = l_CombinedList[0:i_MaxLetters]

    if noisy & (len(l_CombinedList)>0):
        print(str(len(l_CombinedList))+" most common letters:")
        printLetters(None,None,None,None,l_CombinedList)

    sortedTopLetters = []
    for i in range(len(l_CombinedList)):
        sortedTopLetters.append(l_CombinedList[i][0])
    return sortedTopLetters

def printLetters(l_WordList:list[str], i_MinCount:int = 1, i_MaxCount:int = None, l_LetterCounts:list[int] = None, l_2DLetterList:list = None) -> None:
    """
    i_MinCount = The Lowest number of hits that this function will return, inclusive. \n
    i_MaxCount = the highest number of hits the letter can have to be returned, exclusive. Useful for ignoring letters that are in every word.\n
    Provide one of the following:\n
        l_WordList = the wordlist to operate on. Can provide this \n
        l_LetterCounts = a list of how common letters are, with the index of the list referring to their ASCII offset from 97(a)\n
        l_2DLetterList = an array of 2 arrays that contains the character in [i][0], and its count in [i][1] \n
    Set values to None if they're unused\n"""

    l_CombinedList = [[0 for x in range(2)] for y in range(26)]

    if l_2DLetterList is None:
        #have to make the list myself
        if l_LetterCounts is None:
            #calculate with genstats and build
            l_LetterCounts = [0] * 26
            genStats(l_WordList,l_LetterCounts)
        
        for i in range(26):
            l_CombinedList[i][0] = chr(i+97)
            l_CombinedList[i][1] = l_LetterCounts[i]
            #to access: [i][0] is the letter, [i][1] is the count
    else:
        l_CombinedList = l_2DLetterList

    #sort the list via the counts, in reverse order because I like the largest values on the left
    l_CombinedList = sorted(l_CombinedList, key=lambda x: x[1], reverse=True)

    if i_MinCount != None:
        #make a list of values that are all nonzero
        for i in range(len(l_CombinedList)-1,-1,-1): #iterate backwards so the index doesn't change on me
            if l_CombinedList[i][1] < i_MinCount:
                del l_CombinedList[i]
            else:
                break #once we hit a non-zero value, we know there's no more zeros as the list is sorted.
    if i_MaxCount != None:
        for i in range(len(l_CombinedList)):
            if l_CombinedList[0][1] >= i_MaxCount:
                del l_CombinedList[0]
            else:
                break #all the top words are gonna be at the front of the list. if one is below that length, we know there are no more.
    #at this point, all zero counts and max counts (assuming filterMaxCounts is set) are removed. The list is also sorted.

    if len(l_CombinedList)>0:
        i_width = len(str(l_CombinedList[0][1])) #the longest number is this many chars wide
        str_Letters = "| "
        str_Counts = "| "
        for i in range(len(l_CombinedList)):
            str_Counts += str(l_CombinedList[i][1]).center(i_width," ")+" | "
            str_Letters += str(l_CombinedList[i][0]).center(i_width," ")+" | "
        print(str_Letters)
        print(str_Counts)

def suggestWord(wordList:list[str], numberOfLetters:int = 6, l_KnownLetters:list[str] =[], WholeWordList:list = [], noisy = True) -> list:
    """Prints words from list wordList that contain the most number of letters returned by mostCommonLetters()\n\n
    wordList is a list of valid words to pick from\n
    numberOfLetters is how many letters to get from mostCommonLetters() to try to cram into the word\n
    wantedLetters lets you specify the letters you wish to use instead of pulling from mostCommonLetters(), send a blank list if unwanted\n
    noisy being True will print out the wording to the console. Either way the suggested word will be returned\n
    returnList will return a list if successful at finding words and there was more than one response

    return: a list of suggested word(s) or suggested character to try next. if there was an error finding an appropriate suggestion, it will spit out a random word from wordlist.
    """
    mcLetters = mostCommonLetters(numberOfLetters, 1, len(wordList), wordList, None, None, l_KnownLetters, noisy)
        
    if noisy:
        printLetters(wordList, 1, len(wordList))
        #midLetters = medianLetters(numberOfLetters, 1, None, wordList, None, None, l_KnownLetters, noisy)
        #lcLetters = leastCommonLetters(numberOfLetters, 1, None, wordList, None, None, l_KnownLetters, noisy)            

    if len(mcLetters) < 1:
        rnd = random.randrange(0,len(wordList),1)
        if noisy:
            print("I've got no guidance. Try \""+wordList[rnd]+"\"?")
        return [str(wordList[rnd])]
    else:
        l_searchableWords = []
        DeepExtend(l_searchableWords,wordList)
        if len(wordList) < 5:
            l_searchableWords.extend(WholeWordList)
        #dedupe the list
        l_searchableWords = list(dict.fromkeys(l_searchableWords))
        
        countMostCommonHit = [0]*len(l_searchableWords)

        for i in range(len(l_searchableWords)):
            #for every legal word, we're gonna count the amount of letters that hit
            lettersInWord = []
            for char in l_searchableWords[i]:
                if char not in lettersInWord:
                    lettersInWord.append(char)
            countMostCommonHit[i] = len(set(mcLetters) & set(lettersInWord)) #this takes a little longer, but should stop reccomendations of vastly different value being suggested.
        #find the remaining word with the most most-common letters and suggest that
        maxMCHit = max(countMostCommonHit)
        maxHitWords = [i for i, j in enumerate(countMostCommonHit) if j == maxMCHit] #this is a list of indexes in wordList where the max hit words reside
        if len(maxHitWords) > 1:
            startIndex = 0
            if noisy and len(maxHitWords) > 20:
                startIndex = 20
            rnd = random.randrange(startIndex,len(maxHitWords),1)
            if noisy:
                print("A few suggestions:")
                for i in range(min(len(maxHitWords),20)):
                    print(l_searchableWords[maxHitWords[i]])
                print("Might I suggest trying \""+l_searchableWords[maxHitWords[rnd]]+"\"?")
            
            listToReturn = []
            for i in range(len(maxHitWords)):
                listToReturn.append(l_searchableWords[maxHitWords[i]])
            return listToReturn
        elif len(maxHitWords) == 1:
            if noisy:
                print("Might I suggest trying \""+l_searchableWords[maxHitWords[0]]+"\"?")
            return [l_searchableWords[maxHitWords[0]]]
        else:
            rnd = random.randrange(0,len(l_searchableWords),1)
            if noisy:
                print("Something severely broke when trying to suggest a word.") #the list shouldn't ever be empty. Only thing I can think of is if all letters are known, so mcLetters is empty, so all counts are 0
                #so I'll use the ol standby:
                print("Try \""+l_searchableWords[rnd]+"\"?")
            return [l_searchableWords[rnd]]

def DeepExtend(l_OrigList:list, l_Extension:list) -> list:
    #for i in range(len(l_Extension)):
    tempCopy = copy.deepcopy(l_Extension)
    l_OrigList.extend(tempCopy)
    return l_OrigList

def PossibleLettersAt(i_Column:int, i_Row:int, l_HorizontalAnswers, l_VerticalAnswers) -> list:
    l_HorizontalWords = l_HorizontalAnswers[i_Row]
    l_VerticalWords = l_VerticalAnswers[i_Column]

    l_HorizontalWordLetters = []
    l_VerticalWordLetters = []
    for i in range(len(l_HorizontalWords)):
        char = l_HorizontalWords[i][i_Column]
        if char not in l_HorizontalWordLetters:
            l_HorizontalWordLetters.append(char)
    for i in range(len(l_VerticalWords)):
        char = l_VerticalWords[i][i_Row]
        if char not in l_VerticalWordLetters:
            l_VerticalWordLetters.append(char)
    l_Crossover = list(set(l_HorizontalWordLetters) & set(l_VerticalWordLetters))
    return l_Crossover

def UncertaintyCube(l_HorizontalAnswers:list, l_VerticalAnswers:list) -> None:
    i_MaxNum = 0
    l_UncertCube = [[0 for x in range(len(l_VerticalAnswers))] for y in range(len(l_HorizontalAnswers))]
    for R in range(len(l_HorizontalAnswers)):
        for C in range(len(l_VerticalAnswers)):
            l_UncertCube[C][R] = PossibleLettersAt(C,R,l_HorizontalAnswers,l_VerticalAnswers)
            if len(l_UncertCube[C][R]) > i_MaxNum:
                i_MaxNum = len(l_UncertCube[C][R])
        
    i_width = len(str(i_MaxNum)) #the longest number is this many chars wide
    for R in range(len(l_HorizontalAnswers)):
        str_Counts = "| "
        for C in range(len(l_VerticalAnswers)):
            i_Count = len(l_UncertCube[C][R])
            if i_Count == 1:
                str_Counts += str(l_UncertCube[C][R][0]).center(i_width," ")+" | "
            else:
                str_Counts += str(i_Count).center(i_width," ")+" | "
        print(str_Counts)

def ReducePossibleWords(l_HorizontalAnswers:list, l_VerticalAnswers:list):
    #print("Searching for possible words...")
    DirtyBit = True
    while DirtyBit:
        DirtyBit = False
        for C in range(len(l_VerticalAnswers)):
            s_vertRegex = ""
            for R in range(len(l_HorizontalAnswers)):
                l_Letters = PossibleLettersAt(C,R,l_HorizontalAnswers,l_VerticalAnswers)
                s_LetterRegex = "["
                for char in l_Letters:
                    s_LetterRegex += char
                s_LetterRegex += "]"
                s_regexBase = "."*(len(l_HorizontalAnswers)-1)
                s_horrizRegex = str_Insert(s_regexBase, C, s_LetterRegex)
                s_vertRegex += s_LetterRegex
                newHorrizontalWordlist = reduce_Wordlist(l_HorizontalAnswers[R], [], [], s_horrizRegex)
                if not newHorrizontalWordlist == l_HorizontalAnswers[R]:
                    DirtyBit = True
                    l_HorizontalAnswers[R].clear()
                    DeepExtend(l_HorizontalAnswers[R],newHorrizontalWordlist)
            newVerticalWordlist = reduce_Wordlist(l_VerticalAnswers[C], [], [], s_vertRegex)
            if not newVerticalWordlist == l_VerticalAnswers[C]:
                    DirtyBit = True
                    l_VerticalAnswers[C].clear()
                    DeepExtend(l_VerticalAnswers[C],newVerticalWordlist)
        #if DirtyBit:
        #    print("Comflicts Found. Resolving...")
        #else:
        #    print("No further conflicts found.")

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

def LetterIndextoCoords(Index:int,iWordLen:int,iNumOfWords:int) -> list:
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
    lUnhomed.clear()
    if not len(sLetters) == len(sColors):
        raise ValueError("Letters and Colors must be the same length.")
    iWordLen = len(lHorizLetters[0])
    iNumOfWords = len(lHorizLetters)
    for i in range(len(sColors)):
        if sColors[i] == "g":
            l_LetterIndexes = LetterIndextoCoords(i,iWordLen,iNumOfWords)
            if l_LetterIndexes[0][0] != None:
                lHorizLetters[l_LetterIndexes[0][0]][l_LetterIndexes[0][1]] = sLetters[i]
            if l_LetterIndexes[1][0] != None:
                lVertLetters[l_LetterIndexes[1][0]][l_LetterIndexes[1][1]] = sLetters[i]
        elif sColors[i] == "y":
            pass
        else:
            lUnhomed.append(sLetters[i])

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
                if not i == X:
                    if sLetters[iLetterIndex] in lNotAllowed:
                        #Probably in here by mistake, remove it from notallowed
                        del lNotAllowed[lNotAllowed.index(sLetters[iLetterIndex])]
            elif not sColors[iLetterIndex] == "g": #if it's not yellow or green it's a white
                if not sLetters[iLetterIndex] in lAllowedLetters:
                    lNotAllowed.append(sLetters[iLetterIndex])
    #check vertical
    if l_WordLocations[1][0] != None:
        for i in range(iWordLen):
            iLetterIndex = CoordsToStringIndex(X,i,iWordLen,iNumOfWords)
            if sColors[iLetterIndex] == "y":
                lAllowedLetters.append(sLetters[iLetterIndex])
                if not i == Y:
                    if sLetters[iLetterIndex] in lNotAllowed:
                        #Probably in here by mistake, remove it from notallowed
                        del lNotAllowed[lNotAllowed.index(sLetters[iLetterIndex])]
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
                if x % 2 == 1: #odd x: 1,3: If it's yellow, it HAS to be in this word
                    if sColors[CoordsToStringIndex(xCoord,y,iWordLen,iNumOfWords)] == "y":
                        lRequiredLetters.append(sLetters[CoordsToStringIndex(xCoord,y,iWordLen,iNumOfWords)])
            newWordlist = reduce_Wordlist(l_VerticalAnswers[AnswerListIndex], [], lRequiredLetters, sRegex)
            if not newWordlist == l_VerticalAnswers[AnswerListIndex]:
                    DirtyBit = True
                    l_VerticalAnswers[AnswerListIndex].clear()
                    DeepExtend(l_VerticalAnswers[AnswerListIndex],newWordlist)
    #done reducing: do some cleanup:
    #write out all known letters:
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
                    lHorizLetters[lAffectedWords[0][0]][lAffectedWords[0][1]] = l_VerticalAnswers[WordListIndex][0][x]
                if lAffectedWords[1][0] != None:
                    lVertLetters[lAffectedWords[1][0]][lAffectedWords[1][1]] = l_VerticalAnswers[WordListIndex][0][x]


     



    



#program
build_dictionary(wordLen,bannedChars)

#lists loaded. Fill the lists.
for i in range(NumberOfWords):
    DeepExtend(l_HorizontalAnswers[i],l_AllWords)
    DeepExtend(l_VerticalAnswers[i],l_AllWords)

#s_StartingWaffle = input("Enter Your Starting letters: ").lower()
#s_StartingColors = input("Enter the colors for them (G=Green, Y=Yellow, .=White): ").lower()
s_StartingWaffle = "eeatslrtehuugloarntay"
s_StartingColors = "g.yyg...y.g.y...g.gyg"
try:
    SetLetters(s_StartingWaffle,s_StartingColors,l_HorizontalKnownLetters,l_VerticalKnownLetters,l_FullyUnhomedLetters)
except:
    print("Those lists need to be the same length")
    quit()

ReducePossibleWords(s_StartingWaffle,s_StartingColors,l_HorizontalKnownLetters,l_VerticalKnownLetters,l_HorizontalAnswers,l_VerticalAnswers,l_FullyUnhomedLetters)

DisplayWaffle(l_HorizontalKnownLetters,l_VerticalKnownLetters)

for y in range(wordLen):
    for x in range(wordLen):
        lPossibleLetters = PossibleLettersAtLocation(x,y,s_StartingWaffle,s_StartingColors,l_HorizontalKnownLetters,l_VerticalKnownLetters,l_HorizontalAnswers,l_VerticalAnswers,l_FullyUnhomedLetters)
        if not lPossibleLetters == []:
            print("Possible Letters at ("+str(x)+","+str(y)+") :"+str(lPossibleLetters))

while(AreWeDoneYet(l_HorizontalAnswers,l_VerticalAnswers) == False):
    print("\n")
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
            print("Row "+str(i+1)+": "+str(len(l_VerticalAnswers[i]))+" words remaining.")
            if len(l_VerticalAnswers[i]) < 15:
                print(str(l_VerticalAnswers[i]))
        else:
            print("Row "+str(i+1)+" answer: "+str(l_HorizontalAnswers[i][0]))

    l_AllHorrizAnswers = []
    for i in range(len(l_HorizontalAnswers)):
        if len(l_HorizontalAnswers[i]) > 1:
            l_AllHorrizAnswers.extend(l_HorizontalAnswers[i])
     #put all the answers in one list

    l_AllKnownLetters = []
    for i in range(len(l_KnownLetters)):
        if len(l_KnownLetters[i]) > 1:
            l_AllKnownLetters.extend(l_KnownLetters[i])
    for i in range(len(l_KnownBadLetters)):
        if len(l_KnownBadLetters[i]) > 1:
            l_AllKnownLetters.extend(l_KnownBadLetters[i])

    suggestWord(l_AllHorrizAnswers, wordLen+1, l_AllKnownLetters, l_AllWords, True)
    InterrogateUserForInfo_and_FilterWordlist()
    ReducePossibleWords(l_HorizontalAnswers,l_VerticalAnswers)

    print("\n")
    print("Possible Letters at all locations:")
    UncertaintyCube(l_HorizontalAnswers,l_VerticalAnswers)

    b_FirstRun = False

print("Done!") #normally I'd print out the answer here, but that's already done.