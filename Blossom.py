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

    #load a small list of known SpellingBee words
    load_dict("Wordlists/SpellingBee.txt",listWords)

    #load the unabridged MW dict
    #load_dict("Wordlists/webster_unabridged.txt",listWords)

    #load the unabridged MW dict but with blossom rejected words removed
    #load_dict("Wordlists/webster_unabridged_blossomfilter.txt",listWords)

    #load the unabridged MW dict but with nouns removed and only words 4 letters or longer
    #load_dict("Wordlists/MW_NoNouns_4LetterPlus.txt",listWords)


    #Open the OH LAWD webster dict
    #load_dict("Wordlists/webster-dictionary.txt",listWords)

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

def GroupByBestBonusLetter(listWordList:list[str],listBonusableLetters:list[str],NBDDistance:int=8) -> list[list[list[str,int]]]:
    """output format is [bonus letter index][which item in the list][0=the word, 1=the score it gives]"""
    listBestWordsByLetter = [[] for i in range(len(listBonusableLetters))]
    intScoreNBDDistance = NBDDistance
    #intScoreNBDDistance = 8 #this number is a delicate balancing act. examples of tests:
    #Blossom O-NLKSER (july 12, 2023): without grouping: 432, with grouping: NBD=2:433(+1), NBD=5:436(+4), 6:444, 7:444, NBD=9:444(+12), NBD=10:444(+12), NBD=11:439(+7)
        #sweet spot may lie between 5 and 11, as the linear relationship didn't follow to 11, and 10 more points is a significant amount to deviate by. May be an issue with the second half of the game, that bonus letter may NEVER show up again
        #so high value words are lost because they were kept for something not meant to be
        #large NBD values can allow them to still show up, but that also means that they might be used up before they can be used to their full potential.
        #or we could simply be seeing diminishing returns, but 11 still resulted in the highest score, so it may be a perfectly fine value
        #updated with a NBD of 10 results in the highest score yet, meaning we had passed to apex with 11.
    for strWord in listWordList:
        listScoresByBonusLetter = []
        for i in range(len(listBonusableLetters)): 
            charLetter = listBonusableLetters[i]
            listScoresByBonusLetter.append(PointsForWord(strWord,listBonusableLetters,charLetter)) #technically I should feed in a list of all letters, including the center, but the function SHOULD behave identically, as all words will have the center letter, and it just wants the letter list to find a pangram
        #have a list of all the scores each word can give. Find out if one letter is much larger than the others. If it is, only add the word to that/those list(s). if not, add it to all.
        intMaxScore = max(listScoresByBonusLetter)
        intMinScore = min(listScoresByBonusLetter)
        if (intMaxScore-intMinScore) > intScoreNBDDistance:
            #have to find out the best words.
            for i in range(len(listBonusableLetters)):
                if(intMaxScore - listScoresByBonusLetter[i])<intScoreNBDDistance:
                    listBestWordsByLetter[i].append([strWord,listScoresByBonusLetter[i]])
        else:
            #score is close enough. Just put it in all of them.
            for i in range(len(listBonusableLetters)):
                listBestWordsByLetter[i].append([strWord,listScoresByBonusLetter[i]])
    #all the words are in apropriate lists. Now to just sort the lists.
    for i in range(len(listBonusableLetters)):
        listBestWordsByLetter[i].sort(key=lambda row: (row[1]),reverse=True)
    return listBestWordsByLetter #it's very important to ACTUALLY RETURN THE THING WE MADE.

