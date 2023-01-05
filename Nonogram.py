from itertools import combinations

global c_Fill
c_Fill = "██"
global c_Empty
c_Empty = "  "
global c_Unknown
c_Unknown = "░░"
global i_BoardWidth
global i_BoardHeight
global l_HorizontalPatterns
global l_VerticalPatterns
global l_KnownSpots
global l_HorizontalNumbers
global l_VerticalNumbers



def minLengthOfRow(l_numbers:list[int])->int:
	i_minLength = 0
	#offset: 0 for 0 to 1, 1 for 2, 2 for 3, etc.
	iOffset = max(len(l_numbers)-1,0)
	i_minLength += iOffset
	i_minLength += sum(l_numbers)
	#for i in l_numbers:
	#	i_minLength += i
	return i_minLength

def isRowSolved(l_Row:list[bool])->bool:
	for b in l_Row:
		if b is None:
			return False
	return True

def isPuzzleSolved(l_KnownSpots:list[list[bool]])->bool:
	for row in l_KnownSpots:
		if not isRowSolved(row):
			return False
	return True

def printBoard(l_KnownSpots:list[list[bool]], noLines:bool=False)->None:
	i_Width = len(l_KnownSpots)
	i_Height = len(l_KnownSpots[0])
	for i in range(i_Height):
		s_Row = ""
		for j in range(i_Width):
			if l_KnownSpots[j][i] is True:
				s_Row += c_Fill
			elif l_KnownSpots[j][i] is False:
				s_Row += c_Empty
			else:
				s_Row += c_Unknown
			if not noLines:
				if j < i_Width-1:
					s_Row += "|"
		print(s_Row)
	return

def getHorizontalRow(l_KnownSpots:list[list[bool]],i_RowIndex:int) -> list[bool]:
	l_Row = []
	i_width = len(l_KnownSpots)
	for i in range(i_width):
		l_Row.append(l_KnownSpots[i][i_RowIndex])

	return l_Row

def DoesRowFitKnown(l_KnownRow:list[bool],l_ProposedRow:list[bool])->bool:
	for i in range(len(l_KnownRow)):
		if (l_ProposedRow[i] != l_KnownRow[i]) and (l_KnownRow[i] is not None):
			return False
	return True

def generatePossibleStates(i_BoardSize:int,l_KnownRow:list[bool],l_numbers:list[int])->list[list[bool]]:
	if isRowSolved(l_KnownRow):
		return [l_KnownRow]
	else:
		#actually have to generate the possible states
		#can treat each block of filled blocks as a single unit
		#only really need to figure out the possible ways to space them out.
		## 1,1,2 on a 9 length
		## 3 groups
		## 4 filled
		## 5 empty spaces
		## 3 extra empty
		## range(groups+extra empty) = range(3+3) = [0,1,2,3,4,5]
		## comb(range,groups) = comb([0,1,2,3,4,5],3) = 20 solutions.
		## 
		## 3,2,6 on a 15
		## 3 groups
		## 11 filled
		## 4 empty
		## 2 extra
		## range = [0,1,2,3,4]
		## comb([0,1,2,3,4],3) = 10 solutions
		## (0,1,2) = X_X_X__
		## (0,1,3) = X_X__X_
		## (0,1,4) = X_X___X
		## ...
		## (1,2,3) = _X_X_X_
		## ...
		## (2,3,4) = __X_X_X
		i_Spaces = i_BoardSize - sum(l_numbers) #number of empty squares
		i_RequiredEmpty = max(0,len(l_numbers)-1)
		i_ExtraSpaces = i_Spaces-i_RequiredEmpty
		i_Groups = len(l_numbers)
		l_indexOfStart = combinations(range(i_Groups+i_ExtraSpaces),i_Groups) #will have the index of the start of groups, offset by required spaces.
		l_States = []
		for combo in l_indexOfStart:
			i_GroupIndex = 0
			i_indexOn = 0
			l_ProposedState = []
			for indexOffset in combo:
				fillWidth = indexOffset-i_indexOn
				for i in range(fillWidth):
					l_ProposedState.append(False)
				i_indexOn += fillWidth
				for i in range(l_numbers[i_GroupIndex]):
					l_ProposedState.append(True)
				l_ProposedState.append(False)
				i_indexOn += 1 #group includes one space after
				i_GroupIndex += 1
			#fill up the end with Falses or trim the extra false off the end
			if len(l_ProposedState) < i_BoardSize:
				i_FillWidth = i_BoardSize - len(l_ProposedState)
				for i in range(i_FillWidth):
					l_ProposedState.append(False)
			elif i_BoardSize < len(l_ProposedState):
				l_ProposedState = l_ProposedState[0:i_BoardSize]
			if DoesRowFitKnown(l_KnownRow,l_ProposedState):
				l_States.append(l_ProposedState)
		
		return l_States

