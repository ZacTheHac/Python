import io

#global variables
listWords = []

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

def build_dictionary(strRequiredLetter:str,listAllowedCharacters:list[str]):
    global listWords

    #load the list of known Blossom words
    load_dict("Wordlists/Blossom.txt",listWords)

    #Open the OH LAWD webster dict
    load_dict("Wordlists/webster-dictionary.txt",listWords)

    #load combined file that eliminated 7,506,911 duplicates (~7MB), 571,985 words (Now expanded with YAWL to 578,747)
    #load_dict("Wordlists/MEGADICT.txt",legalWords)

    listWords = optimize_wordlist(listWords,strRequiredLetter,listAllowedCharacters)
    #list optomized

    print("Word list assembled. ("+str(len(listWords))+" words)")
    print("First word: \""+str(listWords[0])+"\"")
    print("Final word: \""+str(listWords[len(listWords)-1])+"\"")

def optimize_wordlist(wordList:list[str],strRequiredLetter:str,listAllowedCharacters:list[str]) -> list:
    """
    Returns all words in \"wordList\" that are at least 4 characters long, contain \"strRequiredLetter\" and only contain characters from \"listAllowedCharacters\"\n
    The new list is deduplicated and sorted alphabetically.
    """

    newWords = []
    for word in wordList:
        word = word.strip().lower()
        if(len(word) >= 4):
            if all(chrNeededCharacter in listAllowedCharacters for chrNeededCharacter in word):
                if word.count(strRequiredLetter) > 0:
                    newWords.append(word)
    newWords = list(dict.fromkeys(newWords)) #dedupe the list (because evidently it needs that)
    newWords.sort() #why not have it sorted, too?
    return newWords

def PointsForWord(strWord:str,listAllLetters:list[str],charBonusLetter:str) -> int:
    intPoints = 0
    #word length points
    intWordLen = len(strWord)
    if(intWordLen < 4):
        return 0 #Blossom words MUST be 4 characters or longer
    elif(intWordLen == 4):
        intPoints += 2
    elif(intWordLen == 5):
        intPoints += 4
    elif(intWordLen == 6):
        intPoints += 6
    elif(intWordLen >= 7):
        intPoints += (12+ ((intWordLen - 7)*3)) #7 letters is 12 points, and each additional letter is +3 points
    else:
        print("Something went wrong calculating value of word",strWord,"with length",intWordLen)
        return 0
    #Calculate the bonus letter bonus
    #count the number of times the letter appears in the word, multiply by 5
    if len(charBonusLetter) == 1: #if it's blank or more than one letter, I'm not counting bonus points
        intBonusLetterCount = strWord.count(charBonusLetter)
        intPoints += (intBonusLetterCount * 5)
    #check if it's a pangram worth a bonus 7 points (meaning a minimum score of 24pts. 7 letters (12pts), 1 bonus (5pts), plus pangram bonus (7pts))
    boolHasAllLetters = True #assume true until proven false
    for charLetter in listAllLetters:
        if strWord.count(charLetter) == 0:
            boolHasAllLetters = False
            break
    if boolHasAllLetters:
        intPoints += 7
    #return the point value
    return intPoints

def GetPangrams(listWordList:list[str],listAllLetters:list[str]) -> list[str]:
    listPangrams = []
    for strWord in listWordList:
        boolHasAllLetters = True #assume true until proven false
        for charLetter in listAllLetters:
            if strWord.count(charLetter) == 0:
                boolHasAllLetters = False
                break
        if boolHasAllLetters:
            listPangrams.append(strWord)

    return listPangrams

def GetAndSortByScore(listWordList:list[str],listAllLetters:list[str],charBonusLetter:str) -> list[list[str,int]]:
    listWordAndScore = []
    for strWord in listWordList:
        intScore = PointsForWord(strWord,listAllLetters,charBonusLetter)
        listSubWordPlusScore = [strWord,intScore]
        listWordAndScore.append(listSubWordPlusScore)
    listWordAndScore.sort(key=lambda row: (row[1]),reverse=True) #sort by the score (highest first), and in a tie it'll default to the list order (which is usually alphabetical.)
    #key=lambda row: (row[1] , row[0]) for reverse sort alphabetically, too.
    return listWordAndScore


#main code block
def main():
    strCenterLetter = input("What is the center (required) letter?: ").lower()
    strOtherLetters = input("What are the rest of the letters?: ").lower()
    listAllowedCharacters = [*strOtherLetters]
    listAllowedCharacters.append(strCenterLetter)

    build_dictionary(strCenterLetter,listAllowedCharacters)

    listPangrams = GetPangrams(listWords,listAllowedCharacters)
    listPangramValues = GetAndSortByScore(listPangrams,listAllowedCharacters,"") #gets the value of the word ignoring letter bonuses
    #print(listPangramValues)
    print()
    print("** Found the following pangrams for today:")
    for listPangramAndValue in listPangramValues:
        print(listPangramAndValue[0],"- worth at least",listPangramAndValue[1]+5,"points") #boosts the points by 5 since we know it'll hit the bonus letter at least once

    #calculate base points (without knowing bonus letter)
    #delete the lowest scoring like half of the wordlist (at least all the 0 point ones) - turns out just assembling the possible words reduces the list to <500 words anyways
    #sort by score
    #now when given a bonus letter we can create a new list of values, starting with the first 100 or so top scoring words.

    while True: #just run forever. The user can kill it when they're done.
        print("\n\n")
        strBonusLetter = input("What is the current bonus letter? ")
        #calculate all the values of the words now, sort by the top scores and show the top 20
        listWordValues = GetAndSortByScore(listWords,listAllowedCharacters,strBonusLetter)
        for i in range(min(20,len(listWordValues))):
            print(listWordValues[i][0],"- worth ",listWordValues[i][1],"points")

if __name__ == "__main__":
    main()