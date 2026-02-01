import copy
import io
import string
import re
import statistics
import math
import random
from functools import lru_cache
from collections import defaultdict

#hardcoded variables
bannedChars = ["'","Å","â","ä","á","å","ç","é","è","ê","í","ñ","ó","ô","ö","ü","û","-"," "]
wordLen = 5


#global variables
l_ULAnswers = []
l_URAnswers = []
l_LLAnswers = []
l_LRAnswers = [] #U/L = Upper/Lower, L/R = Left/Right

l_ULUnknownPositions = []
l_URUnknownPositions = []
l_LLUnknownPositions = []
l_LRUnknownPositions = []

l_ULGreyCharacters = []
l_URGreyCharacters = []
l_LLGreyCharacters = []
l_LRGreyCharacters = []

PossibleAnswers = []
l_AllAnswers = []
l_AllKnownLetters = []

WholeWordList = [] #holds all the words we know.
b_SuperSearch = False
b_SuperSearchConfirmed = True

#functions block
def load_dict(file,StorageList):
    fileDict=io.open(file, mode="r", encoding="utf-8")
    dictionary = fileDict.readlines()
    dictsize = int(len(dictionary))
    StorageList += dictionary

def build_dictionary(wordLength,bannedCharacters):
    global PossibleAnswers

    #load wordle answer list (sorted, so it can't be directly used for cheating)
    load_dict("Wordlists/wordle_answerlist.txt",PossibleAnswers)

    #load wordle complete list (both accepted words and answers)
    load_dict("Wordlists/wordle_complete.txt",PossibleAnswers)

    #Unix dict
    load_dict("Wordlists/words.txt",PossibleAnswers)

    PossibleAnswers = optimize_wordlist(PossibleAnswers,wordLength,bannedCharacters)

    print("Answer list Loaded.")
    print("("+str(len(PossibleAnswers))+" words)")

def load_extra_wordlists(wordLength,bannedCharacters):
    """Basically a clone of build_ductionary() but stores and optimizes to WholeWordList instead"""
    global WholeWordList

    #if "hard mode" is active, I'm pretty sure they're looking to play wordle.
    load_dict("Wordlists/wordle_complete.txt",WholeWordList)
    WholeWordList = optimize_wordlist(WholeWordList,wordLength,bannedCharacters)

    print("Whole word list assembled.")
    print("("+str(len(WholeWordList))+" words)")
    print("First line: \""+str(WholeWordList[0])+"\"")
    print("final line: \""+str(WholeWordList[len(WholeWordList)-1])+"\"")

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

    if l_LetterStats is not None:
        totalChars=0
        #clear array
        for i in range(len(l_LetterStats)):
            l_LetterStats[i] = 0
        for word in l_WordList:
            for char in word:
                c = char.lower()
                if c in string.ascii_lowercase:
                    ind = ord(c) - 97
                    l_LetterStats[ind] += 1
                    totalChars += 1
                else:
                    if noisy:
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
    if l_WordStats is not None:
        charsSeen = []
        for i in range(len(l_WordStats)):
            l_WordStats[i] = 0
        for word in l_WordList:
            for char in word:
                c = char.lower()
                try:
                    if c not in charsSeen:
                        charsSeen.append(c)
                        if c in string.ascii_lowercase:
                            ind = ord(c) - 97
                            l_WordStats[ind] += 1
                        else:
                            if noisy:
                                print("Non-ascii character found: "+char)
                except Exception:
                    if noisy:
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

