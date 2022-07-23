"""Hangman except the computer hates you"""
#Basic premise: Hangman, except the computer is trying to get you to lose, so it constantly gives you the least knowledge possible by picking a result that fits the most number of words.
#example: wordlist of "what, when, then", if a W is guessed, it would be filled in, as there are more Ws, if e were guessed, then it would be filled, as more words have that.
#The standard hangman game has about 6 wrong guesses allowed. The computer could easily win in this space, so the wrong guesses would have to be larger or infinite
#an element of randomness should play a part in this, or known strategies break the fun. maybe a variance of 10% on what the "most" common fit would be. This would mean sometimes the computer gives itself a smaller space to work in, but stops known cornering strats

import io
import math
import random
import re
#import time
#import timeit


#global variables
l_BannedChars = ["'","Å","â","ä","á","å","ç","é","è","ê","í","ñ","ó","ô","ö","ü","û","-"," "] #sometimes the wordlist comes with a whole lot of non-english characters, or characters that make hangman unfun. 
i_WordLen = 10
l_WordList = [] #will hold all the words that we can still pick from
s_GivenInfo = "" #holds a string representation of the information players have for display and filtering.
l_WrongGuesses = []
i_MaxErrorCount = 13

def load_dict(file,StorageList):
    """Opens the file at path file, and appends the list to StorageList"""
    fileDict=io.open(file, mode="r", encoding="utf-8")
    dictionary = fileDict.readlines()
    dictsize = int(len(dictionary))
    StorageList += dictionary

def optimize_wordlist(wordList,wordLength,bannedCharacters) -> list:
    """
    Returns all words in \"wordList\" that are not \"wordLength\" characters long or contains any of \"bannedCharacters\"\n
    The new list is deduplicated and sorted alphabetically."""

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

def filter_wordlist(l_wordList, s_matchPattern, l_NotPresentChars=[]) -> list:
    """returns a wordlist in which all words match the regex s_matchPattern and contain no characters from l_NotPresentChars\n
    the regex is modified so all \".\" are replaced with a search that excludes all other letters in the regex."""
    if s_matchPattern != "":
        knownCharacters = ""
        for char in s_matchPattern:
            if char.isalpha() & (char not in knownCharacters):
                knownCharacters += char
        if knownCharacters != "": #if the string was empty/all unknown, don't bother with anything
            filterBlock = "[^"+knownCharacters.lower()+"]"
            s_matchPattern = s_matchPattern.replace(".",filterBlock)
        regex_matchPattern = re.compile(s_matchPattern)
        l_wordList = list(filter(regex_matchPattern.match,l_wordList)) #run the list against regex all at once

    if l_NotPresentChars != []:
        newWordList = []
        for word in l_wordList:
            if not any(bannedCharacter in l_NotPresentChars for bannedCharacter in word): #no banned letters
                newWordList.append(word)
        return newWordList
    else:
        return l_wordList