def findKnownSpots(l_HorizontalPatterns:list[list[bool]],l_VerticalPatterns:list[list[bool]],l_KnownSpots:list[list[bool]])->bool:
	dirtyReturnBit = False
	for row in range(len(l_HorizontalPatterns)): #row is the specific row we're checking right now
		for i in range(len(l_HorizontalPatterns[row][0])): #i is the spot in the row we're checking
			rightAnswer = l_HorizontalPatterns[row][0][i]
			DirtyBit = False
			for pattern in l_HorizontalPatterns[row]: #pattern is the potential pattern we're checking currently.
				if pattern[i] != rightAnswer:
					DirtyBit = True
					break
			if not DirtyBit:
				l_KnownSpots[i][row] = rightAnswer
				dirtyReturnBit = True

	for collumn in range(len(l_VerticalPatterns)): #collumn is the specific collumn we're checking right now
		for i in range(len(l_VerticalPatterns[collumn][0])): #i is the spot in the collumn we're checking
			rightAnswer = l_VerticalPatterns[collumn][0][i]
			DirtyBit = False
			for pattern in l_VerticalPatterns[collumn]: #pattern is the potential pattern we're checking currently.
				if pattern[i] != rightAnswer:
					DirtyBit = True
					break
			if not DirtyBit:
				l_KnownSpots[collumn][i] = rightAnswer
				dirtyReturnBit = True
	return dirtyReturnBit

def reducePatternList(l_HorizontalPatterns:list[list[bool]],l_VerticalPatterns:list[list[bool]],l_KnownSpots:list[list[bool]])->bool:
	dirtyReturnBit = False
	for row in range(len(l_HorizontalPatterns)):
		i_patternCount = len(l_HorizontalPatterns[row])
		pattern = 0
		while pattern < i_patternCount:
			if not DoesRowFitKnown(getHorizontalRow(l_KnownSpots,row),l_HorizontalPatterns[row][pattern]):
				del l_HorizontalPatterns[row][pattern]
				i_patternCount -= 1
				pattern -= 1
				dirtyReturnBit = True
			pattern += 1
	for collumn in range(len(l_VerticalPatterns)):
		i_patternCount = len(l_VerticalPatterns[collumn])
		pattern = 0
		while pattern < i_patternCount:
			if not DoesRowFitKnown(l_KnownSpots[collumn],l_VerticalPatterns[collumn][pattern]):
				del l_VerticalPatterns[collumn][pattern]
				i_patternCount -= 1
				pattern -= 1
				dirtyReturnBit = True
			pattern += 1
	return dirtyReturnBit