def IUI_a_FWL_Breakout(s_WordAttempt, l_Answers, l_UnknownPositions, l_GreyCharacters ) -> bool:

    s_WordOutcome = input("How did that go for you? (y=yellow, g=green, anything else = grey) ").lower()
    #yellows added to unknowPositions, Greens added to filter, greys added to banned chars
    #edge cases: guessed a double letter when only a single exists. make sure to not add it to banned. however, it also means the letter is not there.

    if len(s_WordOutcome) < len(s_WordAttempt):
        print("You're that lazy? Going to assume the rest are grey.")
        s_WordOutcome = s_WordOutcome.ljust(len(s_WordAttempt),".")
    elif len(s_WordOutcome) > len(s_WordAttempt):
        print("That response is too long. I'm going to assume that was erroneous.")
        return False
    
    s_FilterString = ""
    l_TempGreenLetters = []
    l_TempYellowLetters = []
    l_TempGreyLetters = []
    for i in range(len(s_WordAttempt)):
        if s_WordOutcome[i] == "g":
            #green letter: best outcome
            l_TempGreenLetters.append(s_WordAttempt[i])
            s_FilterString += s_WordAttempt[i]
        elif s_WordOutcome[i] == "y":
            #Yellow: not great, but it works
            l_TempYellowLetters.append(s_WordAttempt[i])
            s_FilterString += "[^"+s_WordAttempt[i]+"]"
        else:
            #grey. garbage. however, to help mitigate the edge cases, will filter from this position anyways.
            l_TempGreyLetters.append(s_WordAttempt[i])
            s_FilterString += "[^"+s_WordAttempt[i]+"]"
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
            l_GreyCharacters.append(l_TempGreyLetters[i])
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
    l_BackupAnswers = l_Answers
    if len(reduce_Wordlist(l_Answers, l_GreyCharacters, l_TempYellowLetters, s_FilterString)) < 1:
        print("Check that input again. There's no words left if that's the case.")
        l_Answers = l_BackupAnswers
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

    l_TempAnswers = reduce_Wordlist(l_Answers, l_GreyCharacters, l_UnknownPositions, s_FilterString)
    l_Answers.clear()
    l_Answers.extend(l_TempAnswers)
    return True

def InterrogateUserForInfo_and_FilterWordlist() -> None:
    global l_ULAnswers
    global l_URAnswers
    global l_LLAnswers
    global l_LRAnswers #U/L = Upper/Lower, L/R = Left/Right

    global l_ULUnknownPositions
    global l_URUnknownPositions
    global l_LLUnknownPositions
    global l_LRUnknownPositions

    global l_ULGreyCharacters
    global l_URGreyCharacters
    global l_LLGreyCharacters
    global l_LRGreyCharacters

    while True:
        s_WordAttempt = input("Enter the word you tried: ").lower()
        if (len(s_WordAttempt) != wordLen):
            print("That word isn't the length we're looking for. I'm going to assume that was erroneous.")
        else:
            break
    while True:
        if len(l_ULAnswers) > 1:
            print("Upper left:")
            if IUI_a_FWL_Breakout(s_WordAttempt,l_ULAnswers,l_ULUnknownPositions,l_ULGreyCharacters) == True:
                if len(l_ULAnswers) == 1:
                    print("**Upper Left is \""+str(l_ULAnswers[0])+"\"")
                break
        else:
            print("**Upper left is \""+str(l_ULAnswers[0])+"\"")
            break
    while True:
        if len(l_URAnswers) > 1:
            print("Upper right:")
            if IUI_a_FWL_Breakout(s_WordAttempt,l_URAnswers,l_URUnknownPositions,l_URGreyCharacters) == True:
                if len(l_URAnswers) == 1:
                    print("**Upper Right is \""+str(l_URAnswers[0])+"\"")
                break
        else:
            print("**Upper right is \""+str(l_URAnswers[0])+"\"")
            break
    while True:
        if len(l_LLAnswers) > 1:
            print("Lower left:")
            if IUI_a_FWL_Breakout(s_WordAttempt,l_LLAnswers,l_LLUnknownPositions,l_LLGreyCharacters) == True:
                if len(l_LLAnswers) == 1:
                    print("**Lower Left is \""+str(l_LLAnswers[0])+"\"")
                break
        else:
            print("**Lower left is \""+str(l_LLAnswers[0])+"\"")
            break
    while True:
        if len(l_LRAnswers) > 1:
            print("Lower right:")
            if IUI_a_FWL_Breakout(s_WordAttempt,l_LRAnswers,l_LRUnknownPositions,l_LRGreyCharacters) == True:
                if len(l_LRAnswers) == 1:
                    print("**Lower Right is \""+str(l_LRAnswers[0])+"\"")
                break
        else:
            print("**Lower right is \""+str(l_LRAnswers[0])+"\"")
            break


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
            genStats(l_WordList, None, l_LetterCounts)
        
        for i in range(26):
            l_CombinedList[i][0] = chr(i+97)
            l_CombinedList[i][1] = l_LetterCounts[i]
            #to access: [i][0] is the letter, [i][1] is the count
    else:
        l_CombinedList = l_2DLetterList
        

    #sort the list via the counts, in reverse order because I like the largest values on the left
    l_CombinedList = sorted(l_CombinedList, key=lambda x: x[1], reverse=True)

    if i_MinCount is not None:
        #make a list of values that are all greater than or equal to the minimum count
        for i in range(len(l_CombinedList)-1,-1,-1): #iterate backwards so the index doesn't change on me
            if l_CombinedList[i][1] < i_MinCount:
                del l_CombinedList[i]
            else:
                break #once we hit a non-zero value, we know there's no more zeros as the list is sorted.

    if i_MaxCount is not None:
        for i in range(len(l_CombinedList)):
            if l_CombinedList[0][1] >= i_MaxCount:
                del l_CombinedList[0]
            else:
                break #all the top words are gonna be at the front of the list. if one is below that length, we know there are no more.
            #technically, there could be more known letters after the check fails once, but realistically, if we're not filtering, we probably just want the top unknown result.

    if l_IgnoredLetters is not None:
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
            genStats(l_WordList, None, l_LetterCounts)
        
        for i in range(26):
            l_CombinedList[i][0] = chr(i+97)
            l_CombinedList[i][1] = l_LetterCounts[i]
            #to access: [i][0] is the letter, [i][1] is the count
    else:
        l_CombinedList = l_2DLetterList

    #sort the list via the counts, in reverse order because I like the largest values on the left
    l_CombinedList = sorted(l_CombinedList, key=lambda x: x[1], reverse=True)

    if i_MinCount is not None:
        #make a list of values that are all nonzero
        for i in range(len(l_CombinedList)-1,-1,-1): #iterate backwards so the index doesn't change on me
            if l_CombinedList[i][1] < i_MinCount:
                del l_CombinedList[i]
            else:
                break #once we hit a non-zero value, we know there's no more zeros as the list is sorted.
    if i_MaxCount is not None:
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

