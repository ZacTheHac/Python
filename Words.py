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

    #load combined file that eliminated 7,506,911 duplicates (~7MB)
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


def genStats(noisy = True) -> None:
    """Pulls words from legalWords and outputs how common certain letters are into the global letterStats (all instances), and wordsContainingLetters (one instance counted per word)"""
    global letterStats
    global wordsContainingLetters
    global legalWords

    totalChars=0
    newLetterStats = [0] * 26
    for word in legalWords:
        for char in word:
            try:
                ind = string.ascii_letters.index(char)
                newLetterStats[ind] += 1
                #print(str(char)+"'s = "+str(letterStats[ind]))
                totalChars += 1
            except ValueError:
                print("Non-ascii character found: "+char)
    letterStats = newLetterStats

    #more useful counts: only count one instance per word
    charsSeen = []
    newWordsContainingLetters = [0]*26
    for word in legalWords:
        for char in word:
            try:
                if char not in charsSeen:
                    charsSeen.append(char)
                    ind = string.ascii_letters.index(char)
                    newWordsContainingLetters[ind] += 1
            except ValueError:
                print("Non-ascii character found: "+char)
        charsSeen = []
    wordsContainingLetters = newWordsContainingLetters

    if noisy:
        maxCount = max(letterStats)
        #find all instances of that count
        maxLetters = [i for i, j in enumerate(letterStats) if j == maxCount]
        #normalize the indexes into characters
        for i in range(len(maxLetters)):
            maxLetters[i] = chr(maxLetters[i]+97)
        if len(maxLetters) > 1:
            letters = ""
            for letter in maxLetters:
                letters += letter
                letters += ", "
            print("Most common letters are: "+letters+"with a count of "+str(maxCount)+" each.")
        else:
            print("Most common letter is: "+str(maxLetters[0])+" with a count of "+str(maxCount)+".")

        minCount = min(letterStats)
        minLetters = [i for i, j in enumerate(letterStats) if j == minCount]
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

    if noisy:
        maxCount = max(wordsContainingLetters)
        #find all instances of that count
        maxLetters = [i for i, j in enumerate(wordsContainingLetters) if j == maxCount]
        #normalize the indexes into characters
        for i in range(len(maxLetters)):
            maxLetters[i] = chr(maxLetters[i]+97)

        if len(maxLetters) > 1:
            letters = ""
            for letter in maxLetters:
                letters += letter
                letters += ", "
            print("Most common letters are: "+letters+"with "+str(maxCount)+" words each.")
        else:
            print("Most common letter is: "+str(maxLetters[0])+" in "+str(maxCount)+" words.")

        minCount = min(wordsContainingLetters)
        minLetters = [i for i, j in enumerate(wordsContainingLetters) if j == minCount]
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

def filterWordlist(hangmanRules,WordleMode) -> None:
    global bannedChars
    global unknownPositions
    global knownPositions
    global legalWords

    if WordleMode:
        s_WordAttempt = input("Enter the word you tried: ").lower()
        s_WordOutcome = input("How did that go for you? (y=yellow, g=green, anything else = grey) ").lower()
        #yellows added to unknowPositions, Greens added to filter, greys added to banned chars
        #edge cases: guessed a double letter when only a single exists. make sure to not add it to banned. however, it also means the letter is not there.
        if len(s_WordOutcome) < len(s_WordAttempt):
            print("You're that lazy? Going to assume the rest are grey.")
            s_WordOutcome = s_WordOutcome.ljust(len(s_WordAttempt),".")
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
            if l_GreyLetters[i] in l_GreenLetters:
                print("Looks like there's no more \""+l_GreyLetters[i]+"\" in the word.")
                l_FoundAll.append(l_GreyLetters[i])
                l_GreyLetters[i] = ""
            elif l_GreyLetters[i] in l_YellowLetters:
                print("Looks like there's no more \""+l_GreyLetters[i]+"\" in the word.")
                #We don't know where it goes, so fullban isn't possible, and we already added it to filter string. so just remove the entry
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


    newLegalWords = []
    for word in legalWords:
        if not any(bannedCharacter in bannedChars for bannedCharacter in word): #no banned letters
            if StrContainsAllLettersWithCount(word,unknownPositions): #all(needLetter in word for needLetter in neededLetters): #contains the letters we need
                if re.search(knownPositions, word):
                    newLegalWords.append(word)
    legalWords = newLegalWords

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