def KeepBestBonusLetter(listWordList:list[str],listBonusableLetters:list[str]) -> list[list[list[str,int]]]:
    #new idea: Keep the best possible 2 words for each letter, as the "bonus letter" is just going through the letter choices. (for example, if the puzzle is puzzle ID I-AENPRT, the bonus letters will be A,E,N,P,R,T,A,E,N,P,R and T, in that order)
    #the rest can be given to anyone because of errors in the wordlist or whatever.
    #if there is a tie between two words, put it in both, but let each one reserve an extra?
    #For grouping turned on, the function never sorts, so it's important that it is given back in the final sorted order.
    intDefaultReserveAmount = 2
    listBestWordsByLetter = [[] for i in range(len(listBonusableLetters))]
    listNumWordsReservedByLetter = [intDefaultReserveAmount] * len(listBonusableLetters)
    listReservedWords = [[] for i in range(len(listBonusableLetters))]
    intScoreNBDDistance = 8 #this number is a delicate balancing act. examples of tests:
    #Blossom O-NLKSER (july 12, 2023): without grouping: 432, with grouping: NBD=2:433(+1), NBD=5:436(+4), 6:444, 7:444, NBD=9:444(+12), NBD=10:444(+12), NBD=11:439(+7)
        #sweet spot may lie between 5 and 11, as the linear relationship didn't follow to 11, and 10 more points is a significant amount to deviate by. May be an issue with the second half of the game, that bonus letter may NEVER show up again
        #so high value words are lost because they were kept for something not meant to be
        #large NBD values can allow them to still show up, but that also means that they might be used up before they can be used to their full potential.
        #or we could simply be seeing diminishing returns, but 11 still resulted in the highest score, so it may be a perfectly fine value
        #updated with a NBD of 10 results in the highest score yet, meaning we had passed to apex with 11.
    for strWord in listWordList:
        listScoresByBonusLetter = []
        for i in range(len(listBonusableLetters)): 
            charLetter = listBonusableLetters[i]
            listScoresByBonusLetter.append(PointsForWord(strWord,listBonusableLetters,charLetter)) #technically I should feed in a list of all letters, including the center, but the function SHOULD behave identically, as all words will have the center letter, and it just wants the letter list to find a pangram
        #have a list of all the scores each word can give. Find out if one letter is much larger than the others. If it is, only add the word to that/those list(s). if not, add it to all.
        intMaxScore = max(listScoresByBonusLetter)
        intMinScore = min(listScoresByBonusLetter)
        if (intMaxScore-intMinScore) > intScoreNBDDistance:
            #have to find out the best words.
            for i in range(len(listBonusableLetters)):
                if(intMaxScore - listScoresByBonusLetter[i])<intScoreNBDDistance:
                    listBestWordsByLetter[i].append([strWord,listScoresByBonusLetter[i]])
        else:
            #score is close enough. Just put it in all of them.
            for i in range(len(listBonusableLetters)):
                listBestWordsByLetter[i].append([strWord,listScoresByBonusLetter[i]])
    #all the words are in apropriate lists. Now to just sort the lists.
    for i in range(len(listBonusableLetters)):
        listBestWordsByLetter[i].sort(key=lambda row: (row[1]),reverse=True)
    return listBestWordsByLetter #it's very important to ACTUALLY RETURN THE THING WE MADE.

def GamePlan(listWordList:list[str],listBonusableLetters:list[str]):
    """We know that no matter what, the game will select each letter to be the "bonus letter" twice.\n
    Therefore, we can plan out our game such that we get the most optimal plays.\n
    To do this, we find the 2 best possible words for any given letter, but verify that it's not worth MORE points with a different bonus letter."""
    #store a list of all unused words, one by one chew through them to find ~a top 10 list for a letter,
    #then run through THAT list, calculating the point value for a given bonus letter
    #if another letter has a higher score, give it to them & delete from our list
    #but what if the value is better for another letter, but that letter has WAY better words to choose from anyways?

    #perhaps the solution is to generate all the letter's top point values. The words they want.
    #then we go through those lists to find conflicts and resolve them.
    #reuse the current "GroupByBestBonusLetter" to get the lists and then just sift through those.

    #is this worth it? Who knows! July 4th: N-DEIPRT: 513 pts without, 514 points with.
    #July 3: N-ACEIMN 425 vs 

    intFallbackDeleteCount = 0 #here to track how often I'm deleting by checking third value. Might be something to fix later.
    listGroupedList = GroupByBestBonusLetter(listWordList,listBonusableLetters,12) #format is [bonus letter][which item in the list][0=the word, 1=the score it gives]
    dirtybit = 1
    while(dirtybit):
        dirtybit = 0
        for i in range(len(listBonusableLetters)):
            #check their top 2 scores to see if they're in another letter's list. continue until no more conflicts with the top 2 scores.
            topWord = listGroupedList[i][0][0]
            secondWord = listGroupedList[i][1][0]
            for BonLetIndex in range(len(listBonusableLetters)):
                if BonLetIndex == i:
                    continue
                for WordIndex in range(2):
                    if listGroupedList[BonLetIndex][WordIndex][0] == topWord: #gotta duke it out for top spot
                        if listGroupedList[i][0][1] > listGroupedList[BonLetIndex][WordIndex][1]: #the original word is better, remove the word from the second letter checked
                            del(listGroupedList[BonLetIndex][WordIndex]) #delete the whole row
                            dirtybit = 1
                            break
                        elif listGroupedList[i][0][1] < listGroupedList[BonLetIndex][WordIndex][1]: #the other word is better, remove this word
                            del(listGroupedList[i][0]) #delete the row
                            dirtybit = 1
                            break
                        else: #the scores are even. check if one has a particularly enticing third option?
                            if listGroupedList[i][2][1] > listGroupedList[BonLetIndex][2][1]:#This letter has less to lose
                                del(listGroupedList[i][0])
                                dirtybit = 1
                                break
                            else:#either it doesn't matter, or the other has less to lose.
                                #TODO: in a list where there's a lot of ties, one may, say, have 8 30pt options to choose from, while the other may only have 1 before they drop to 28.
                                #if this hits more often than I thought, it may be worthwhile to keep looking further until we get a tie breaker.?
                                intFallbackDeleteCount += 1
                                del(listGroupedList[BonLetIndex][WordIndex])
                                dirtybit = 1
                                break
                    elif listGroupedList[BonLetIndex][WordIndex][0] == secondWord: #gotta duke it out for second place
                        if listGroupedList[i][1][1] > listGroupedList[BonLetIndex][WordIndex][1]: #the original word is better, remove the word from the second letter checked
                            del(listGroupedList[BonLetIndex][WordIndex]) #delete the whole row
                            dirtybit = 1
                            break
                        elif listGroupedList[i][1][1] < listGroupedList[BonLetIndex][WordIndex][1]: #the other word is better, remove this word
                            del(listGroupedList[i][1]) #delete the row
                            dirtybit = 1
                            break
                        else: #the scores are even. check if one has a particularly enticing third option?
                            if listGroupedList[i][2][1] > listGroupedList[BonLetIndex][2][1]: #This letter has less to lose
                                del(listGroupedList[i][1])
                                dirtybit = 1
                                break
                            else: #either it doesn't matter, or the other has less to lose.
                                #TODO: in a list where there's a lot of ties, one may, say, have 8 30pt options to choose from, while the other may only have 1 before they drop to 28.
                                #if this hits more often than I thought, it may be worthwhile to keep looking further until we get a tie breaker.?
                                intFallbackDeleteCount += 1
                                del(listGroupedList[BonLetIndex][WordIndex])
                                dirtybit = 1
                                break
                if dirtybit:
                    break
            #if it got to here, then it's either done, or something broke out, and we need to reset.
            if dirtybit:
                break


    
    #by the time we get here, every list has its top 2 favorite words picked out and unique. Time to cut down the list and send it away!
    print("Fallback delete count: ",intFallbackDeleteCount)
    listSlimmedList = []
    for i in range(len(listBonusableLetters)):
        listSlimmedList.append(listGroupedList[i][0:2])
    return listSlimmedList