#program
if __name__ == '__main__':
	i_BoardWidth = int(input("Width: "))
	i_BoardHeight = int(input("Height: "))
	l_HorizontalPatterns = [[] for i in range(i_BoardHeight)]
	l_VerticalPatterns = [[] for i in range(i_BoardWidth)]
	l_HorizontalNumbers = [[] for i in range(i_BoardHeight)]
	l_VerticalNumbers = [[] for i in range(i_BoardWidth)]
	l_KnownSpots = [[None for j in range(i_BoardHeight)] for i in range(i_BoardWidth)] #indexes are [x][y], so horizontal index, then vertical index, [0][0] in top left, [n][n] in bottom right, [n][0] is upper right corner, etc
	b_PreFill = bool(input("Is the grid prefilled? "))
	print("Horizontal Numbers:")
	for i in range(i_BoardHeight):
		while(1): #keep trying to get row numbers and parse them.
			s_Input = input("Row "+str(i+1)+" numbers:")
			try:
				l_numbers = s_Input.split()
				for j in range(len(l_numbers)):
					l_numbers[j] = int(l_numbers[j])
				if minLengthOfRow(l_numbers)>i_BoardWidth:
					print("That seems too long to fit in a row of size",i_BoardWidth)
					continue
				break
			except:
				print("There was an error. Please try again.")
		l_HorizontalNumbers[i] = l_numbers

		if b_PreFill:
			while(1):
				s_prefill = input("Enter prefill (X for empty, F for filled, anything else for unknown): ").lower()
				if len(s_prefill)>i_BoardWidth:
					print("Err: prefill is too long.")
				else:
					break
			for j in range(len(s_prefill)):
				c = s_prefill[j]
				#i = which horizontal row
				#j = vertical index in i
				if c == "x":
					l_KnownSpots[j][i] = False
				elif c == "f":
					l_KnownSpots[j][i] = True
		l_HorizontalPatterns[i] = generatePossibleStates(i_BoardWidth,getHorizontalRow(l_KnownSpots,i),l_HorizontalNumbers[i])
	while(1):
		for i in range(len(l_HorizontalNumbers)):
			print("Row",i+1,"groups:",l_HorizontalNumbers[i])
		if b_PreFill:
			printBoard(l_KnownSpots)
		b_mistake = bool(input("Did you make a mistake anywhere?"))
		if b_mistake:
			i_mistakeIndex=int(input("Row number of the mistake:"))
			i_mistakeIndex -= 1

			while(1): #keep trying to get row numbers and parse them.
				s_Input = input("Row "+str(i_mistakeIndex+1)+" numbers:")
				try:
					l_numbers = s_Input.split()
					for j in range(len(l_numbers)):
						l_numbers[j] = int(l_numbers[j])
					if minLengthOfRow(l_numbers)>i_BoardWidth:
						print("That seems too long to fit in a row of size",i_BoardWidth)
						continue
					break
				except:
					print("There was an error. Please try again.")
			l_HorizontalNumbers[i_mistakeIndex] = l_numbers

			if b_PreFill:
				while(1):
					s_prefill = input("Enter prefill (X for empty, F for filled, anything else for unknown): ").lower()
					if len(s_prefill)>i_BoardWidth:
						print("Err: prefill is too long.")
					else:
						break
				for j in range(len(s_prefill)):
					c = s_prefill[j]
					#i = which horizontal row
					#j = vertical index in i
					if c == "x":
						l_KnownSpots[j][i_mistakeIndex] = False
					elif c == "f":
						l_KnownSpots[j][i_mistakeIndex] = True
					else:
						l_KnownSpots[j][i_mistakeIndex] = None
			l_HorizontalPatterns[i_mistakeIndex] = generatePossibleStates(i_BoardWidth,getHorizontalRow(l_KnownSpots,i_mistakeIndex),l_HorizontalNumbers[i_mistakeIndex])
		else:
			break

	
	print("\nVertical Numbers:")
	for i in range(i_BoardWidth):
		while(1): #keep trying to get collumn numbers and parse them.
			s_Input = input("Collumn "+str(i+1)+" numbers:")
			try:
				l_numbers = s_Input.split()
				for j in range(len(l_numbers)):
					l_numbers[j] = int(l_numbers[j])
				if minLengthOfRow(l_numbers)>i_BoardHeight:
					print("That seems too long to fit in a collumn of size",i_BoardHeight)
					continue
				break
			except:
				print("There was an error. Please try again.")
		l_VerticalNumbers[i] = l_numbers
		l_VerticalPatterns[i] = generatePossibleStates(i_BoardHeight,l_KnownSpots[i],l_VerticalNumbers[i])
	while(1):
		for i in range(len(l_VerticalNumbers)):
			print("Collumn",i+1,"groups:",l_VerticalNumbers[i])
		b_mistake = bool(input("Did you make a mistake anywhere?"))
		if b_mistake:
			i_mistakeIndex=int(input("Row number of the mistake:"))
			i_mistakeIndex -= 1
			while(1): #keep trying to get collumn numbers and parse them.
				s_Input = input("Collumn "+str(i_mistakeIndex+1)+" numbers:")
				try:
					l_numbers = s_Input.split()
					for j in range(len(l_numbers)):
						l_numbers[j] = int(l_numbers[j])
					if minLengthOfRow(l_numbers)>i_BoardHeight:
						print("That seems too long to fit in a collumn of size",i_BoardHeight)
						continue
					break
				except:
					print("There was an error. Please try again.")
			l_VerticalNumbers[i_mistakeIndex] = l_numbers
			l_VerticalPatterns[i_mistakeIndex] = generatePossibleStates(i_BoardHeight,l_KnownSpots[i_mistakeIndex],l_VerticalNumbers[i_mistakeIndex])
			
		else:
			break

	printBoard(l_KnownSpots)
	print()
	findKnownSpots(l_HorizontalPatterns,l_VerticalPatterns,l_KnownSpots)
	printBoard(l_KnownSpots)
	print()
	while(not isPuzzleSolved(l_KnownSpots)):
		b_DirtyBit = False
		if reducePatternList(l_HorizontalPatterns,l_VerticalPatterns,l_KnownSpots):
			b_DirtyBit = True
		if findKnownSpots(l_HorizontalPatterns,l_VerticalPatterns,l_KnownSpots):
			b_DirtyBit = True
		printBoard(l_KnownSpots)
		if not b_DirtyBit:
			print("Giving up. Insufficient Knowledge.")
			break
		print()
	printBoard(l_KnownSpots,True)

	