def mostCommonLetters(maxLetters, filterMaxCounts = True, noisy = True) -> list:
    global unknownPositions
    global wordsContainingLetters
    global legalWords

    topLetters = [""]*maxLetters
    topLetterCounts = [0]*maxLetters #i could do this as a 2D array, but I don't wanna!

    for i in range(len(wordsContainingLetters)):
        minValue = min(topLetterCounts)
        minValueIndex = topLetterCounts.index(minValue)
        if(wordsContainingLetters[i]>minValue)& ((wordsContainingLetters[i] < len(legalWords)) or not filterMaxCounts): #make sure the new value is larger than the minimum, but isn't in EVERY word. That's just not fun.
            char = chr(i+97)
            if (char not in unknownPositions) & (char not in topLetters):
                topLetters[minValueIndex] = char
                topLetterCounts[minValueIndex] = wordsContainingLetters[i]
    
    #now sort them
    sortedTopLetters = []
    for i in range(maxLetters):
        topLetterIndex = topLetterCounts.index(max(topLetterCounts))
        if(topLetterCounts[topLetterIndex] > 0): #if it's a zero count, it won by default, ignore it.
            sortedTopLetters.append(topLetters[topLetterIndex])
            topLetterCounts[topLetterIndex] = 0 #zero out the counter so it can't be used again

    if noisy:
        print("Top "+str(len(sortedTopLetters))+" unknown letters:")
        print(str(sortedTopLetters))
        #repair the top letter counts
        for i in range(len(sortedTopLetters)):
            ind = string.ascii_letters.index(sortedTopLetters[i])
            topLetterCounts[i] = wordsContainingLetters[ind]
        print(str(topLetterCounts[0:len(sortedTopLetters)]))
    return sortedTopLetters

def leastCommonLetters(maxLetters, noisy = True) -> list:
    global bannedChars
    global wordsContainingLetters

    maxNumber = 999999
    lowLetters = [""]*maxLetters
    lowLetterCounts = [maxNumber]*maxLetters #i could do this as a 2D array, but I don't wanna!

    for i in range(len(wordsContainingLetters)):
        maxValue = max(lowLetterCounts)
        maxValueIndex = lowLetterCounts.index(maxValue)
        if(wordsContainingLetters[i]<maxValue) & (wordsContainingLetters[i] > 0):
            char = chr(i+97)
            
            if (char not in bannedChars) & (char not in lowLetters):
                if (wordsContainingLetters[i] < len(legalWords)):
                    lowLetters[maxValueIndex] = char
                    lowLetterCounts[maxValueIndex] = wordsContainingLetters[i]
                elif char not in unknownPositions: #i found out I had to add this because occasionally it would tell me this for letters I KNEW were in everything
                    print(char+" was removed because it's in everything.")

    #now sort them
    sortedBottomLetters = []
    for i in range(maxLetters):
        bottomLetterIndex = lowLetterCounts.index(min(lowLetterCounts))
        if(lowLetterCounts[bottomLetterIndex] < maxNumber): #if it's a max count, it won by default, ignore it.
            sortedBottomLetters.append(lowLetters[bottomLetterIndex])
            lowLetterCounts[bottomLetterIndex] = maxNumber #max out the counter so it can't be used again

    if noisy:
        print("Lowest "+str(len(sortedBottomLetters))+" unbanned letters:")
        print(str(sortedBottomLetters))
        #repair the top letter counts
        for i in range(len(sortedBottomLetters)):
            ind = string.ascii_letters.index(sortedBottomLetters[i])
            lowLetterCounts[i] = wordsContainingLetters[ind]
        print(str(lowLetterCounts[0:len(sortedBottomLetters)]))
    return sortedBottomLetters