def generate_FilterCombinations(s_Pattern, c_ComboCharacter, i_startIndex = 0) -> list:
    """Using recusion, generates most of the combinations you can make from replacing \".\" with c_ComboCharacter in s_Pattern\n
    However, this will only allow up to length/4 replacement characters, as beyond that is considered an edge case"""
    i_BlankSpots = 0
    i_AlreadyFilledSpots = 0
    for i in range(0,len(s_Pattern)):
        if s_Pattern[i] == c_ComboCharacter:
            i_AlreadyFilledSpots +=1
    for i in range(i_startIndex, len(s_Pattern)):
        if s_Pattern[i] == ".":
            i_BlankSpots += 1

    #i_BlankSpots = s_Pattern.count(".") #can't be used because we only care about results AFTER where we start
    l_Combinations = []
    l_Combinations.append(s_Pattern)
    if i_BlankSpots < 1 or (i_AlreadyFilledSpots > len(s_Pattern)/4): #no more blank spots OR an unreasonable amount of one letter
        return l_Combinations
    l_BlankSpotIndices = []
    i_currIndex = i_startIndex
    for BlankNum in range(1,i_BlankSpots+1):
        i_foundIndex = s_Pattern.index(".",i_currIndex)
        l_BlankSpotIndices.append(i_foundIndex)
        i_currIndex = i_foundIndex+1
    #indices of blank spots found
    for BlankNum in range(0,i_BlankSpots):
        s_NewPattern = str_Replace(s_Pattern, l_BlankSpotIndices[BlankNum], c_ComboCharacter)
        l_Combinations.extend(generate_FilterCombinations(s_NewPattern, c_ComboCharacter, l_BlankSpotIndices[BlankNum]+1)) #append makes a list in a list, extend adds the items. Also: recursion is fun~
    l_Combinations = list(dict.fromkeys(l_Combinations)) #dedupe, just in case.
    #if i_startIndex == 0:
    #    print(str(len(l_Combinations))+" combinations found.")
    return l_Combinations

def str_Replace(s_Original, i_index, c_Replacement) -> str:
    """Returns a string with the character at i_index in s_Original replaced with c_Replacement"""
    return s_Original[:i_index]+c_Replacement+s_Original[i_index+1:]

def RemovedFromList(l_filteredList, l_UnfilteredList) -> list:
    """Returns a list showing what l_filteredList is missing from l_UnfilteredList"""
    return list(set(l_UnfilteredList) - set(l_filteredList)) #more than double the speed than doing it individually.

def display_hangman(s_knownInfo,l_wrongGuesses, i_MaxAllowedErrors):
    """Handles displaying all gameplay information, from the blanks to the gallows"""
    f_errorPercent = len(l_wrongGuesses)/i_MaxAllowedErrors
    drawGallows(f_errorPercent)

    s_knownInfo = s_knownInfo.replace(".","_ ")
    print(s_knownInfo)

    s_wrongGuesses = str(l_wrongGuesses)
    s_wrongGuesses = s_wrongGuesses[1:len(s_wrongGuesses)-1] #use the default list to string conversion and cut off the []
    if  s_wrongGuesses != "":
        print("Wrong guesses: "+s_wrongGuesses)

