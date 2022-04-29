import io
import string
import re
import statistics
import math
import random

#hardcoded variables
bannedChars = ["'","Å","â","ä","á","å","ç","é","è","ê","í","ñ","ó","ô","ö","ü","û","-"," "]
wordLen = 5
b_AnyWordLength = False


#global variables
legalWords = []
letterStats = [0] * 26
wordsContainingLetters = [0] * 26
unknownPositions = []
knownPositions = ""
b_HardMode = True
WholeWordList = [] #holds all the words we know. If hardmode isn't active, we can get more info trying words from this list
b_SuperSearch = False
b_SuperSearchConfirmed = True

#functions block
def load_dict(file,StorageList):
    fileDict=io.open(file, mode="r", encoding="utf-8")
    dictionary = fileDict.readlines()
    dictsize = int(len(dictionary))
    #print(file + " dictionary Loaded.")
    #print("("+str(dictsize)+" words)")
    #print("First line: \""+str(dictionary[0]).strip()+"\"")
    #print("final line: \""+str(dictionary[dictsize-1])+"\"")
    #add it to the list
    StorageList += dictionary

def build_dictionary(wordLength,bannedCharacters):
    global legalWords

    #load unix words
    #load_dict("Wordlists/words.txt",legalWords)

    #load scrabble dict
    #load_dict("Wordlists/Scrabble-Words-2019.txt",legalWords)

    #Open the OH LAWD webster dict
    #load_dict("Wordlists/webster-dictionary.txt",legalWords)

    #load gwicks dictionary
    #load_dict("Wordlists/english3.txt",legalWords)

    #load infochimps/dwyl dictionary
    #load_dict("Wordlists/words_alpha.txt",legalWords)

    #Load YAWL by Mendel Leo Cooper
    #load_dict("Wordlists/YAWL.txt",legalWords)

    #load combined file that eliminated 7,506,911 duplicates (~7MB), 571,985 words (Now expanded with YAWL to 578,747)
    #load_dict("Wordlists/MEGADICT.txt",legalWords)

    #load wordle answer list (sorted, so it can't be directly used for cheating)
    load_dict("Wordlists/wordle_answerlist.txt",legalWords)

    #load wordle complete list (both accepted words and answers)
    #load_dict("Wordlists/wordle_complete.txt",legalWords)

    #load reduced wordle answer list (contains only the words after wordle 260 (CLOTH))
    #load_dict("Wordlists/wordle_reduced_answerlist.txt",legalWords)

    #print("Optimizing wordlist...")
    legalWords = optimize_wordlist(legalWords,wordLength,bannedCharacters)
    #list optomized

    print("Legal word list assembled.")
    print("("+str(len(legalWords))+" words)")
    print("First line: \""+str(legalWords[0])+"\"")
    print("final line: \""+str(legalWords[len(legalWords)-1])+"\"")

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
    The new list is deduplicated and sorted alphabetically.\n
    wordLength is ignored if the global \"b_AnyWordLength\" is set."""
    global b_AnyWordLength

    newWords = []
    for word in wordList:
        word = word.strip().lower()
        if(len(word)==wordLength or b_AnyWordLength):
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
    if l_WordStats is not None:
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

