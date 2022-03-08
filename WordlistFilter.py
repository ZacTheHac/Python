
from importlib.machinery import FileFinder
import io


bannedChars = ["'","Å","â","ä","á","å","ç","é","è","ê","í","ñ","ó","ô","ö","ü","û","-"," "]
equivalentCharacters = [["a","Å","â","ä","á","å"],["c","s","ç"],["e","é","è","ê"],["i","í"],["n","ñ"],["o","ó","ô","ö"],["u","ü","û"],[" ","-","'"]]
wordlist = []
wordsToRemove = []
s_WordFile = "Wordlists\handfiltered_words.txt"

def load_dict(file,StorageList):
    fileDict=io.open(file, mode="r", encoding="utf-8")
    dictionary = fileDict.readlines()
    fileDict.close()
    #dictsize = int(len(dictionary))
    #print(file + " dictionary Loaded.")
    #print("("+str(dictsize)+" words)")
    #print("First line: \""+str(dictionary[0]).strip()+"\"")
    #print("final line: \""+str(dictionary[dictsize-1])+"\"")
    #add it to the list
    StorageList += dictionary

def cleanList(l_Wordlist) ->str:
    l_newList = []
    for word in l_Wordlist:
        l_newList.append(word.strip())
    return l_newList

def FindBannedChars(l_Wordlist,l_BannedChars) -> list:
    l_Bans = []
    for word in l_Wordlist:
        if any(bannedCharacter in l_BannedChars for bannedCharacter in word):
            choice = bool(input("Ban \""+word+"\"? "))
            if choice:
                l_Bans.append(word)
        if len(l_Bans)>50:
            break
    return l_Bans

def WriteWordlist(l_Wordlist, s_File):
    global wordsToRemove

    fileDict=io.open(s_File, mode="w", encoding="utf-8")
    for word in l_Wordlist:
        if word not in wordsToRemove:
            fileDict.write(word+"\n")
    fileDict.truncate()
    fileDict.close()






#begin program
load_dict(s_WordFile,wordlist)
wordlist = cleanList(wordlist)
print("Word list loaded.")
print("("+str(len(wordlist))+" words)")
print("First line: \""+str(wordlist[0])+"\"")
print("final line: \""+str(wordlist[len(wordlist)-1])+"\"")
#wordsToRemove += FindBannedChars(wordlist,bannedChars)
WriteWordlist(wordlist, s_WordFile)