def drawGallows(f_PercentComplete):
    """Prints ASCII art depending on the percentage passed in. 0% is empty, 100% is complete"""
    s_Gallows0 = ""
    s_Gallows1 = """ Original art by: Krzysztof Biolik
         ________________________
        /                         4
       /                         /|
      /                         / /
     /                         / /
    /                         / /
   /                         / / 
  /                         / /
 /                         / / 
/                         / /  
\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"|/   
__________________________f|   
"""
    s_Gallows2 = """ Original art by: Krzysztof Biolik
         _________________________
        /                         4
       /                         /|
      /                         / /
     /                         / /|
    /                         / /||
   /                         / / ||
  /                         / /| ||
 /                         / / | ||
/                         / /  | ||
\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"|/   | ||
__________________________f|   | |
| ||                    | ||
| ||                    | ||
| ||                    | ||
| ||                    | ||
| ||                    | ||
| |                     | |
"""
    s_Gallows3 = """ Original art by: Krzysztof Biolik
     _______________,,.
    /_____________.;;'/|
   |\"____  _______;;;]/
   | || //'         |
   | ||//'          |
   | |//'           |
   |  /'            |
   | ||             |
   | ||             |
   | ||             |
   | ||             |
   | ||             |
   | ||             |
   | ||             |
   | ||             |
   | ||             |
   | ||   __________|______________
   | ||  /          |             4
   | || /           |            /|
   | ||/            |           / /
   | ||           /---\        / /|
   | ||       ___||/|\ |      / /||
   |_|/        ---\___/      / / ||
  /                         / /| ||
 /                         / / | ||
/                         / /  | ||
\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"|/   | ||
__________________________f|   | |
| ||                    | ||
| ||                    | ||
| ||                    | ||
| ||                    | ||
| ||                    | ||
| |                     | |
"""
    s_Gallows4 = """ Original art by: Krzysztof Biolik & Riitta Rasimus
     _______________,,.
    /_____________.;;'/|
   |\"____  _______;;;]/
   | || //'         ;
   | ||//'          ;
   | |//'           ;
   |  /'            $
   | ||             $
   | ||             $
   | ||            ,^.
   | ||            | |
   | ||            `.'
   | ||
   | ||
   | ||
   | ||
   | ||   _________________________
   | ||  /                        4
   | || /        ________        /|
   | ||/        |_/__\___|      / /
   | ||          ||: || |      / /|
   | ||          ||: || |     / /||
   |_|/          ||==||=|    / / ||
  /              ||: || |   / /| ||
 /                         / / | ||
/                         / /  | ||
\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"|/   | ||
__________________________f|   | |
| ||                    | ||
| ||                    | ||
| ||                    | ||
| ||                    | ||
| ||                    | ||
| |                     | |
"""
    s_Gallows5 = """ Original art by: Krzysztof Biolik & Riitta Rasimus
     _______________,,.
    /_____________.;;'/|
   |\"____  _______;;;]/       
   | || //'         ;
   | ||//'          ;
   | |//'           ;     
   |  /'            $
   | ||             $       
   | ||             $        
   | ||            ,^.        
   | ||            | |        
   | ||            `.'       
   | ||                     
   | ||                    
   | ||      *MENACING MUSIC*
   | ||                     
   | ||   _________________________
   | ||  /                        4
   | || /        ________        /|
   | ||/        |_/__\___|      / /
   | ||          ||: || |      / /|
   | ||          ||: || |     / /||
   |_|/          ||==||=|    / / ||
  /              ||: || |   / /| ||
 /                         / / | ||
/                         / /  | ||
\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"|/   | ||
__________________________f|   | |
| ||                    | ||
| ||                    | ||
| ||                    | ||
| ||                    | ||
| ||                    | ||
| |                     | |
"""
    s_Gallows6 = """ Original art by: Krzysztof Biolik & Riitta Rasimus
     _______________,,.
    /_____________.;;'/|
   |\"____  _______;;;]/      ゴ
   | || //'         ;
   | ||//'          ;
   | |//'           ;    ゴ
   |  /'            $
   | ||             $      ゴ
   | ||             $       ゴ
   | ||            ,^.       ゴ
   | ||            | |       ゴ
   | ||            `.'      ゴ
   | ||                    ゴ
   | ||                   ゴ
   | ||      *MENACING MUSIC*
   | ||                    ゴ
   | ||   __________________ゴ______
   | ||  /                   ゴ    4
   | || /        ________    ゴ   /|
   | ||/        |_/__\___|      / /
   | ||          ||: || |      / /|
   | ||          ||: || |     / /||
   |_|/          ||==||=|    / / ||
  /              ||: || |   / /| ||
 /                         / / | ||
/                         / /  | ||
\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"|/   | ||
__________________________f|   | |
| ||                    | ||
| ||                    | ||
| ||                    | ||
| ||                    | ||
| ||                    | ||
| |                     | |
"""
    s_Gallows7 = """ Original art by: Krzysztof Biolik, Riitta Rasimus, & makeindiadankabhiyan
     _______________,,.
    /_____________.;;'/|
   |\"____  _______;;;]/      ゴ
   | || //'         ;
   | ||//'          ;
   | |//'           ;    ゴ
   |  /'            $
   | ||             $      ゴ                    ⣀⡀                           ⣴⣿⣿⠿⣫⣥⣄
   | ||             $       ゴ             ⢀   ⠾⢿⢟⣵⣾⣿⡿⠃                 ⣰⡿⣀⣤⣴⣾⣿⡇⠙⠛⠁
   | ||            ,^.       ゴ         ⣠⣾⣿⣿⣿⣿⣿⣿⣿⠁                    ⣴⣿⣿⠿⠛⠉⢩⣿⣿⡇        ⣀⣀⡀
   | ||            | |       ゴ        ⠈⠛⠉    ⢸⣿⣿⡇           ⢀⣼⡿⣫⣾⠆  ⢀⣶⣶⣶⣶⣶⣶⣿⣿⣿⠇   ⣠⣎⣠⣴⣶⠎⠛⠁
   | ||            `.'      ゴ         ⣾⣿⣿⣿⣿⠿⠿⠟⠛⠋      ⢀⣼⣿⠿⠛⣿⡟          ⠛⠉⠉      ⠘⠉  ⢸⣿⡇
   | ||                    ゴ                         ⣼⣿⣿⣿⡿⠿⠃                    ⣼⣿⣿⣿⡿⠿⠃
   | ||                   ゴ                          ⠋⠉                       ⣀⡀
   | ||      *MENACING MUSIC*                  ⣴⣿⣿⠿⣫⣥⣄                   ⢀   ⠾⢿⢟⣵⣾⣿⡿⠃
   | ||                    ゴ             ⣰⡿⣀⣤⣴⣾⣿⡇⠙⠛⠁                 ⣠⣾⣿⣿⣿⣿⣿⣿⣿⠁
   | ||   __________________ゴ____      ⣴⣿⣿⠿⠛⠉⢩⣿⣿⡇        ⣀⣀⡀       ⠈⠛⠉    ⢸⣿⣿⡇       ⢀⣼⡿⣫⣾⠆
   | ||  /                   ゴ   4    ⢀⣶⣶⣶⣶⣶⣶⣿⣿⣿⠇   ⣠⣎⣠⣴⣶⠎⠛⠁       ⣾⣿⣿⣿⣿⠿⠿⠟⠛⠋   ⢀⣼⣿⠿⠛⣿⡟
   | || /        ________    ゴ  /|    ⠛⠉⠉          ⠘⠉  ⢸⣿⡇                      ⣼⣿⣿⣿⡿⠿⠃
   | ||/        |_/__\___|      / /                 ⣼⣿⣿⣿⡿⠿⠃
   | ||          ||: || |      / /|
   | ||          ||: || |     / /||
   |_|/          ||==||=|    / / ||
  /              ||: || |   / /| ||
 /                         / / | ||
/                         / /  | ||
\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"|/   | ||
__________________________f|   | |
| ||                    | ||
| ||                    | ||
| ||                    | ||
| ||                    | ||
| ||                    | ||
| |                     | |
    """
    s_Gallows8 = """ Original art by: Krzysztof Biolik
     _______________,,.
    /_____________.;;'/|
   |\"____  _______;;;]/
   | || //'         ;
   | ||//'          ;
   | |//'           ;
   |  /'            $
   | ||             $
   | ||             $
   | ||            ,^.
   | ||            | |
   | ||            `.'
   | ||
   | ||
   | ||
   | ||
   | ||   _________________________
   | ||  /                        4
   | || /                        /|
   | ||/           _____        / /
   | ||           /|___/       / /|
   | ||          / |  /       / /||
   |_|/         / cj /       / / ||
  /             \"\"\"\"\"       / /| ||
 /                         / / | ||
/                         / /  | ||
\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"\"|/   | ||
__________________________f|   | |
| ||                    | ||
| ||                    | ||
| ||                    | ||
| ||                    | ||
| ||                    | ||
| |                     | |
YOU ARE DEAD.
"""
    s_JoJoMenacing = """
                        ⣀⡀                           ⣴⣿⣿⠿⣫⣥⣄
             ⢀   ⠾⢿⢟⣵⣾⣿⡿⠃                  ⣰⡿⣀⣤⣴⣾⣿⡇⠙⠛⠁
          ⣠⣾⣿⣿⣿⣿⣿⣿⣿⠁                    ⣴⣿⣿⠿⠛⠉⢩⣿⣿⡇        ⣀⣀⡀
        ⠈⠛⠉    ⢸⣿⣿⡇      ⢀⣼⡿⣫⣾⠆        ⢀⣶⣶⣶⣶⣶⣶⣿⣿⣿⠇   ⣠⣎⣠⣴⣶⠎⠛⠁
        ⣾⣿⣿⣿⣿⠿⠿⠟⠛⠋  ⢀⣼⣿⠿⠛⣿⡟            ⠛⠉⠉         ⠘⠉  ⢸⣿⡇
                    ⣼⣿⣿⣿⡿⠿⠃
                    ⠋⠉                             ⣀⡀
                  ⣴⣿⣿⠿⣫⣥⣄                   ⢀   ⠾⢿⢟⣵⣾⣿⡿⠃
            ⣰⡿⣀⣤⣴⣾⣿⡇⠙⠛⠁                  ⣠⣾⣿⣿⣿⣿⣿⣿⣿⠁
         ⣴⣿⣿⠿⠛⠉⢩⣿⣿⡇          ⣀⣀⡀       ⠈⠛⠉    ⢸⣿⣿⡇        ⢀⣼⡿⣫⣾⠆
        ⢀⣶⣶⣶⣶⣶⣶⣿⣿⣿⠇   ⣠⣎⣠⣴⣶⠎⠛⠁      ⣾⣿⣿⣿⣿⠿⠿⠟⠛⠋  ⢀⣼⣿⠿⠛⣿⡟
        ⠛⠉⠉            ⠘⠉  ⢸⣿⡇                          ⣼⣿⣿⣿⡿⠿⠃
                        ⠋⠉
    """

    i_GallowsIndex = math.floor(f_PercentComplete*9)
    #Keep getting an error that match isn't supported until 3.10, whatever, Ill do this the ugly way
    if i_GallowsIndex == 0:
        print(s_Gallows0)
    elif i_GallowsIndex == 1:
        print(s_Gallows1)
    elif i_GallowsIndex == 2:
        print(s_Gallows2)
    elif i_GallowsIndex == 3:
        print(s_Gallows3)
    elif i_GallowsIndex == 4:
        print(s_Gallows4)
    elif i_GallowsIndex == 5:
        print(s_Gallows5)
    elif i_GallowsIndex == 6:
        print(s_Gallows6)
    elif i_GallowsIndex == 7:
        print(s_Gallows7)
    elif i_GallowsIndex == 8:
        print(s_Gallows7)
    elif i_GallowsIndex == 9:
        print(s_Gallows8)
    else:
        print(s_Gallows8)

