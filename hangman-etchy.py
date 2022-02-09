"""Hangman except the computer hates you"""
#Basic premise: Hangman, except the computer is trying to get you to lose, so it constantly gives you the least knowledge possible by picking a result that fits the most number of words.
#example: wordlist of "what, when, then", if a W is guessed, it would be filled in, as there are more Ws, if e were guessed, then it would be filled, as more words have that.
#The standard hangman game has about 6 wrong guesses allowed. The computer could easily win in this space, so the wrong guesses would have to be larger or infinite
#an element of randomness should play a part in this, or known strategies break the fun. maybe a variance of 10% on what the "most" common fit would be. This would mean sometimes the computer gives itself a smaller space to work in, but stops known cornering strats

import io
import math
import random
import re
import timeit


#global variables
l_BannedChars = ["'","Å","â","ä","á","å","ç","é","è","ê","í","ñ","ó","ô","ö","ü","û","-"," "] #sometimes the wordlist comes with a whole lot of non-english characters, or characters that make hangman unfun. 
i_WordLen = 10
l_WordList = [] #will hold all the words that we can still pick from
s_GivenInfo = "" #holds a string representation of the information players have for display and filtering.
l_WrongGuesses = []
i_MaxErrorCount = 13

def load_dict(file,StorageList):
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

def generate_FilterPermutations(s_Pattern, c_PermCharacter, i_startIndex = 0) -> list:
    i_BlankSpots = 0
    for i in range(i_startIndex, len(s_Pattern)):
        if s_Pattern[i] == ".":
            i_BlankSpots += 1
    #i_BlankSpots = s_Pattern.count(".") #can't be used because we only care about results AFTER where we start
    l_Permutations = []
    l_Permutations.append(s_Pattern)
    if i_BlankSpots < 1:
        return l_Permutations
    l_BlankSpotIndices = []
    i_currIndex = i_startIndex
    for BlankNum in range(1,i_BlankSpots+1):
        i_foundIndex = s_Pattern.index(".",i_currIndex)
        l_BlankSpotIndices.append(i_foundIndex)
        i_currIndex = i_foundIndex+1
    #indices of blank spots found
    for BlankNum in range(0,i_BlankSpots):
        s_NewPattern = str_Replace(s_Pattern, l_BlankSpotIndices[BlankNum], c_PermCharacter)
        #s_NewPattern[l_BlankSpotIndices[BlankNum]] = c_PermCharacter #can't do this in python
        #l_Permutations.append(s_NewPattern) #unneeded since the function spits back the input if there's nothing to do
        l_Permutations.extend(generate_FilterPermutations(s_NewPattern, c_PermCharacter, l_BlankSpotIndices[BlankNum]+1)) #append makes a list in a list, extend adds the items. Also: recursion is fun~
    l_Permutations = list(dict.fromkeys(l_Permutations)) #dedupe, just in case.
    #if i_startIndex == 0:
    #    print(str(len(l_Permutations))+" combinations found.")
    return l_Permutations

def str_Replace(s_Original, i_index, c_Replacement) -> str:
    return s_Original[:i_index]+c_Replacement+s_Original[i_index+1:]

def RemovedFromList(l_filteredList, l_UnfilteredList) -> list:
    #l_removedList = []
    #for word in l_UnfilteredList:
    #    if word not in l_filteredList:
    #        l_removedList.append(word)
    l_removedList = list(set(l_UnfilteredList) - set(l_filteredList)) #more than double the speed
    return l_removedList


def display_hangman(s_knownInfo,l_wrongGuesses, i_MaxAllowedErrors):
    f_errorPercent = len(l_wrongGuesses)/i_MaxAllowedErrors
    drawGallows(f_errorPercent)

    s_knownInfo = s_knownInfo.replace(".","_ ")
    print(s_knownInfo)

    s_wrongGuesses = str(l_wrongGuesses)
    s_wrongGuesses = s_wrongGuesses[1:len(s_wrongGuesses)-1] #use the default list to string conversion and cut off the []
    if  s_wrongGuesses != "":
        print("Wrong guesses: "+s_wrongGuesses)

def drawGallows(f_PercentComplete):
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
    l_Perms = generate_FilterPermutations(s_CurrentLayout,c_CurrentGuess)
    l_FilterResults = [0]*len(l_Perms)
    s_NotCurrentGuessRegex = "[^"+c_CurrentGuess+"]"

    l_wordsWithoutGuess = filter_wordlist(l_wordlist,"",[c_CurrentGuess])
    l_RemainingWords = RemovedFromList(l_wordsWithoutGuess,l_wordlist) #get all the words with at least 1 of the letters in it
    l_FilterResults[0] = len(l_wordsWithoutGuess)
    #l_RemainingWords = l_wordlist
    for i in range(1,len(l_Perms)):
        s_tempRegex = l_Perms[i].replace(".",s_NotCurrentGuessRegex)
        l_filteredWordlist = filter_wordlist(l_RemainingWords, s_tempRegex)
        if len(l_filteredWordlist) != 0: #only run it if it's worth my time
            l_RemainingWords = RemovedFromList(l_filteredWordlist,l_RemainingWords) #I hope that by removing hits, the process will get faster and faster.
        l_FilterResults[i] = len(l_filteredWordlist) #get the length of wordlists to inform our descision
    

    #TODO: maybe add some randomness, but it seems like the best option is WAY ahead of others
    #TODO: currently when down to the final results, the bot will sometimes give up the win. make sure that the best result has at least one blank at all costs.
    i_BestResultindex = l_FilterResults.index(max(l_FilterResults))
    s_BestResultFilter = l_Perms[i_BestResultindex]

    return s_BestResultFilter



#program
load_dict("Wordlists/words.txt",l_WordList)

input_wordlength = input("Desired word length: ")
try:
    i_WordLen = int(input_wordlength)
    l_WordList = optimize_wordlist(l_WordList,i_WordLen,l_BannedChars)
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

g=timeit.Timer(lambda: generate_FilterPermutations(s_GivenInfo,"a"))
#print("generate filter: "+str(g.timeit(1)))

a=timeit.Timer(lambda: filter_wordlist(l_WordList, "aaaaaaa[^a][^a][^a][^a][^a][^a][^a][^a]",["b"]))
print("Apply filter: "+str(a.timeit(33000)))

rfl=timeit.Timer(lambda: RemovedFromList(l_WordList,l_WordList))
#print("Remove from list: "+str(rfl.timeit(100)))

bp = timeit.Timer(lambda: getBestPlay(l_WordList, s_GivenInfo, "a"))
#print("Get Best play: "+str(bp.timeit(1)))
quit()

#display_hangman(s_GivenInfo, l_WrongGuesses, i_MaxErrorCount) #give them the number of letters before forcing them to guess. It's only polite.
#main game loop
while(len(l_WrongGuesses) < i_MaxErrorCount ):
    display_hangman(s_GivenInfo, l_WrongGuesses, i_MaxErrorCount)
    c_GuessInput = input("Pick a letter: ").strip().lower()
    for c in c_GuessInput:
        if c not in l_WrongGuesses and c not in s_GivenInfo: #make sure I'm not counting previous errors or correct answers against them.
            s_bestPlay = getBestPlay(l_WordList, s_GivenInfo, c)
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