def InterrogateUserForInfo_and_FilterWordlist(hangmanRules,WordleMode) -> None:
    global bannedChars
    global unknownPositions
    global knownPositions
    global legalWords

    if WordleMode:
        s_WordAttempt = input("Enter the word you tried: ").lower()
        s_WordOutcome = input("How did that go for you? (y=yellow, g=green, anything else = grey) ").lower()
        #yellows added to unknowPositions, Greens added to filter, greys added to banned chars
        #edge cases: guessed a double letter when only a single exists. make sure to not add it to banned. however, it also means the letter is not there.
        if (len(s_WordAttempt) != wordLen) and not b_AnyWordLength:
            print("That word isn't the length we're looking for. I'm going to assume that was erroneous.")
            return
        elif len(s_WordOutcome) < len(s_WordAttempt):
            print("You're that lazy? Going to assume the rest are grey.")
            s_WordOutcome = s_WordOutcome.ljust(len(s_WordAttempt),".")
        elif len(s_WordOutcome) > len(s_WordAttempt):
            print("That response is too long. I'm going to assume that was erroneous.")
            return
        s_FilterString = ""
        l_GreenLetters = []
        l_YellowLetters = []
        l_GreyLetters = []
        for i in range(len(s_WordAttempt)):
            if s_WordOutcome[i] == "g":
                #green letter: best outcome
                l_GreenLetters.append(s_WordAttempt[i])
                s_FilterString += s_WordAttempt[i]
            elif s_WordOutcome[i] == "y":
                #Yellow: not great, but it works
                l_YellowLetters.append(s_WordAttempt[i])
                s_FilterString += "[^"+s_WordAttempt[i]+"]"
            else:
                #grey. garbage. however, to help mitigate the edge cases, will filter from this position anyways.
                l_GreyLetters.append(s_WordAttempt[i])
                s_FilterString += "[^"+s_WordAttempt[i]+"]"
        #check for double letters while filling out bannedChars
        l_FoundAll = []
        for i in range(len(l_GreyLetters)):
            if l_GreyLetters[i] in l_YellowLetters: #we have to check for yellow first or it'll fullban the letter despite not knowing the position. (see: eerie y.g.g for scree)
                print("Looks like there's no more \""+l_GreyLetters[i]+"\"s in the word.")
                #We don't know where it goes, so fullban isn't possible, and we already added it to filter string. so just remove the entry
                l_GreyLetters[i] = ""
            elif l_GreyLetters[i] in l_GreenLetters:
                print("Looks like there's no more \""+l_GreyLetters[i]+"\"s in the word.")
                l_FoundAll.append(l_GreyLetters[i])
                l_GreyLetters[i] = ""
            else:
                bannedChars.append(l_GreyLetters[i])
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

        #make sure the green letters are in unknownPositions so they can pad double letters
        for char in l_GreenLetters:
            if char not in unknownPositions:
                unknownPositions.append(char)
            else:
                i_neededCount = (l_YellowLetters.count(char) + l_GreenLetters.count(char)) - unknownPositions.count(char)
                #if unknownPositions.count(char) < (l_YellowLetters.count(char) + l_GreenLetters.count(char)):
                for i in range(i_neededCount):
                    unknownPositions.append(char)

        #Finally, put the yellow letters into unknownPositions, being careful to only double up on confirmed double letters
        for char in l_YellowLetters:
            if char not in unknownPositions:
                unknownPositions.append(char)
            else:
                i_neededCount = max(((l_YellowLetters.count(char) + l_GreenLetters.count(char)) - unknownPositions.count(char)),0)
                #if unknownPositions.count(char) < (l_YellowLetters.count(char) + l_GreenLetters.count(char)):
                for i in range(i_neededCount):
                    unknownPositions.append(char)
        knownPositions = s_FilterString
    else:
        purgatory = True
        while purgatory:
            bannedLetters = ""
            knownPositions = "" #need these assignments or a blank input will keep old values
            neededLetters = "" #need this assignment or the sanity check later will crash if playing by hangman rules

            bannedLetters = input("Enter a list of known non-ocurring letters: ")
            if not hangmanRules:
                print("Known necessary letters: "+str(unknownPositions))
                neededLetters = input("Enter necessary letters: ") #unknown positions aren't a thing in hangman

            knownPositions = input("Enter known letter positions with \".\" for an unknown place:") #secretly it's just a regex
            if hangmanRules:
                #read and convert the regex if it's a simple one
                specialRegexChars = ["\\","^","[","]","$","|","?","*","+","{","}",":","<",">","!","(",")"]
                if not any(specialChar in specialRegexChars for specialChar in knownPositions):
                    #find all the letters and filter them with [^chars] + add them to unknown positions, just in case
                    knownCharacters = ""
                    for char in knownPositions:
                        if (char != ".") & (char not in knownCharacters):
                            knownCharacters += char
                    if knownCharacters != "": #if the string was empty/all unknown, don't bother with anything
                        filterBlock = "[^"+knownCharacters.lower()+"]"
                        knownPositions = knownPositions.replace(".",filterBlock)
                        for char in knownCharacters:
                            if char not in unknownPositions: #have to filter this or it causes a crash by making the known characters longer than the word!
                                unknownPositions.append(char)

            if bool(set(bannedLetters).isdisjoint(set(neededLetters))):
                if bool(set(bannedLetters).isdisjoint(set(unknownPositions))):
                    purgatory = False
                else:
                    print("Check that input again, it looks impossible.")
            else:
                print("Check that input again, it looks impossible.")

        for char in bannedLetters:
            bannedChars.append(char)
        for char in neededLetters:
            if char in unknownPositions:
                if bool(input("Did you mean there are multiple \""+char+"\"s? ")):
                    unknownPositions.append(char)
            else:
                unknownPositions.append(char)


    legalWords = reduce_Wordlist(legalWords, bannedChars, unknownPositions, knownPositions)

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