def medianLetters(maxLetters, noisy = True) -> list:
    """Returns a list of the letter that occurs the high median in the global \"legalWords\" based on values found in the global \"wordsContainingLetters\"\n
    All 0 counts are removed from consideration, so the median returned may be higher than the whole list would suggest.\n
    if maxLetters>1, the further items will be the letters surrounding the median letter\n
    if maxLetters is even, the true median will be right after the halfway point, and the found letters will fill the first half\n
    if maxLetters is odd, the high median will be in the center of the returned list.\n
    noisy determines if the function prints out its findings to the console. True is to print, and is the default
    """

    #TODO: this code can easily softlock. either build in protection against that, or rewrite it to be unable to softlock.
    global wordsContainingLetters
    global legalWords

    medianLetters = [""]*maxLetters
    medianLetterCounts = [0]*maxLetters

    #make a list of values that are all nonzero
    nonzeroWCL = []
    for i in range(len(wordsContainingLetters)):
        if wordsContainingLetters[i]>0:
            nonzeroWCL.append(wordsContainingLetters[i])


    midLetterCount = statistics.median_high(nonzeroWCL)
    midLetter = chr(wordsContainingLetters.index(midLetterCount)+97)
    medianLetterCounts[math.ceil(maxLetters/2)-1] = midLetterCount
    medianLetters[math.ceil(maxLetters/2)-1] = midLetter

    #find the next smaller counts
    index = math.ceil(maxLetters/2)-2
    letterCount = midLetterCount
    while index >= 0:
        for c in range(letterCount-1,0,-1):
            try:
                letter = wordsContainingLetters.index(c)
                medianLetterCounts[index] = c
                medianLetters[index] = chr(letter+97)

                index -= 1
                letterCount = c
                break
            except ValueError:
                #do nothing of value
                pass
        if letterCount == 1:
            break #it's possible there's not enough values left to fill

    #find the next larger counts
    index = math.ceil(maxLetters/2)
    letterCount = midLetterCount
    while index < maxLetters:
        for c in range(letterCount+1,letterCount+10000): #highest known count was 7401 so we can stop it past there
            try:
                letter = wordsContainingLetters.index(c)
                medianLetterCounts[index] = c
                medianLetters[index] = chr(letter+97)

                index += 1
                letterCount = c
                break
            except ValueError:
                #do nothing of value
                pass
        if c == letterCount+9999:
            break #we ran out of things to search

    #filter out nonsense values if they exist
    filteredMedianLetters = []
    filteredMedianLetterCounts = []
    for i in range(maxLetters):
        if (medianLetterCounts[i] > 0):
            if((medianLetterCounts[i] < len(legalWords))):
                filteredMedianLetterCounts.append(medianLetterCounts[i])
                filteredMedianLetters.append(medianLetters[i])
            elif medianLetters[i] not in unknownPositions:
                print(medianLetters[i]+" was removed because it's in everything.")

    if noisy:
        print("middle "+str(len(filteredMedianLetters))+" letters:")
        print(str(filteredMedianLetters))
        print(str(filteredMedianLetterCounts))

    return filteredMedianLetters

def suggestWord_Refactor(wordList, numberOfLetters, hangmanRules=False, hardMode = True, wholeWordList = [], wantedLetters = [], noisy = True, returnList = False) -> list:
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
        mcLetters = mostCommonLetters(numberOfLetters, not hangmanRules, noisy) #if making a bot, set this to false as it can be very useful, it's also super useful when the positions of letters can really give a lot of info
        #TODO: mcLetters always grabs from the global legalWords. may want to refactor it to use an input wordlist. until then, there's NO reason to pass the legalwordlist and the whole wordlist in the same go for hardmode.
        if noisy:
            midLetters = medianLetters(numberOfLetters, noisy)
            lcLetters = leastCommonLetters(numberOfLetters, noisy)
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

def suggestWord(maxLetters, knownLetters, hangmanRules=False) -> None:
    """Prints words from global list \"legalWords\" that contain the most number of letters returned by mostCommonLetters()\n\n
    maxLetters is an int assumidly indicating how many letters long the word should be, but can be modified to fit your needs\n
    knownLetters is a list of letters you know to be in the word. Can be blank if you're not using that\n
    hangmanRules will just print the most common letter in the wordlist\n
    The function grabs maxLetters-len(knownLetters) letters from mostCommonLetters()\n
    \n
    This is very convoluted. Should be reworked to take the wordlist as an argument and a combined value for how many letters to look for.
    """
    global legalWords

    unknownCount = maxLetters - len(knownLetters)
    mcLetters = mostCommonLetters((unknownCount+1), not hangmanRules) #if making a bot, set this to false as it can be very useful, it's also super useful when the positions of letters can really give a lot of info
    midLetters = medianLetters((unknownCount+1))
    lcLetters = leastCommonLetters((unknownCount+1))

    if(hangmanRules):
        print("I would suggest trying \""+str(mcLetters[0])+"\".")
        return

    if unknownCount < 1:
        rnd = random.randrange(0,len(legalWords),1)
        print("I've got no guidance. Try \""+legalWords[rnd]+"\"?")
    else:
        countMostCommonHit = [0]*len(legalWords)
        mcUnknownLetters = mostCommonLetters(maxLetters+1, True, False)
        for i in range(len(legalWords)):
            #for every legal word, we're gonna count the amount of mc, mid, and lc letters
            #eh, just the most common for now
            #countMostCommonHit[i] = len(set(mcUnknownLetters) & set(legalWords[i])) #turns out this unfairly weights words that have duplicate letters. I don't want that. I want UNIQUE letters to filter by!
            lettersInWord = []
            for char in legalWords[i]:
                if char not in lettersInWord:
                    lettersInWord.append(char)
            countMostCommonHit[i] = len(set(mcUnknownLetters) & set(lettersInWord)) #this takes a little longer, but should stop reccomendations of vastly different value being suggested.
        #find the remaining word with the most most-common letters and suggest that
        maxMCHit = max(countMostCommonHit)
        maxHitWords = [i for i, j in enumerate(countMostCommonHit) if j == maxMCHit] #this is a list of indexes in legalWords where the max hit words reside
        if len(maxHitWords) > 1:
            print("A few suggestions:")
            for i in range(min(len(maxHitWords),20)):
                print(legalWords[maxHitWords[i]])
            if(len(maxHitWords) > 20):
                startIndex = 20
            else:
                startIndex = 0
            rnd = random.randrange(startIndex,len(maxHitWords),1)
            print("Might I suggest trying \""+legalWords[maxHitWords[rnd]]+"\"?")
        elif len(maxHitWords) == 1:
            print("Might I suggest trying \""+legalWords[maxHitWords[0]]+"\"?")
        else:
            print("Something severely broke when trying to suggest a word.") #the list shouldn't ever be empty. Only thing I can think of is if all letters are known, so mcLetters is empty, so all counts are 0
            #so I'll use the ol standby:
            rnd = random.randrange(0,len(legalWords),1)
            print("Try \""+legalWords[rnd]+"\"?")
        