def getBestPlay(l_wordlist, s_CurrentLayout,c_CurrentGuess) -> str:
    """Returns the board layout that would most benefit the computer by giving the player the least amount of info possible."""
    l_Filters = [""]*len(l_wordlist) #it's possible each word has a different outcome! So just in case.
    l_FilterCounts = [0]*len(l_Filters)
    i_FilterIndex = 0
    for word in l_wordlist:
        str_Outcome = ""
        for letter in word:
            if letter.lower() == c_CurrentGuess:
                str_Outcome += c_CurrentGuess
            else:
                str_Outcome += "."
        #result string calculated, Merge the current layout and increment the list.
        for i in range(len(s_CurrentLayout)):
            if not s_CurrentLayout[i] == ".":
                str_Outcome = str_Replace(str_Outcome,i,s_CurrentLayout[i])
        #increment list
        if str_Outcome in l_Filters:
            i_TempIndex = l_Filters.index(str_Outcome)
        else:
            i_TempIndex = i_FilterIndex
            i_FilterIndex += 1
            l_Filters[i_TempIndex] = str_Outcome
        l_FilterCounts[i_TempIndex] += 1
    #when down to the final results, the bot will sometimes give up the win. The following code makes sure the answer given is as unhelpful as possible.
    i_BestResultScore = max(l_FilterCounts)
    l_BestResults = [i for i, j in enumerate(l_FilterCounts) if j == i_BestResultScore]
    if len(l_BestResults) > 1:
        l_BlanksLeft = [0]*len(l_BestResults)
        for i in range(len(l_BestResults)):
            i_BlanksLeft = 0
            for c in l_Filters[l_BestResults[i]]:
                if c == ".":
                    i_BlanksLeft +=1
            l_BlanksLeft[i] = i_BlanksLeft
        #all results had their blanks counted up. Want to pick the one with the most blanks. Don't give up if you don't have to!
        i_MaxBlanks = max(l_BlanksLeft)
        l_MaxBlanks = [i for i, j in enumerate(l_BlanksLeft) if j == i_MaxBlanks]
        if len(l_MaxBlanks) > 1:#somehow there is STILL a tie
            i_BestResultindex = l_BestResults[random.randrange(0,len(l_MaxBlanks))]
        else:
            i_BestResultindex = l_BestResults[l_MaxBlanks[0]]
    else:
        i_BestResultindex = l_FilterCounts.index(i_BestResultScore)
    
    s_BestResultFilter = l_Filters[i_BestResultindex]

    return s_BestResultFilter