def mostCommonLetters(i_MaxLetters:int, i_MinCount:int, i_MaxCount:int, l_WordList:list[str] = None, l_LetterCounts:list[int] = None, l_2DLetterList:list = None, noisy:bool = True) -> list:
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
    #at this point, all zero counts and max counts (assuming filterMaxCounts is set) are removed. The list is also sorted.
    #just need to trim it to final size
    if len(l_CombinedList)>i_MaxLetters:
        l_CombinedList = l_CombinedList[0:i_MaxLetters]

    if noisy & (len(l_CombinedList)>0):
        print("Top "+str(len(l_CombinedList))+" unknown letters:")
        i_width = len(str(l_CombinedList[0][1])) #the longest number is this many chars wide
        str_Letters = "| "
        str_Counts = "| "
        for i in range(len(l_CombinedList)):
            str_Counts += str(l_CombinedList[i][1]).center(i_width," ")+" | "
            str_Letters += str(l_CombinedList[i][0]).center(i_width," ")+" | "
        print(str_Letters)
        print(str_Counts)

    sortedTopLetters = []
    for i in range(len(l_CombinedList)):
        sortedTopLetters.append(l_CombinedList[i][0])
    return sortedTopLetters

def medianLetters(maxLetters, noisy = True) -> list:
    """Returns a list of the letter that occurs the high median in the global \"legalWords\" based on values found in the global \"wordsContainingLetters\"\n
    All 0 counts are removed from consideration, so the median returned may be higher than the whole list would suggest.\n
    if maxLetters>1, the further items will be the letters surrounding the median letter\n
    if maxLetters is even, the true median will be right after the halfway point, and the found letters will fill the first half\n
    if maxLetters is odd, the high median will be in the center of the returned list.\n
    noisy determines if the function prints out its findings to the console. True is to print, and is the default
    """

    global wordsContainingLetters
    global legalWords
    
    l_CombinedList = [[0 for x in range(2)] for y in range(26)]
    for i in range(26):
        l_CombinedList[i][0] = chr(i+97)
        l_CombinedList[i][1] = wordsContainingLetters[i]
        #to access: [i][0] is the letter, [i][1] is the count

    #sort the list via the counts, in reverse order because I like the largest values on the left
    l_CombinedList = sorted(l_CombinedList, key=lambda x: x[1], reverse=True)

    #make a list of values that are all nonzero
    for i in range(len(l_CombinedList)-1,-1,-1): #iterate backwards so the index doesn't change on me
        if l_CombinedList[i][1] == 0:
            del l_CombinedList[i]
        else:
            break #once we hit a non-zero value, we know there's no more zeros as the list is sorted.

    #l_MedianLetters = [[0 for x in range(2)] for y in range(maxLetters)]
    i_CutAmount = len(l_CombinedList) - maxLetters
    if i_CutAmount > 0:
        if i_CutAmount % 2 == 0: #even cuts
            i_cut = math.floor(i_CutAmount/2)
            for i in range(i_cut):
                del l_CombinedList[0]
            for i in range(i_cut):
                del l_CombinedList[len(l_CombinedList)-1]
            #ends chopped off
        else: #odd cuts, take the majority from the bottom
            i_cut = math.floor(i_CutAmount/2)
            for i in range(i_cut+1):
                del l_CombinedList[0]
            for i in range(i_cut):
                del l_CombinedList[len(l_CombinedList)-1]
            #for i in range(len(l_CombinedList)-1,len(l_CombinedList)-i_cut-1,-1):#technically also works, but is really ugly to look at
            #    del l_CombinedList[i]


    #filter out nonsense values if they exist
    filteredMedianLetters = []
    for i in range(len(l_CombinedList)):
        if((l_CombinedList[i][1] < len(legalWords))):
            filteredMedianLetters.append(l_CombinedList[i][0])

    if noisy & (len(l_CombinedList)>0):
        print("middle "+str(len(l_CombinedList))+" letters:")
        i_width = len(str(l_CombinedList[0][1])) #the longest number is this many chars wide
        str_Letters = "| "
        str_Counts = "| "
        for i in range(len(l_CombinedList)):
            str_Counts += str(l_CombinedList[i][1]).center(i_width," ")+" | "
            str_Letters += str(l_CombinedList[i][0]).center(i_width," ")+" | "
        print(str_Letters)
        print(str_Counts)

    return filteredMedianLetters