#let it run to the old suggester, too.
#sometimes the fancy stuff doesn't make words the thing will accept

    try:
        lettersToSearchFor = []
        #find up to 3 of the most common letters
        rnd = random.randint(1,3)
        for i in range(rnd):
            rndlet = random.randrange(0,len(mcLetters),1)
            lettersToSearchFor.append(mcLetters[rndlet])

        #find up to 2 mid-range values
        rnd = random.randint(0,2)
        for i in range(rnd):
            rndlet = random.randrange(0,len(midLetters),1)
            lettersToSearchFor.append(midLetters[rndlet])

        #maybe even throw in a low-value letter
        rnd = random.randint(0,1)
        for i in range(rnd):
            rndlet = random.randrange(0,len(lcLetters),1)
            lettersToSearchFor.append(lcLetters[rndlet])

        #dedupe the list (important in late game)
        lettersToSearchFor = list(dict.fromkeys(lettersToSearchFor)) #just mash it into keys. keys can't be duped, so they're eliminated.

        #try to find a word that includes all these letters
        purgatory = True
        while purgatory:
            suggestableWordlist = []
            for word in legalWords:
                if all(needLetter in word for needLetter in lettersToSearchFor): #contains the letters we want
                    suggestableWordlist.append(word)
            if len(suggestableWordlist) != 0:
                rnd = random.randrange(0,len(suggestableWordlist),1)
                print("Might I suggest trying \""+suggestableWordlist[rnd]+"\"?")
                purgatory = False
            else:
                #print("Failed to find a word to suggest. Retrying.")
                #crude weighted random. 50% of the time it tries to remove the last element since it's probably the one breaking it.
                rnd = random.randrange(0,(len(lettersToSearchFor)*2),1)
                rnd = min(rnd,(len(lettersToSearchFor)-1)) #clip the value to a possible element
                #print("Removing "+str(lettersToSearchFor[rnd])+".")
                lettersToSearchFor[rnd] = "" #remove that element
    except ValueError: #very rare case: end up with a list of words that are all made of the same letters but no direction as to how they're arranged, the rands can't give back on a 0,0, so they error.
        #print("I cannot make a suggestion at this time.")
        rnd = random.randrange(0,len(legalWords),1)
        print("I dunno, man? Try \""+legalWords[rnd]+"\"?")

def FindWordWithLetters_refactor(wantedLetters, wordList):
    """Prints words from list wordList with the most number of letters from list wantedLetters.\n
    this was more a proof of concept that the new suggestWord can function much the same. but not exactly. it misses the finer points"""
    foundWords = suggestWord_Refactor(wordList, 0, False, False, [], wantedLetters, True, True)
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
b_WordleMode = bool(input("Wordle mode: "))
if not b_WordleMode: 
    b_KnowAllPositions = bool(input("Hangman rules (All letter positions known)? "))
else:
    b_KnowAllPositions = False
    b_HardMode = bool(input("Is Hard Mode active? "))
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
        FindWordWithLetters(Letters,legalWords)
        quit() #why I can't just return when not in a function is beyond me...

while len(legalWords) > 1:
    genStats(False)
    print("\n\n\n")
    print(str(len(legalWords))+" words remaining.")
    if len(legalWords)<=75:
        print("Remaining words:")
        for word in legalWords:
            print(word)
        print("--END OF WORDS--")
    #suggestWord(wordLen, unknownPositions, b_KnowAllPositions)
    suggestWord_Refactor(legalWords, wordLen+1, b_KnowAllPositions, b_HardMode, WholeWordList, [], True, True) #to be most faithful to the first part of the function, I originally used "(1+wordLen-len(unknownPositions))" but wordLen+1 is actually the part used later in the function
    filterWordlist(b_KnowAllPositions, b_WordleMode)
try:
    print("Your word is: "+legalWords[0])
except IndexError:
    print("Something went wrong. I don't know a word that fits.")