def suggestWord(wordList:list[str], numberOfLetters:int = 6, wholeWordList:list[str] = [], l_KnownLetters:list[str] =[], noisy = True) -> list:
    """Prints words from list wordList that contain the most number of letters returned by mostCommonLetters()\n\n
    wordList is a list of valid words to pick from\n
    numberOfLetters is how many letters to get from mostCommonLetters() to try to cram into the word\n
    hangmanRules will just print the most common letter in the wordlist, or the first letter in your wantedLetters list, if you sent one instead for some reason, as a string.\n
    hardMode will only return words that contain all the knowlege provided. False will pull from wholeWordList.
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
        if len(wordList)>8: #if there's only 2 words in the wordlist, it takes less guesses to just try them both. 3 is more or less the same.
            wordList.extend(wholeWordList)
        #dedupe the list
        wordList = list(dict.fromkeys(wordList))
        
        countMostCommonHit = [0]*len(wordList)

        for i in range(len(wordList)):
            #for every legal word, we're gonna count the amount of letters that hit
            lettersInWord = []
            for char in wordList[i]:
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
                    print(wordList[maxHitWords[i]])
                print("Might I suggest trying \""+wordList[maxHitWords[rnd]]+"\"?")
            
            listToReturn = []
            for i in range(len(maxHitWords)):
                listToReturn.append(wordList[maxHitWords[i]])
            return listToReturn
        elif len(maxHitWords) == 1:
            if noisy:
                print("Might I suggest trying \""+wordList[maxHitWords[0]]+"\"?")
            return [wordList[maxHitWords[0]]]
        else:
            rnd = random.randrange(0,len(wordList),1)
            if noisy:
                print("Something severely broke when trying to suggest a word.") #the list shouldn't ever be empty. Only thing I can think of is if all letters are known, so mcLetters is empty, so all counts are 0
                #so I'll use the ol standby:
                print("Try \""+wordList[rnd]+"\"?")
            return [wordList[rnd]]

def FindWordsWithOnlyLetters(wantedLetters, wordList) -> list:
    """Returns words from list wordList made completely of letters from list wantedLetters"""
    countLettersHit = [0]*len(wordList)
    for i in range(len(wordList)):
        countLettersHit[i] = len(set(wantedLetters) & set(wordList[i])) #turns out this unfairly weights words that have duplicate letters. I don't care!
    #find the remaining word with the most most-common letters and suggest that
    maxHitWords = [i for i, j in enumerate(countLettersHit) if j == len(wordList[i])] #this is a list of indexes in wordList where the count equals the length of the word

    l_Output = []
    for i in range(len(maxHitWords)):
        l_Output.append(wordList[maxHitWords[i]])
    return l_Output


def _score_play_worker(args):
    """Module-level worker used by multiprocessing.Pool. Expects (play, answers)."""
    play, answers = args
    outcomes = defaultdict(int)
    for answer in answers:
        out = GetWordleResponse(play, answer)
        outcomes[out] += 1
    if outcomes:
        counts = list(outcomes.values())
        return [play, sum(counts) / len(counts), max(counts)]
    else:
        return [play, 0, 0]

@lru_cache(maxsize=None)
def GetWordleResponse(s_Input, s_Answer) -> str:
    """Returns a list of ".","G", and "Y" for absent, Green, and Yellow, respectively, to simulate what wordle would respond with"""
    s_Correct = "G"
    s_Present = "Y"
    s_Absent = "."
    #find greens
    #find yellows from remaining letters, left to right. make sure letters aren't double-counted. Possibly destroy the letter in Answer when counted to make it easy?
    #probably just process left to right, but I wonder if I can pull the code from wordle itself to see how it actually does it
    #Code from wordle is as follows:
    """var r = function(s_Guess, Solution) {
        for (var a_Evaluation = Array(Solution.length).fill(s_LetterAbsent), a_IsNotCorrect = Array(Solution.length).fill(!0), a_IsNotFoundWrongPosition = Array(Solution.length).fill(!0), n = 0; n < s_Guess.length; n++) //fill eval aray with Absent, t/o with trues
            s_Guess[n] === Solution[n] && a_IsNotFoundWrongPosition[n] && (a_Evaluation[n] = s_LetterCorrect,
            a_IsNotCorrect[n] = !1,
            a_IsNotFoundWrongPosition[n] = !1); //if the letter is correct & a_IsNotFoundWrongPosition is true, set the eval as correct, set IsNotCorrect and a_IsNotFoundWrongPosition to false
        for (var r = 0; r < s_Guess.length; r++) {
            var LetterToLookFor = s_Guess[r];
            if (a_IsNotCorrect[r])
                for (var l = 0; l < Solution.length; l++) {
                    var LetterFromSolution = Solution[l];
                    if (a_IsNotFoundWrongPosition[l] && LetterToLookFor === LetterFromSolution) { //if that letter isn't already marked as present and matches
                        a_Evaluation[r] = s_LetterPresent,
                        a_IsNotFoundWrongPosition[l] = !1;
                        break
                    } //mark the eval of the guess as Present, and set a_IsNotFoundWrongPosition to false. Immediately break.
                }
        }
        return a_Evaluation
    }"""
    l_Evaluation = [s_Absent]*len(s_Answer)
    l_IsCorrect = [False]*len(s_Answer)
    l_IsSearchable = [True]*len(s_Answer)
    for i in range(len(s_Answer)):
        if (s_Input[i] == s_Answer[i]) and (l_IsSearchable[i]):
            l_Evaluation[i] = s_Correct
            l_IsCorrect[i] = True
            l_IsSearchable[i] = False
    #greens found and marked
    for i in range(len(s_Answer)):
        if not l_IsCorrect[i]:
            Letter = s_Input[i]
            for j in range(len(s_Answer)):
                SolutionLetter = s_Answer[j]
                if l_IsSearchable[j] and (Letter == SolutionLetter):
                    l_Evaluation[i] = s_Present
                    l_IsSearchable[j] = False
                    break
    #yellows found and marked
    #create string
    s_Output = ""
    for i in range(len(l_Evaluation)):
        s_Output += l_Evaluation[i]
    return s_Output

def GetGuessScores(l_WordList, l_WholeWordList = [], l_UselessCharacters = [], use_parallel: bool = True, heuristic_k: int = 100) -> list:
    """A rather expensive function. runs in ~ O(n*m) time, depending on the length of the lists put in.
    BUT: should give the best possible wordle play, or pretty close to it!
    l_WordList is a list of all the answers
    b_HardMode tells the function if hardmode is active
    l_WholeWordList lists all playable words, is only used if b_HardMode is True"""
    #Find all the words in WholeWordList that could help (have unknown letters and/or unknown positions in a position to test), or use WordList if hardmode is on
    #of that list, find the word that gives the best outcome on average, no matter the response
        #find all possible responses (grey, yellows, greens) given the wordlist
        #calculate a score for each one: given that result, how many words are left?
        #average all scores
        #lowest average score is returned (if more than 1, return list. but I don't know how common that'd be)
            #based on some early testing: surprisingly common, actually!
        #OR: do I want to score the most ambiguous outcome (Only keep highest score from the list)
        #I feel like unless it's SUPER close, or one actually decimates all the competition, average gives a better idea.
    l_PossiblePlays = []
    l_PossiblePlays.extend(l_WordList) #Have to do it like this or it modifies the answerlist for SOME REASON?! Point is: I want the answers to be first if they work
    if len(l_UselessCharacters) > 0:
        l_BannedWords = FindWordsWithOnlyLetters(l_UselessCharacters,l_WholeWordList)
        l_PossiblePlays.extend([word for word in l_WholeWordList if word not in l_BannedWords]) #add all words that aren't useless
    else:
        l_PossiblePlays.extend(l_WholeWordList)
    #however, if the answers are possible solutions, we want them on there first. Only relevant if they're providing perfect scores, but it happens enough.
    #dedupe the list if answer list is contained in the whole list (as it most certainly is):
    l_PossiblePlays = list(dict.fromkeys(l_PossiblePlays))
    # Two-stage heuristic: quick sampling estimator across all plays, then exact scoring
    # on a reduced pool. This gives much better matching to full scoring.
    if heuristic_k is not None and 0 < heuristic_k < len(l_PossiblePlays):
        # small sample size for quick estimation
        quick_sample_size = min(250, max(50, int(len(l_WordList) * 0.05)))
        try:
            quick_samples = random.sample(l_WordList, quick_sample_size) if quick_sample_size < len(l_WordList) else list(l_WordList)
        except Exception:
            quick_samples = list(l_WordList)

        quick_estimates = []
        for play in l_PossiblePlays:
            outcomes = defaultdict(int)
            for answer in quick_samples:
                out = GetWordleResponse(play, answer)
                outcomes[out] += 1
            if outcomes:
                counts = list(outcomes.values())
                avg = sum(counts) / len(counts)
                # prefer answer words slightly
                if play in l_WordList:
                    avg *= 0.995
                quick_estimates.append((play, avg))
            else:
                quick_estimates.append((play, float('inf')))

        quick_estimates.sort(key=lambda x: x[1])
        pool_k = min(len(l_PossiblePlays), max(heuristic_k * 3, 1500))
        l_PossiblePlays = [w for w, _ in quick_estimates[:pool_k]]

    l_ScoreList = []

    # Use multiprocessing for large runs if requested
    if use_parallel and len(l_PossiblePlays) > 50:
        import multiprocessing as mp
        cpu_count = mp.cpu_count()
        with mp.Pool(processes=cpu_count) as pool:
            args = ((play, l_WordList) for play in l_PossiblePlays)
            for res in pool.imap_unordered(_score_play_worker, args, chunksize=16):
                l_ScoreList.append(res)
    else:
        for play in l_PossiblePlays:
            outcomes = defaultdict(int)
            for answer in l_WordList:
                out = GetWordleResponse(play, answer)
                outcomes[out] += 1
            if outcomes:
                counts = list(outcomes.values())
                l_ScoreList.append([play, sum(counts) / len(counts), max(counts)])
            else:
                l_ScoreList.append([play, 0, 0])
    
    #now that I have the scores, I want to trim the useless values
    i_WorstAcceptableAverage = len(l_WordList) - 0.5 #must on average remove at least 1 word, 50% of the time
    i_WorstAcceptableMax = len(l_WordList) - 1 #come on, man. You gotta always remove ONE word from the pool.

    l_ScoreList = sorted(l_ScoreList, key=lambda x: x[2], reverse=False) #sort by max, reverse false because we want the worst scores at the end

    #delete all values greater than the acceptable score
    for i in range(len(l_ScoreList)-1,-1,-1): #iterate backwards so the index doesn't change on me
        if l_ScoreList[i][2] > i_WorstAcceptableMax:
            del l_ScoreList[i]
        else:
            break #once we hit a less-than value, we know there's no more as the list is sorted.

    l_ScoreList = sorted(l_ScoreList, key=lambda x: x[1], reverse=False) #sort by average score

    #delete all values greater than the acceptable score
    for i in range(len(l_ScoreList)-1,-1,-1): #iterate backwards so the index doesn't change on me
        if l_ScoreList[i][1] > i_WorstAcceptableAverage:
            del l_ScoreList[i]
        else:
            break #once we hit a less-than value, we know there's no more as the list is sorted.
    
    return l_ScoreList

def FindOptimalQuordlePlay() -> list:
    global l_ULAnswers
    global l_URAnswers
    global l_LLAnswers
    global l_LRAnswers #U/L = Upper/Lower, L/R = Left/Right

    global l_ULGreyCharacters
    global l_URGreyCharacters
    global l_LLGreyCharacters
    global l_LRGreyCharacters

    global WholeWordList

    #Make a list of letters none of the words benefit from
    #l_FullBanCharacters = set(l_ULGreyCharacters) & set(l_URGreyCharacters) & set(l_LLGreyCharacters) & set(l_LRGreyCharacters)
    #nvm, this wouldn't do much. Gonna remove them on a word-by-word basis


    #step 1: get all the scores for all the guesses
    l_CombinedScores = []
    i_ExpectedDupes = 4

    l_ULScores = None
    if len(l_ULAnswers)>1:
        l_ULScores = GetGuessScores(l_ULAnswers, WholeWordList, l_ULGreyCharacters)
        DeepExtend(l_CombinedScores, l_ULScores)
    else:
        i_ExpectedDupes -= 1
    l_URScores = None
    if len(l_URAnswers)>1:
        l_URScores = GetGuessScores(l_URAnswers, WholeWordList, l_URGreyCharacters)
        DeepExtend(l_CombinedScores, l_URScores)
    else:
        i_ExpectedDupes -= 1
    l_LLScores = None
    if len(l_LLAnswers)>1:
        l_LLScores = GetGuessScores(l_LLAnswers, WholeWordList, l_LLGreyCharacters)
        DeepExtend(l_CombinedScores, l_LLScores)
    else:
        i_ExpectedDupes -= 1
    l_LRScores = None
    if len(l_LRAnswers)>1:
        l_LRScores = GetGuessScores(l_LRAnswers, WholeWordList, l_LRGreyCharacters)
        DeepExtend(l_CombinedScores, l_LRScores)
    else:
        i_ExpectedDupes -= 1

    #step 2: calculate average score for each, noting if there's a perfect solution available.
    
    i_Length = len(l_CombinedScores)
    i_PunishmentValue = AverageValNot1(len(l_ULAnswers),len(l_URAnswers),len(l_LLAnswers),len(l_LRAnswers))
    i=0
    while(i<i_Length): #for i in range(i_Length): #this would cause issues when getting to the very end and continuing because the range was already decided.
        i_SUM_avrg = WeightValue(l_CombinedScores[i][1])
        i_SUM_Max = l_CombinedScores[i][2]
        for k in range(1,i_ExpectedDupes):
            try:
                index = CombinedScoresFindDupeIndex(l_CombinedScores,i)
                i_SUM_avrg += WeightValue(l_CombinedScores[index][1])
                i_SUM_Max += l_CombinedScores[index][2]
                del l_CombinedScores[index] #destroy it. it's worthless now.
                i_Length -= 1 #compensate the length so we don't run off the edge
                
            except:
                i_SUM_avrg += i_PunishmentValue
                i_SUM_Max += i_PunishmentValue
        av_average = i_SUM_avrg #/i_ExpectedDupes
        av_Max = i_SUM_Max #/i_ExpectedDupes #I'm thinking I don't want the average, as each list is a different scale, so total words left should be the strat
        l_CombinedScores[i][1] = av_average
        l_CombinedScores[i][2] = av_Max
        i+=1
    #values averaged
    l_CombinedScores = sorted(l_CombinedScores, key=lambda x: x[1], reverse=False) #sort by average score

    print("SuperSearch Top results:")
    i_MaxResultsToPrint = 15
    if len(l_CombinedScores) < i_MaxResultsToPrint:
        i_MaxResultsToPrint = len(l_CombinedScores)
    f_TopScore = l_CombinedScores[0][1]
    for i in range(i_MaxResultsToPrint):
        if l_CombinedScores[i][1] <= (f_TopScore + 1):
            OutputOptimalPlayString(l_CombinedScores[i],l_ULScores,l_URScores,l_LLScores,l_LRScores)
        else:
            return


    return l_CombinedScores[0:15]

def CombinedScoresFindDupeIndex(l_CombinedScores:list, i_Index) -> int:
    s_Word = l_CombinedScores[i_Index][0]
    for i in range(i_Index+1, len(l_CombinedScores)):
        if l_CombinedScores[i][0] == s_Word:
            return i
    raise LookupError(str(s_Word)+" Not found.")

def CombinedScoresFindIndex(l_CombinedScores:list, s_Word) -> int:
    for i in range(len(l_CombinedScores)):
        if l_CombinedScores[i][0] == s_Word:
            return i
    raise LookupError(str(s_Word)+" Not found.")

def OutputOptimalPlayString(l_Input:list,l_ULScores = None,l_URScores = None,l_LLScores = None,l_LRScores = None) -> None:
    i_MaxWordWidth = 18
    i_ListsInPlay = 0
    if l_ULScores is not None:
        i_ListsInPlay += 1
        #i_MaxWordWidth = 17
    if l_URScores is not None:
        #i_MaxWordWidth = max(i_MaxWordWidth, 18)
        i_ListsInPlay += 1
    if l_LLScores is not None:
        #i_MaxWordWidth = max(i_MaxWordWidth, 17)
        i_ListsInPlay += 1
    if l_LRScores is not None:
        #i_MaxWordWidth = max(i_MaxWordWidth, 18)
        i_ListsInPlay += 1

    if l_Input[1] <= (WeightValue(1)*i_ListsInPlay):
        print("\""+l_Input[0]+"\" gives perfect information.")
        return #no reason to continue if it's 100% perfect
    elif l_Input[1] <= 0:
        print("\""+l_Input[0]+"\" gives near perfect information with a score of "+"{:.3f}".format(l_Input[1])+", but up to "+str(l_Input[2])+" words left.")
    else:
        print("\""+l_Input[0]+"\" gives a score of "+"{:.3f}".format(l_Input[1])+", but up to "+str(l_Input[2])+" words left.")
    
    if l_ULScores is not None:
        try:
            index = CombinedScoresFindIndex(l_ULScores,l_Input[0])
            if l_ULScores[index][1] == 1.0:
                print("   **It gives Perfect information for the Upper-Left!")
            else:
                print("     Upper-Left: ".ljust(i_MaxWordWidth," ")+"{:.1f}".format(l_ULScores[index][1])+" words left on average, with a max of "+str(l_ULScores[index][2]))
        except:
            pass
    if l_URScores is not None:
        try:
            index = CombinedScoresFindIndex(l_URScores, l_Input[0])
            if l_URScores[index][1] == 1.0:
                print("   **It gives Perfect information for the Upper-Right!")
            else:
                print("     Upper-Right: ".ljust(i_MaxWordWidth," ")+"{:.1f}".format(l_URScores[index][1])+" words left on average, with a max of "+str(l_URScores[index][2]))
        except:
            pass
    if l_LLScores is not None:
        try:
            index = CombinedScoresFindIndex(l_LLScores, l_Input[0])
            if l_LLScores[index][1] == 1.0:
                print("   **It gives Perfect information for the Lower-Left!")
            else:
                print("     Lower-Left: ".ljust(i_MaxWordWidth," ")+"{:.1f}".format(l_LLScores[index][1])+" words left on average, with a max of "+str(l_LLScores[index][2]))
        except:
            pass
    if l_LRScores is not None:
        try:
            index = CombinedScoresFindIndex(l_LRScores, l_Input[0])
            if l_LRScores[index][1] == 1.0:
                print("   **It gives Perfect information for the Lower-Right!")
            else:
                print("     Lower-Right: ".ljust(i_MaxWordWidth," ")+"{:.1f}".format(l_LRScores[index][1])+" words left on average, with a max of "+str(l_LRScores[index][2]))
        except:
            pass
    
def DeepExtend(l_OrigList:list, l_Extension:list) -> list:
    #for i in range(len(l_Extension)):
    tempCopy = copy.deepcopy(l_Extension)
    l_OrigList.extend(tempCopy)
    return l_OrigList

def AverageValNot1(Item1:int, Item2:int = 1, Item3:int = 1, Item4:int = 1):
    i_Sum = 0
    i_Divisor = 0
    if Item1 != 1:
        i_Sum += Item1
        i_Divisor += 1
    if Item2 != 1:
        i_Sum += Item2
        i_Divisor += 1
    if Item3 != 1:
        i_Sum += Item3
        i_Divisor += 1
    if Item4 != 1:
        i_Sum += Item4
        i_Divisor += 1
    return i_Sum/i_Divisor

def WeightValue(Value):
    if Value == 1:
        return -2 #perfect knowlege answers are heavily weighted
    elif Value < 2:
        return Value - 0.5 #close to perfect knowlege is good
    else:
        return Value

def PrintWordsRemaining(s_Name:str, l_wordlist:list[str]) -> None:
    i_Strwidth = 13
    i_length = len(l_wordlist)
    if i_length == 1:
        print("**"+s_Name+" is \""+str(l_wordlist[0])+"\"")
    elif i_length < 10:
        print(str(s_Name+": ").ljust(i_Strwidth," ")+str(i_length)+" words remaining:")
        print(str(l_wordlist))
    else:
        print(str(s_Name+": ").ljust(i_Strwidth," ")+str(i_length)+" words remaining.")

        







    



#program
if __name__ == "__main__":
    print("NOTE: for every yes/no question, blank responses are \"no\", and any response is considered \"yes\"")
    b_SuperSearch = bool(input("Enable SuperSearch (Very slow, but the best possible outcome)? "))
    b_AllWords = bool(input("Load whole wordlist (Makes SS take 6.5x longer, but may yield SLIGHTLY better results)?"))
    if not b_SuperSearch:
        b_SuperSearchConfirmed = False
    build_dictionary(wordLen,bannedChars)

    WholeWordList += PossibleAnswers
    if b_AllWords:
        load_extra_wordlists(wordLen,bannedChars)

    #lists loaded. Fill the lists.
    l_ULAnswers.extend(PossibleAnswers)
    l_URAnswers.extend(PossibleAnswers)
    l_LLAnswers.extend(PossibleAnswers)
    l_LRAnswers.extend(PossibleAnswers)

    b_FirstRun = True
    while (len(l_ULAnswers) > 1) or (len(l_URAnswers) > 1) or (len(l_LLAnswers) > 1) or (len(l_LRAnswers) > 1):
        print("\n\n")
        PrintWordsRemaining("Upper Left", l_ULAnswers)
        PrintWordsRemaining("Upper Right", l_URAnswers)
        PrintWordsRemaining("Lower Left", l_LLAnswers)
        PrintWordsRemaining("Lower Right", l_LRAnswers)
        if (len(l_ULAnswers)<=15) and (len(l_URAnswers)<=15) and (len(l_LLAnswers)<=15) and (len(l_LRAnswers)<=15):
            if not b_SuperSearchConfirmed:
                b_SuperSearch = bool(input("Do you want to enable SuperSearch now? "))
                b_SuperSearchConfirmed = True

        l_AllAnswers = []
        if len(l_ULAnswers) > 1:
            l_AllAnswers.extend(l_ULAnswers)
        if len(l_URAnswers) > 1:
            l_AllAnswers.extend(l_URAnswers)
        if len(l_LLAnswers) > 1:
            l_AllAnswers.extend(l_LLAnswers)
        if len(l_LRAnswers) > 1:
            l_AllAnswers.extend(l_LRAnswers) #put all the answers in one list
        l_AllKnownLetters = []
        l_AllKnownLetters.extend(l_ULUnknownPositions)
        l_AllKnownLetters.extend(l_URUnknownPositions)
        l_AllKnownLetters.extend(l_LLUnknownPositions)
        l_AllKnownLetters.extend(l_LRUnknownPositions)

        suggestWord(l_AllAnswers, wordLen+1, WholeWordList, l_AllKnownLetters, True)

        if b_SuperSearch & (not b_FirstRun):
            OptimalWord = FindOptimalQuordlePlay()
            #print("SuperSearch Suggestion: "+str(OptimalWord))
        InterrogateUserForInfo_and_FilterWordlist()
        b_FirstRun = False
    try:
        print("\n\n")
        PrintWordsRemaining("Upper Left", l_ULAnswers)
        PrintWordsRemaining("Upper Right", l_URAnswers)
        PrintWordsRemaining("Lower Left", l_LLAnswers)
        PrintWordsRemaining("Lower Right", l_LRAnswers)
        print("Done!")
    except IndexError:
        print("Something went wrong. I can't find the solutions.")