def leastCommonLetters(i_MaxLetters:int, i_MinCount:int, i_MaxCount:int, l_WordList:list[str] = None, l_LetterCounts:list[int] = None, l_2DLetterList:list = None, noisy:bool = True) -> list:
    """Returns the least common letters in the wordlist. \n
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
    #at this point, all zero counts and max counts (assuming filterMaxCounts is set) are removed. The list is also sorted.
    #just need to trim it to final size
    if len(l_CombinedList)>i_MaxLetters:
        l_CombinedList = l_CombinedList[len(l_CombinedList)-i_MaxLetters:]

    if noisy & (len(l_CombinedList)>0):
        print("Rarest "+str(len(l_CombinedList))+" occuring letters:")
        i_width = len(str(l_CombinedList[0][1])) #the longest number is this many chars wide
        str_Letters = "| "
        str_Counts = "| "
        for i in range(len(l_CombinedList)):
            str_Counts += str(l_CombinedList[i][1]).center(i_width," ")+" | "
            str_Letters += str(l_CombinedList[i][0]).center(i_width," ")+" | "
        print(str_Letters)
        print(str_Counts)

    sortedLowestLetters = []
    for i in range(len(l_CombinedList)):
        sortedLowestLetters.append(l_CombinedList[i][0])
    return sortedLowestLetters

#TODO: Use input letter list
def printAllLetters(filterMaxCounts = False) -> None:
    global wordsContainingLetters
    global legalWords

    l_CombinedList = [[0 for x in range(2)] for y in range(26)]
    for i in range(26):
        l_CombinedList[i][0] = chr(i+97)
        l_CombinedList[i][1] = wordsContainingLetters[i]
        #to access: [i][0] is the letter, [i][1] is the count

    #sort the list via the counts, in reverse order because I like the largest values on the left
    l_CombinedList = sorted(l_CombinedList, key=lambda x: x[1], reverse=True)

    #make a list of values that are all nonzero
    for i in range(len(l_CombinedList)-1,-1,-1): #iterate backwards so the index doesn't change on me
        if l_CombinedList[i][1] == 0:
            del l_CombinedList[i]
        else:
            break #once we hit a non-zero value, we know there's no more zeros as the list is sorted.
    if filterMaxCounts:
        for i in range(len(l_CombinedList)):
            if l_CombinedList[0][1] >= len(legalWords):
                del l_CombinedList[0]
            else:
                break #all the top words are gonna be at the front of the list. if one is below that length, we know there are no more.
    #at this point, all zero counts and max counts (assuming filterMaxCounts is set) are removed. The list is also sorted.

    if len(l_CombinedList)>0:
        print("Letter frequency in remaining words:")
        i_width = len(str(l_CombinedList[0][1])) #the longest number is this many chars wide
        str_Letters = "| "
        str_Counts = "| "
        for i in range(len(l_CombinedList)):
            str_Counts += str(l_CombinedList[i][1]).center(i_width," ")+" | "
            str_Letters += str(l_CombinedList[i][0]).center(i_width," ")+" | "
        print(str_Letters)
        print(str_Counts)

def suggestWord(wordList, numberOfLetters, hangmanRules=False, hardMode = True, wholeWordList = [], wantedLetters = [], noisy = True, returnList = False) -> list:
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
    if wantedLetters == []:
        if hangmanRules:
            #we want max counts
            mcLetters = mostCommonLetters(numberOfLetters, 1, None, wordList, None, None, noisy)
        else:
            #we don't care about max counts
            mcLetters = mostCommonLetters(numberOfLetters, 1, len(wordList), wordList, None, None, noisy)
        
        if noisy:
            printAllLetters(not hangmanRules)
            #midLetters = medianLetters(numberOfLetters, noisy)
            #lcLetters = leastCommonLetters(numberOfLetters, noisy)
    else:
        mcLetters = wantedLetters #this just makes it easier for the code to work

    if(hangmanRules):
        if noisy:
            print("I would suggest trying \""+str(mcLetters[0])+"\".")
        return [str(mcLetters[0])]

    if (not hardMode) and (len(wordList)>3): #if there's only 2 words in the wordlist, it takes less guesses to just try them both. 3 is more or less the same.
        wordList = wholeWordList
    #TODO: if mostCommonLetters gets refactored to use an input wordlist, I have to be sure to give it the legalWords, but still search inside wholeWordList

    if len(mcLetters) < 1:
        rnd = random.randrange(0,len(wordList),1)
        if noisy:
            print("I've got no guidance. Try \""+wordList[rnd]+"\"?")
        return [str(wordList[rnd])]
    else:
        countMostCommonHit = [0]*len(wordList)
        #mcUnknownLetters = mostCommonLetters(numberOfTopLetters, True, False) #no clue why I generated these again when I did at the beginning and stored it under mcLetters. The arguments would be the same if it got here, so...
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
            if returnList:
                listToReturn = []
                for i in range(len(maxHitWords)):
                    listToReturn.append(wordList[maxHitWords[i]])
                return listToReturn
            else:
                return wordList[maxHitWords[rnd]]
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

def FindOptimalPlay(l_WordList, b_HardMode = True, l_WholeWordList = [], b_Noisy = True) -> list:
    """A rather expensive function. runs in ~ O(n*m) time, depending on the length of the lists put in.
    BUT: should give the best possible wordle play, or pretty close to it!
    l_WordList is a list of all the answers
    b_HardMode tells the function if hardmode is active
    l_WholeWordList lists all playable words, is only used if b_HardMode is True"""
    i_MaxOutput = 50 #this is the most words this function will return
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
    if not b_HardMode:
        if b_Noisy:
            l_PossiblePlays.extend(l_WholeWordList)
            #if we're looking at whole debug stuff, we probably want the best no matter what.
        else:
            l_PossiblePlays.extend(reduce_Wordlist(l_WholeWordList, [], mostCommonLetters(1, 1, len(l_WordList), l_WordList, None, None, False), str("")))
            #often this would cause lockups that lasted almost a minute. By trimming down the list we search by requiring it have the most popular letter, we can still get great results in 1/4 the time.
            #however, if the answers are possible solutions, we want them on there first. Only relevant if they're providing perfect scores, but it happens enough.
    #dedupe the list if answer list is contained in the whole list (as it most certainly is):
    l_PossiblePlays = list(dict.fromkeys(l_PossiblePlays))



    l_AverageScore = [0] * len(l_PossiblePlays)
    l_MaxScore = [0] * len(l_PossiblePlays) #if the average ties with something else, we'll use this to slim the list a bit more.
    PerfectScoreCount = 0 #in some scenarios, there's dozens of words that give a perfect score. It's not worth it to provide more than ~5?
    for i in range(len(l_PossiblePlays)):
        l_PossibleOutcomes = [[0 for x in range(len(l_PossiblePlays))] for y in range(2)]
        i_PossOutIndex = 0
        index = 0
        for j in range(len(l_WordList)):
            l_outcome = GetWordleResponse(l_PossiblePlays[i],l_WordList[j])
            try:
                index = l_PossibleOutcomes[0].index(l_outcome)
            except:
                index = i_PossOutIndex
                i_PossOutIndex+= 1
            l_PossibleOutcomes[0][index] = l_outcome
            l_PossibleOutcomes[1][index] += 1
        #outcomes for this word calculated
        #calculate average score:
        i_sum = 0
        i_divisor = 0
        for k in range(len(l_PossibleOutcomes[0])):
            if l_PossibleOutcomes[1][k] > 0:
                i_sum += l_PossibleOutcomes[1][k]
                i_divisor += 1
            else:
                break
        if i_divisor > 0:
            l_AverageScore[i] = i_sum / i_divisor #thankfully in python 3 this gives a float
            if l_AverageScore[i] == 1:
                PerfectScoreCount += 1
                if PerfectScoreCount >= i_MaxOutput:
                    if b_Noisy:
                        print("Cutting list short. Many Perfect Solutions found.")
                    l_MaxScore[i] = max(l_PossibleOutcomes[1]) #make sure to do this before it breaks out, just in case.
                    l_AverageScore = l_AverageScore[:i+1] #trim the array
                    l_MaxScore = l_MaxScore[:i+1] #Trim the Max Score array, too (was causing errors elsewhere)
                    break
        l_MaxScore[i] = max(l_PossibleOutcomes[1])
    
    if b_Noisy:
        i_MinimumMaxScore = min(l_MaxScore)
        #i_MinimumMaxScore = min(i for i in l_MaxScore if i>0) #Want to only get outcomes that result in words, so score must be > 0. Turns out this was caused by stopping word generation, and only trimming one of the arrays
        l_IndexesOfScore = [i for i, j in enumerate(l_MaxScore) if j == i_MinimumMaxScore]
        print("The minimum of the maximum words left overall is "+str(i_MinimumMaxScore))
        f_averageAverageScore = 0
        l_Output = []
        f_MinimumAverage = 9999
        l_MinAverageList = []
        for i in range(len(l_IndexesOfScore)):
            l_Output.append(l_PossiblePlays[l_IndexesOfScore[i]])
            if (l_AverageScore[l_IndexesOfScore[i]]) < f_MinimumAverage:
                l_MinAverageList = []
                f_MinimumAverage = l_AverageScore[l_IndexesOfScore[i]]
                l_MinAverageList.append(l_PossiblePlays[l_IndexesOfScore[i]])
            elif (l_AverageScore[l_IndexesOfScore[i]]) == f_MinimumAverage:
                l_MinAverageList.append(l_PossiblePlays[l_IndexesOfScore[i]])
            f_averageAverageScore += l_AverageScore[l_IndexesOfScore[i]]
        f_averageAverageScore = f_averageAverageScore/len(l_IndexesOfScore)
        print("With an average of "+"{:.3f}".format(f_averageAverageScore)+" words left.")
        print("For the words:          "+str(l_Output))
        print("But a minimum average of "+"{:.3f}".format(f_MinimumAverage)+" words left")
        print("For the words:          "+str(l_MinAverageList))

    
    
    #scores calculated. find the minimum value
    f_minScore = min(l_AverageScore)
    if b_Noisy:
        print("On average, SuperSearch will result in "+"{:.3f}".format(f_minScore)+" words left.")
    i_IndexesOfScore = [i for i, j in enumerate(l_AverageScore) if j == f_minScore]
    if len(i_IndexesOfScore) == 1:
        if b_Noisy:
            print("With a the maximum being "+str(l_MaxScore[i_IndexesOfScore[0]]))
        return [l_PossiblePlays[i_IndexesOfScore[0]]]
    else:
        i_MinimumMaxScore = 999999
        i_indexOfMinMax = 0
        l_OutputWords = []
        for i in range(len(i_IndexesOfScore)):
            if l_MaxScore[i_IndexesOfScore[i]] < i_MinimumMaxScore:
                i_MinimumMaxScore = l_MaxScore[i_IndexesOfScore[i]]
                i_indexOfMinMax = i_IndexesOfScore[i]
                l_OutputWords = [l_PossiblePlays[i_IndexesOfScore[i]]]
            elif l_MaxScore[i_IndexesOfScore[i]] == i_MinimumMaxScore:
                l_OutputWords.append(l_PossiblePlays[i_IndexesOfScore[i]])
        if b_Noisy:
            print("With a the maximum being "+str(i_MinimumMaxScore))
        return l_OutputWords #This used to only hold extra choices, but now it holds all of them. Just streamlines the code.

def FindWordWithLetters_refactor(wantedLetters, wordList):
    """Prints words from list wordList with the most number of letters from list wantedLetters.\n
    this was more a proof of concept that the new suggestWord can function much the same. but not exactly. it misses the finer points"""
    foundWords = suggestWord(wordList, 0, False, False, [], wantedLetters, True, True)
    if len(foundWords) == 1:
        print("The only/best word I can find is \""+foundWords[0]+"\".")
    elif len(foundWords) > 1:
            print("Words containing "+str(wantedLetters)+":")
            for i in range(len(foundWords)):
                print(foundWords[i])
    else:
        print("I couldn't find a word.") #it's possible the wordlist handed over contains none of the wanted letters, but it should've still handed back a random word.

def FindWordWithLetters(wantedLetters, wordList) -> None:
    """Prints words from list wordList with the most number of letters from list wantedLetters"""
    countLettersHit = [0]*len(wordList)
    for i in range(len(wordList)):
        #for every legal word, we're gonna count the amount of mc, mid, and lc letters
        #eh, just the most common for now
        #countMostCommonHit[i] = len(set(wantedLetters) & set(wordList[i])) #turns out this unfairly weights words that have duplicate letters. I don't want that. I want UNIQUE letters to filter by!
        lettersInWord = []
        for char in wordList[i]:
            if char not in lettersInWord:
                lettersInWord.append(char)
        countLettersHit[i] = len(set(wantedLetters) & set(lettersInWord)) #this takes a little longer, but should stop reccomendations of vastly different value being suggested.
    #find the remaining word with the most most-common letters and suggest that
    maxLettersHit = max(countLettersHit)
    maxHitWords = [i for i, j in enumerate(countLettersHit) if j == maxLettersHit] #this is a list of indexes in wordList where the max hit words reside
    if maxLettersHit != len(wantedLetters) and len(maxHitWords) != 0: #if we didn't find all the letters, but we have at least one result
        print("I was unable to find any words containing all of the letters. The top results are shown instead.")
    if len(maxHitWords) > 1:
        print("Words containing "+str(wantedLetters)+":")
        for i in range(len(maxHitWords)):
            print(wordList[maxHitWords[i]])
    elif len(maxHitWords) == 1:
        print("The only/best word I can find is \""+wordList[maxHitWords[0]]+"\".")
    else:
        print("I couldn't find a word.") #it's possible the wordlist handed over contains none of the wanted letters





    



#program
wordLen = input("Length of word: ")
try:
    wordLen = int(wordLen)
except: #they didn't enter a proper number
    print("Finding any length word.")
    wordLen = 10 #for edge purposes/a generic length for word suggestion to give
    b_AnyWordLength = True 

print("NOTE: for every yes/no question, blank responses are \"no\", and any response is considered \"yes\"")
b_HardMode = False #assume this until proven otherwise. Helps with things like finding words with arbitrary letters.
b_WordleMode = bool(input("Wordle mode: "))
if not b_WordleMode: 
    b_KnowAllPositions = bool(input("Hangman rules (All letter positions known)? "))
else:
    b_KnowAllPositions = False
    b_HardMode = bool(input("Is Hard Mode active? "))
if not b_KnowAllPositions:
    b_SuperSearch = bool(input("Enable SuperSearch (Very slow, but the best possible outcome)? "))
    if not b_SuperSearch:
        b_SuperSearchConfirmed = False
build_dictionary(wordLen,bannedChars)
if not b_HardMode: #only bother populating it if we're gonna use it
    WholeWordList += legalWords
    load_extra_wordlists(wordLen,bannedChars)


if (not b_KnowAllPositions) and (not b_WordleMode):
    findLetters = input("If you just want to find a word matching some letters, enter them now: ")
    if findLetters != "":
        Letters = []
        for char in findLetters:
            Letters.append(char)
        FindWordWithLetters(Letters,WholeWordList)
        quit() #why I can't just return when not in a function is beyond me...
b_FirstRun = True
while len(legalWords) > 1:
    genStats(legalWords, wordsContainingLetters, None, False) #the "None" could be replaced with "letterStats" but honestly: I never ended up using it. So processing it is a waste of time.
    print("\n\n\n")
    print(str(len(legalWords))+" words remaining.")
    if len(legalWords)<=75:
        print("Remaining words:")
        for word in legalWords:
            print(word)
        print("--END OF WORDS--")
        if not b_SuperSearchConfirmed:
            b_SuperSearch = bool(input("Do you want to enable SuperSearch now? "))
            b_SuperSearchConfirmed = True
    #suggestWord(wordLen, unknownPositions, b_KnowAllPositions)
    suggestWord(legalWords, wordLen+1, b_KnowAllPositions, b_HardMode, WholeWordList, [], True, True) #to be most faithful to the first part of the function, I originally used "(1+wordLen-len(unknownPositions))" but wordLen+1 is actually the part used later in the function
    if b_SuperSearch & (not b_FirstRun):
        OptimalWord = FindOptimalPlay(legalWords,b_HardMode,WholeWordList)
        print("SuperSearch Suggestion: "+str(OptimalWord))
    InterrogateUserForInfo_and_FilterWordlist(b_KnowAllPositions, b_WordleMode)
    b_FirstRun = False
try:
    print("Your word is: "+legalWords[0])
except IndexError:
    print("Something went wrong. I don't know a word that fits.")