#program
load_dict("Wordlists/words.txt",l_WordList)

input_wordlength = input("Desired word length: ")
try:
    i_WordLen = int(input_wordlength)
    l_tempWordList = optimize_wordlist(l_WordList,i_WordLen,l_BannedChars)
    if len(l_tempWordList) == 0:
        print("I don't know any words with that length.")
        raise ValueError
    l_WordList = l_tempWordList #if it gets here, there's a valid list.
except: #they didn't enter a proper number
    print("Using any length word.")
    i_minimumWordCount = math.floor(len(l_WordList)/100) #at least 1% of the words have to be that length (would be about 1000 words from the unix wordlist)
    while(True): #keep trying until random gives us a usable wordlength
        i_WordLen = random.randrange(2,len(max(l_WordList,key=len)),1) #random number between 2 and the longest length word in the list
        l_tempWords = optimize_wordlist(l_WordList,i_WordLen,l_BannedChars)
        if len(l_tempWords) >= i_minimumWordCount: 
            l_WordList = l_tempWords
            del l_tempWords
            break
s_GivenInfo = "."*i_WordLen

#main game loop
while(len(l_WrongGuesses) < i_MaxErrorCount ):
    display_hangman(s_GivenInfo, l_WrongGuesses, i_MaxErrorCount)
    c_GuessInput = input("Pick a letter: ").strip().lower()
    for c in c_GuessInput:
        if c not in l_WrongGuesses and c not in s_GivenInfo: #make sure I'm not counting previous errors or correct answers against them.
            #startTime = time.perf_counter()
            s_bestPlay = getBestPlay(l_WordList, s_GivenInfo, c)
            #print("getBestPlay took ",time.perf_counter()-startTime,", and responded with",s_bestPlay)
            if s_bestPlay == s_GivenInfo: #the best play was to not let them have that letter
                l_WrongGuesses.append(c)
            else:
                s_GivenInfo = s_bestPlay
        l_WordList = filter_wordlist(l_WordList,s_GivenInfo,l_WrongGuesses) #make sure to update the wordlist after every letter
        try:
            s_GivenInfo.index(".") #will throw an error if there's no blanks left. If there are, we haven't lost yet! Even if the wordlist is down to one word, if they don't know it: tough!
        except:
            print("Yeah, alright, the word was "+s_GivenInfo+".")
            quit()


#the loop was exited because they ran out of guesses.
display_hangman(s_GivenInfo, l_WrongGuesses, i_MaxErrorCount) #show the death piece       
print("The word was "+l_WordList[0]+", obviously!")