#main code block
def main():
    strCenterLetter = input("What is the center (required) letter?: ").lower()
    strOtherLetters = input("What are the rest of the letters?: ").lower()
    b_BonusLetters = bool(input("Are there Bonus letters (Like in Blossom)? "))
    if b_BonusLetters:
        boolGamePlan = bool(input("Pick the best play automatically? "))
        if boolGamePlan:
            boolSort = False
            boolAutoDelete = False
        else:
            boolSort = bool(input("Automatically separate words into their top value bonus letters? "))
            boolAutoDelete = bool(input("Automatically delete top values once shown? "))
    else:
        boolGamePlan = False
        boolSort = False
        boolAutoDelete = bool(input("Automatically delete top values once shown? "))

    listBonusableLetters = [*strOtherLetters]
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
    print("\n\n") #newline after it.

    #calculate base points (without knowing bonus letter)
    #delete the lowest scoring like half of the wordlist (at least all the 0 point ones) - turns out just assembling the possible words reduces the list to <500 words anyways
    #sort by score
    #now when given a bonus letter we can create a new list of values, starting with the first 100 or so top scoring words.

    listGroupedList = [] #have to make sure it doesn't go out of scope too soon.
    if boolSort:
        listGroupedList = GroupByBestBonusLetter(listWords,listBonusableLetters)
    if boolGamePlan:
        listSlimmedList = GamePlan(listWords,listBonusableLetters)
    

    while True: #just run forever. The user can kill it when they're done.
        if boolGamePlan:
            for i in range(len(listBonusableLetters)):
                print("Bonus letter: \"",listBonusableLetters[i],"\":")
                for j in range(len(listSlimmedList[i])):
                    print("    ",listSlimmedList[i][j][0]," for ",listSlimmedList[i][j][1]," points.")
            break
        if b_BonusLetters:
            strBonusLetter = input("What is the current bonus letter? ").lower()
            if strBonusLetter == "list":
                print(listWords)
                continue
        #calculate all the values of the words now, sort by the top scores and show the top 20
        listWordValues = []
        if boolSort:
            try:
                intIndexOfLetter = listBonusableLetters.index(strBonusLetter)
                #print("That is number",intIndexOfLetter+1)
                listWordValues = listGroupedList[intIndexOfLetter]
            except:
                print("I don't see that letter in the initial letters you gave me.")
                continue
        else:
            if b_BonusLetters:
                listWordValues = GetAndSortByScore(listWords,listAllowedCharacters,strBonusLetter)
            else:
                listWordValues = GetAndSortByScore(listWords,listAllowedCharacters,"")
        for i in range(min(10,len(listWordValues))):
            print(listWordValues[i][0],"- worth ",listWordValues[i][1],"points")
        
        if boolAutoDelete:
            #remove the top word from the list.
            strTopWord = listWordValues[0][0]
            if boolSort:
                #find in all lists and eliminate it.
                for i in range(len(listBonusableLetters)):
                    intListLength = len(listGroupedList[i])
                    for j in range(intListLength):
                        if listGroupedList[i][j][0] == strTopWord:
                            del(listGroupedList[i][j]) #delete the whole row
                            #intListLength-=1 #we made the list shorter, so we need to compensate for that.
                            break #we found the word in this list, it shouldn't have any dupes!
            else:
                listWords.remove(strTopWord)
        if len(listWords)<=0 or (boolSort and len(listGroupedList)<=0):
            print("And that's all I know!")
            break

#my top score ever: July 17, 2023:O-NSCTEI: 666 pts 

if __name__ == "__main__":
    main()