                                                #===============================================================================#
                                                #                   Pontificia Universidad Javeriana, Cali                      #
                                                #                           Facultad de Ingeniería                              #
                                                #                    Ingeniería de Sistemas y Computación                       #
                                                #                       Arquitectura del Computador II                          #
                                                #                               Antonio Yu Chen                                 #
                                                #===============================================================================#

import re
from tkinter import *

# R0 will be the base address. It will point to the start of the data memory. It starts at the position 0.
# R1 and R2 will be the registers used for each of the operations.
# The memory address which points to the arrays will be 100. Each array has a size of 100.
# timeParameter: first position corresponds to period, second to frequency.
# balancedList: it will contain each of the opening bracket or parentheses, to check if a given algorithm is balanced.
# registerList: will contain the registers to be used in each of the instructions. These registers will have an offset,
# 				this means that each of these registers will be stored in the memory. It doesn't includes temporal registers.
# counterList: first position corresponds to else counter, second to while counter, third to endWhile counter,
#              fourth to doWhile counter, fifth to doEnd counter, sixth to for counter, seventh to forEnd counter.
# Split the algorithm that was written into the input text box and stores it in an array to start compiling the program.

# Initialization of window with widgets #
root = Tk()
root.title("Compilador a Von Neumann")
root.geometry("800x700")
inputText = Text(width = 35)
inputText.place(x = 35, y = 80)
outputText = Text(width = 35)
outputText.place(x = 485, y = 80)
inputLabel = Label(text = "Algoritmo en alto nivel", font = ("Inconsolata", 12))
inputLabel.place(x = 90, y = 50)
outputLabel = Label(text = "Algoritmo en Von Neumann", font = ("Inconsolata", 12))
outputLabel.place(x = 530, y = 50)
periodText = Text(height = 1, width = 10)
periodText.place(x = 35, y = 525)
periodLabel = Label(text = "Periodo de reloj", font = ("Inconsolata", 12))
periodLabel.place(x = 32, y = 500)
frequencyText = Text(height = 1, width = 10)
frequencyText.place(x = 35, y = 580)
frequencyLabel = Label(text = "Frecuencia de reloj", font = ("Inconsolata", 12))
frequencyLabel.place(x = 32, y = 555)
execText = Text(height = 1, width = 25)
execText.place(x = 483, y = 525)
execLabel = Label(text = "Tiempo de ejecucion", font = ("Inconsolata", 12))
execLabel.place(x = 480, y = 500)
outputText.config(state = DISABLED)
periodText.config(state = DISABLED)
frequencyText.config(state = DISABLED)
execText.config(state = DISABLED)
# Initialization of variables #
registerList = []
counterList = [0, 0, 0, 0, 0, 0, 0]
balancedList = []
timeParameter = [0, 0]

def matching(char1, char2):
	"""Function that checks if two brackets or parentheses matches and returns true if it does, false if it doesn't."""
	if(char1 == "(" and char2 == ")"):
		return 1
	elif(char1 == "[" and char2 == "]"):
		return 1
	elif(char1 == "{" and char2 == "}"):
		return 1
	else:
		return 0

def balanced(line):
	"""Function that checks for balanced parentheses or brackets in a given expression. Returns true if it does, false if it doesn't."""
	for char in line:
		if(char == "{" or char == "(" or char == "["):
			balancedList.append(char)
		elif(char == "}" or char == ")" or char == "]"):
			if(len(balancedList) == 0):
				bracketFlag = 0
				outputText.insert(END, "SyntaxError: missing parentheses.\n")
				return bracketFlag
			elif(matching(balancedList.pop(0), char) == 0):
				bracketFlag = 0
	if(len(balancedList) == 0):
		bracketFlag = 1
	else:
		bracketFlag = 0
	return bracketFlag

def validOperations(operations, line, grouping, lineNumber, groupBool):
	"""Function that checks if a given operation is valid. Returns true if it is, false if it isn't."""
	instruction = re.match(operations, line)
	flag = 1
	if(instruction.group(grouping) != None): # If the expression contains operations, it will check for a valid expression.
		temporal = re.sub("\s*", "", line) # Removes every whitespace in a given expression.
		operand = re.split("[-|=|+|*|/|;]", temporal) # Splits the expression, the results are the operands used in the expression.
		operand.pop(len(operand) - 1) # Removes the last whitespace in the operand list.
		for register in operand:
			# If a given operand is not a number, it will check if it exists in the register list. It means, if it has been declared.
			if(register.isdigit() == 0 and register not in registerList):
				flag = 0
				outputText.insert(END, "SyntaxError at line {}: {} has not been declared.\n\n".format(lineNumber, register))
	else: # If the expression doesn't contains operations, it is an assignation.
		if(groupBool == 0): # It will get the registers located in the first and second group.
			register1 = instruction.group(1)
			register2 = instruction.group(2)
		else: # If the expression comes from a FOR instruction, it will get registers, which are located in the second and third group.
			register1 = instruction.group(2)
			register2 = instruction.group(3)
		if(register1 not in registerList): # If a given register is not in the register list, it has not been declared.
			flag = 0
			outputText.insert(END, "SyntaxError at line {}: {} has not been declared.\n\n".format(lineNumber, register1))

		if(register2.isdigit() == 0 and register2 not in registerList): # If the operand is not a number, checks if it has been declared.
			flag = 0
			outputText.insert(END, "SyntaxError at line {}: {} has not been declared.\n\n".format(lineNumber, register2))
	return flag

def validAlgorithm(algorithm):
	"""Function that returns true if the algorithm is valid. False if it isn't."""
	tmpAlgorithm = algorithm
	lineNumber = 1
	outputText.config(state = NORMAL)

	# Declaration of every regular expression that can be accepted by the compiler.
	init = "^\s*(int)\s*([A-z]+[0-9]*);\s*$"
	ifWhile = "^\s*(if|while)[(]\s*([A-z]+[0-9]*|[0-9]+)\s*(<|>|!=|==|<=|>=)\s*([A-z]+[0-9]*|[0-9]+)\s*[)]\s*{\s*$"
	operationExp = "^\s*([A-z]+[0-9]*)\s*=\s*([A-z]+[0-9]*|[0-9]+)(\s*([-|+|*|/])\s*([A-z]+[0-9]*|[0-9]+))*;\s*$"
	doExp = "^\s*do\s*{\s*$"
	doWhileExp = "^\s*}\s*while[(]\s*([A-z]+[0-9]*|[0-9]+)\s*(<|>|!=|==|<=|>=)\s*([A-z]+[0-9]*|[0-9]+)\s*[)];\s*$"
	closingBracket = "^\s*}$"
	spaces = "^\s*$"
	alphanumeric = "\s*([A-z]+[0-9]*|[0-9]+)\s*"
	forOp = "\s*(([A-z]+[0-9]*)\s*=\s*([A-z]+[0-9]*|[0-9]+)(\s*([-|+|*|/])\s*([A-z]+[0-9]*|[0-9]+))*)\s*"
	forExpression = "^\s*for[(]" + forOp
	expression = forExpression + ";" + alphanumeric + "(<|>|!=|==|<=|>=)" + alphanumeric + ";" + forOp + "[)]\s*{\s*$"

	# Declaration of every flag which will make invalid the algorithm.
	flag = 0 # Valid or invalid algorithm.
	bracketFlag = 1 # If it is turned on, it is balanced.
	doFlag = 1 # If it is turned on, there's a balanced do while expression or none at all.
	doWhileFlag = 1 # If it is turned on, there's a balanced do while expression or none at all.
	syntaxFlag = 0 # If it is turned on, there's a syntax error in the algorithm.

	# If the line of code is an IF, WHILE, DO WHILE or FOR, it will check for balanced parentheses or brackets.
	# If the line of code contains an operation, if will check if the operands, if they are not numbers, are in the register list, that
	#    means if the given operand has been declared.
	while(tmpAlgorithm != []):
		if(re.match(init, tmpAlgorithm[0])): # Checks if the line is a declaration.
			flag = 1
			instruction = re.match(init, tmpAlgorithm[0])
			register = instruction.group(2)
			if(register not in registerList): # If it is, it will add the register to the registerList if it has not been added.
				registerList.append(register)
		elif(re.match(operationExp, tmpAlgorithm[0])):
			flag = validOperations(operationExp, tmpAlgorithm[0], 3, lineNumber, 0)
		elif(re.match(ifWhile, tmpAlgorithm[0])):
			flag = 1
			instruction = re.match(ifWhile, tmpAlgorithm[0])
			register1 = instruction.group(2)
			register2 = instruction.group(4)
			if(register1.isdigit() == 0 and register1 not in registerList):
				flag = 0
				outputText.insert(END, "SyntaxError at line {}: {} has not been declared.\n\n".format(lineNumber, register1))
			if(register2.isdigit() == 0 and register2 not in registerList):
				flag = 0
				outputText.insert(END, "SyntaxError at line {}: {} has not been declared.\n\n".format(lineNumber, register2))
			bracketFlag = balanced(tmpAlgorithm[0])
		elif(re.match(closingBracket, tmpAlgorithm[0])):
			flag = 1
			bracketFlag = balanced(tmpAlgorithm[0])
		elif(re.match(doWhileExp, tmpAlgorithm[0])):
			flag = 1
			instruction = re.match(doWhileExp, tmpAlgorithm[0])
			register1 = instruction.group(1)
			register2 = instruction.group(3)
			if(register1.isdigit() == 0 and register1 not in registerList):
				flag = 0
				outputText.insert(END, "SyntaxError at line {}: {} has not been declared.\n\n".format(lineNumber, register1))
			if(register2.isdigit() == 0 and register2 not in registerList):
				flag = 0
				outputText.insert(END, "SyntaxError at line {}: {} has not been declared.\n\n".format(lineNumber, register2))
			bracketFlag = balanced(tmpAlgorithm[0])
			if(doWhileFlag == 0):
				doWhileFlag = 1 # If the do flag is turned, it will turn it on.
			else:
				doFlag = 0 # If it is not turned, it means there's a while instruction without it's respective do. The syntax is incorrect.
		elif(re.match(doExp, tmpAlgorithm[0])):
			flag = 1
			bracketFlag = balanced(tmpAlgorithm[0])
			doWhileFlag = 0 # If the compiler reads a do, it will turn off a flag that will deactivate if it finds the respective while.
		elif(re.match(expression, tmpAlgorithm[0])):
			instruction = re.match(expression, tmpAlgorithm[0])
			operations1 = instruction.group(1)
			register1 = instruction.group(7)
			register2 = instruction.group(9)
			operations2 = instruction.group(10)
			flag = validOperations(forOp, operations1, 4, lineNumber, 1)
			flag = validOperations(forOp, operations2, 4, lineNumber, 1)
			if(register1.isdigit() == 0 and register1 not in registerList):
				flag = 0
				outputText.insert(END, "SyntaxError at line {}: {} has not been declared.\n\n".format(lineNumber, register1))
			if(register2.isdigit() == 0 and register2 not in registerList):
				flag = 0
				outputText.insert(END, "SyntaxError at line {}: {} has not been declared.\n\n".format(lineNumber, register2))
			bracketFlag = balanced(tmpAlgorithm[0])
		elif(re.match(spaces, tmpAlgorithm[0])): # If the line of code is a whitespace, it will ignore it.
			flag = 1
		else: # If the line of code doesn't matches any of the previous expressions, it is not valid. The syntax flag is turned on.
			syntaxFlag = 1
			outputText.insert(END, "SyntaxError at line {}: invalid syntax.\n".format(lineNumber))
		if(flag == 0): # If there was a single syntax error, it will turn on the syntax flag.
			syntaxFlag = 1
		lineNumber = lineNumber + 1
		tmpAlgorithm.pop(0)
	if(bracketFlag == 0):
		flag = 0
		outputText.insert(END, "SyntaxError: missing parentheses.\n")
	if(doFlag == 0 or doWhileFlag == 0):
		flag = 0
		outputText.insert(END, "SyntaxError: missing do or while expression.")
	if(syntaxFlag == 1):
		flag = 0
	if(frequencyText.get("1.0", "end-1c") == "" and periodText.get("1.0", "end-1c") == ""):
		flag = 0
		outputText.insert(END, "Frequency or period has not been declared.")
	elif(frequencyText.get("1.0", "end-1c").isdigit() == 0 and periodText.get("1.0", "end-1c").isdigit() == 0):
		flag = 0
		outputText.insert(END, "Incorrect declaration of frequency or period.")

	# If the frequency or period of the clock has been declared, it will add the given declaration to the timeParameter list.
	if(periodText.get("1.0", "end-1c").isdigit() == 1):
		timeParameter[0] = int(periodText.get("1.0", "end-1c"))
	if(frequencyText.get("1.0", "end-1c").isdigit() == 1):
		timeParameter[1] = int(frequencyText.get("1.0", "end-1c"))
	outputText.config(state = DISABLED)
	return flag

# grouping is the regular expression group. groupBool is to check if it comes from a FOR instruction or not,
# expression is the regular expression of the instruction.
def operations(line, cycles, grouping, groupBool, expression):
	"""Function that receives a line of code and applies the appropiate instruction in Von Neumann."""
	if(re.match(expression, line)):
		outputText.config(state = NORMAL)
		instruction = re.match(expression, line)
		if(instruction.group(grouping) != None): # If it is not none, there's an operation in the expression.
			temporal = re.sub("\s*", "", line)
			operator = re.split("[A-z]+[0-9]*|[0-9]+", temporal)
			operand = re.split("[-|=|+|*|/|;]", temporal) # List of registers in the expression. The first one is the storing register.
			if(grouping == 3): # If the expression comes from a source different from a FOR, it will remove the last element of the array.
				operand.pop(len(operand) - 1) # After the split, there's a whitespace at the end of the array. It's removed here.
			operator.pop(len(operator) - 1) # After the split, there's a whitespace at the end of the array. It's removed here.
			operator.pop(0) # After the split, there's a whitespace at the start of the array. It's removed here.
			operator.pop(0) # After the split, there's a '=' in the array. It's removed here.
			counter = 3 # From the third register onwards, every one of them is a temporal register.
			index = 0
			while(operator != []): # If the operator list is empty, it means there aren't any operations left.
				if("*" in operator or "/" in operator): # Checks if there's a '*' or '/' for hierarchy purposes.
					if(operator[index] == "*" or operator[index] == "/"): # Iterates the operator expression until it finds '*' or '/'.
						if(operand[index + 1] in registerList): # It is index + 1 since the first position of the operand is ignored.
							outputText.insert(END, "    MOV R1, [R0 + {}]\n".format(registerList.index(operand[index + 1])))
							cycles = cycles + 11
						else:
							outputText.insert(END, "    MOV R1, {}\n".format(operand[index + 1]))
							cycles = cycles + 6
						if(operand[index + 2] in registerList): # It is index + 2 because it is the second operand of the operation.
							outputText.insert(END, "    MOV R2, [R0 + {}]\n".format(registerList.index(operand[index + 2])))
							cycles = cycles + 11
						else:
							outputText.insert(END, "    MOV R2, {}\n".format(operand[index + 2]))
							cycles = cycles + 6
						if(operator[index] == "*"):
							outputText.insert(END, "    MUL R1, R2\n")
						else:
							outputText.insert(END, "    DIV R1, R2\n")
						outputText.insert(END, "    MOV R{}, R1\n".format(counter))
						cycles = cycles + 15
						operator.pop(index) # Removes the operator from the operator list.
						operand.pop(index + 1) # Removes the first operand from the operand list.
						operand.pop(index + 1) # Removes the second operand from the operand list.
						operand.insert(index + 1, "R{}".format(counter)) # Adds the temporal register to the operand list.
						index = 0 # Re-assigns the index to iterate the operator list again.
						counter = counter + 1 # Goes to the next temporal register.
						continue # Goes to the next iteration of the cycle, to check if there's still a '*' or '/' operator.
					index = index + 1
				else: # If there's not a '*' or '/' operator, if will check for '+' and '-'.
					if(operator[index] == "+" or operator[index] == "-"):
						if(operand[index + 1] in registerList):
							outputText.insert(END, "    MOV R1, [R0 + {}]\n".format(registerList.index(operand[index + 1])))
							cycles = cycles + 11
						else:
							outputText.insert(END, "    MOV R1, {}\n".format(operand[index + 1]))
							cycles = cycles + 6
						if(operand[index + 2] in registerList):
							outputText.insert(END, "    MOV R2, [R0 + {}]\n".format(registerList.index(operand[index + 2])))
							cycles = cycles + 11
						else:
							outputText.insert(END, "    MOV R2, {}\n".format(operand[index + 2]))
							cycles = cycles + 6
						if(operator[index] == "+"):
							outputText.insert(END, "    ADD R1, R2\n")
						else:
							outputText.insert(END, "    SUB R1, R2\n")
						outputText.insert(END, "    MOV R{}, R1\n".format(counter))
						cycles = cycles + 15
						operator.pop(index)
						operand.pop(index + 1)
						operand.pop(index + 1)
						operand.insert(index + 1, "R{}".format(counter))
						index = 0
						counter = counter + 1
						continue
					index = index + 1
			# Stores the result in the storing register or first position of the operand list.
			outputText.insert(END, "    MOV [R0 + {}], R{}\n\n".format(registerList.index(operand[0]), counter - 1))
			cycles = cycles + 10
		else: # If the operator list is empty, is an assignation expression.
			if(groupBool == 0): # Gets the first and second operand of the expression.
				register1 = instruction.group(1)
				register2 = instruction.group(2)
			else: # If the operation comes from a FOR instruction, gets the first and second operand of the expression from other groups.
				register1 = instruction.group(2)
				register2 = instruction.group(3)
			if(register2 in registerList):
				outputText.insert(END, "    MOV R1, [R0 + {}]\n".format(registerList.index(register2)))
				cycles = cycles + 11
			else:
				outputText.insert(END, "    MOV R1, {}\n".format(register2))
				cycles = cycles + 6
			outputText.insert(END, "    MOV [R0 + {}], R1\n\n".format(registerList.index(register1)))
			cycles = cycles + 10
		outputText.config(state = DISABLED)
	return cycles

# markup is the ending etiquette, endIndex is the index of said etiquette.
def logicOperation(register1, register2, operator, markup, endIndex, cycles):
	""""Function that receives the necessary parameters to make a logic operation and returns the cycles it takes."""
	# The logic operation will be the inverse one, instead of the given one in high level.
	outputText.config(state = NORMAL)
	if(register1 in registerList):
		outputText.insert(END, "    MOV R1, [R0 + {}]\n".format(registerList.index(register1)))
		cycles = cycles + 11
	else:
		outputText.insert(END, "    MOV R1, {}\n".format(register1))
		cycles = cycles + 6
	if(register2 in registerList):
		outputText.insert(END, "    MOV R2, [R0 + {}]\n".format(registerList.index(register2)))
		cycles = cycles + 11
	else:
		outputText.insert(END, "    MOV R2, {}\n".format(register2))
		cycles = cycles + 6
	if(operator == "<"):
		outputText.insert(END, "    BRM R1, R2, {}{}\n".format(markup, endIndex))
		outputText.insert(END, "    BRI R1, R2, {}{}\n".format(markup, endIndex))
		cycles = cycles + 20
	elif(operator == ">"):
		outputText.insert(END, "    BRME R1, R2, {}{}\n".format(markup, endIndex))
		outputText.insert(END, "    BRI R1, R2, {}{}\n".format(markup, endIndex))
		cycles = cycles + 20
	elif(operator == "=="):
		outputText.insert(END, "    BRM R1, R2, {}{}\n".format(markup, endIndex))
		outputText.insert(END, "    BRME R1, R2, {}{}\n".format(markup, endIndex))
		cycles = cycles + 20
	elif(operator == "!="):
		outputText.insert(END, "    BRI R1, R2, {}{}\n".format(markup, endIndex))
		cycles = cycles + 10
	elif(operator == "<="):
		outputText.insert(END, "    BRM R1, R2, {}{}\n".format(markup, endIndex))
		cycles = cycles + 10
	elif(operator == ">="):
		outputText.insert(END, "    BRME R1, R2, {}{}\n".format(markup, endIndex))
		cycles = cycles + 10
	outputText.config(state = DISABLED)
	return cycles

def forInstruction(algorithm, cycles):
	"""Function that receives an algorithm and checks for the FOR instruction and returns the cycles it takes."""

	# Declaration of the regular expression.
	alphanumeric = "\s*([A-z]+[0-9]*|[0-9]+)\s*"
	forOp = "\s*(([A-z]+[0-9]*)\s*=\s*([A-z]+[0-9]*|[0-9]+)(\s*([-|+|*|/])\s*([A-z]+[0-9]*|[0-9]+))*)\s*"
	opExpression = "^\s*([A-z]+[0-9]*)\s*=\s*([A-z]+[0-9]*|[0-9]+)(\s*([-|+|*|/])\s*([A-z]+[0-9]*|[0-9]+))*;\s*$"
	forExpression = "^\s*for[(]" + forOp
	expression = forExpression + ";" + alphanumeric + "(<|>|!=|==|<=|>=)" + alphanumeric + ";" + forOp + "[)]\s*{\s*$"

	if(re.match(expression, algorithm[0])):
		instruction = re.match(expression, algorithm[0])
		operations1 = instruction.group(1)
		register1 = instruction.group(7)
		operator = instruction.group(8)
		register2 = instruction.group(9)
		operations2 = instruction.group(10)
		currentFor = counterList[5] # Stores the current for index etiquette, to use it at the end of the instruction.
		currentEndFor = counterList[6] # Stores the current endFor index etiquette, to use it at the end of the instruction.
		counterList[5] = counterList[5] + 1 # Adds 1 to the for index, in case there's a nesting of FOR instructions.
		counterList[6] = counterList[6] + 1 # Adds 1 to the endFor index, in case there's a nesting of FOR instructions.
		cycles = operations(operations1, cycles, 4, 1, forOp)
		outputText.config(state = NORMAL)
		outputText.insert(END, "FOR{}:\n".format(currentFor))
		cycles = logicOperation(register1, register2, operator, "ENDFOR", currentEndFor, cycles)
		algorithm.pop(0) # Pops the current line of code, which is the FOR expression to continue reading the algorithm.
		while(re.match("^\s*}$", algorithm[0]) == None): # If the line of code isn't a closing bracket, it will continue reading.
			cycles = branchWhile(algorithm, cycles)
			cycles = operations(algorithm[0], cycles, 3, 0, opExpression)
			cycles = doWhile(algorithm, cycles)
			cycles = forInstruction(algorithm, cycles)
			algorithm.pop(0)
		cycles = operations(operations2, cycles, 4, 1, forOp)
		outputText.config(state = NORMAL)
		outputText.delete("end-1c", END)
		outputText.insert(END, "    JUMP FOR{}\n\n".format(currentFor))
		cycles = cycles + 5
		outputText.insert(END, "ENDFOR{}:\n".format(currentEndFor))
		outputText.config(state = DISABLED)
	for i in range(len(counterList)): # Empties the counter list after iterating the code.
		counterList[i] = 0
	return cycles

def doWhile(algorithm, cycles):
	"""Function that receives an algorithm and checks for the DO WHILE instruction and returns the cycles it takes."""
	if(re.match("^\s*do\s*{\s*$", algorithm[0])):
		outputText.config(state = NORMAL)
		currentDo = counterList[3] # Stores the current do index etiquette, to use it at the end of the instruction.
		currentDoEnd = counterList[4] # Stores the current doEnd index etiquette, to use it at the end of the instruction.
		outputText.insert(END, "DO{}:\n".format(currentDo))
		counterList[3] = counterList[3] + 1  # Adds 1 to the doWhile index, in case there's a nesting of DO WHILE instructions.
		counterList[4] = counterList[4] + 1  # Adds 1 to the doWhile index, in case there's a nesting of DO WHILE instructions.
		algorithm.pop(0)
		opExpression = "^\s*([A-z]+[0-9]*)\s*=\s*([A-z]+[0-9]*|[0-9]+)(\s*([-|+|*|/])\s*([A-z]+[0-9]*|[0-9]+))*;\s*$"

		# If the current line of the algorithm is not a while instruction, it will continue iterating it.
		while(re.match("^\s*}\s*while[(]\s*([A-z]+[0-9]*|[0-9]+)\s*(<|>|!=|==|<=|>=)\s*([A-z]+[0-9]*|[0-9]+)\s*[)];\s*", algorithm[0]) == None):
			cycles = branchWhile(algorithm, cycles)
			cycles = operations(algorithm[0], cycles, 3, 0, opExpression)
			cycles = doWhile(algorithm, cycles)
			cycles = forInstruction(algorithm, cycles)
			algorithm.pop(0)
		instruction = re.match("^\s*}\s*while[(]\s*([A-z]+[0-9]*|[0-9]+)\s*(<|>|!=|==|<=|>=)\s*([A-z]+[0-9]*|[0-9]+)\s*[)];\s*$", algorithm[0])
		register1 = instruction.group(1)
		operator = instruction.group(2)
		register2 = instruction.group(3) 
		outputText.config(state = NORMAL)
		cycles = logicOperation(register1, register2, operator, "DOEND", currentDoEnd, cycles)
		outputText.delete("end-1c", END) # Removes the last end of line in the translation box, just because.
		outputText.insert(END, "    JUMP DO{}\n\n".format(currentDo))
		cycles = cycles + 5
		outputText.insert(END, "DOEND{}:\n".format(currentDoEnd))
		outputText.config(state = DISABLED)
	for i in range(len(counterList)): # Empties the counter list after iterating the code.
		counterList[i] = 0
	return cycles

def branchWhile(algorithm, cycles):
	"""Function that receives an algorithm as parameter and the current cycles and applies if or while instructions."""
	if(re.match("^\s*(if|while)[(]\s*([A-z]+[0-9]*|[0-9]+)\s*(<|>|!=|==|<=|>=)\s*([A-z]+[0-9]*|[0-9]+)\s*[)]\s*{\s*$", algorithm[0])):
		outputText.config(state = NORMAL)
		instruction = re.match("^\s*(if|while)[(]\s*([A-z]+[0-9]*|[0-9]+)\s*(<|>|!=|==|<=|>=)\s*([A-z]+[0-9]*|[0-9]+)\s*[)]\s*{\s*$", algorithm[0])
		condition = instruction.group(1)
		register1 = instruction.group(2)
		operator = instruction.group(3)
		register2 = instruction.group(4)
		currentElse = counterList[0] # Stores the current else index etiquette, to use it at the end of the instruction.
		currentWhile = counterList[1] # Stores the current while index etiquette, to use it at the end of the instruction.
		currentEndWhile = counterList[2] # Stores the current endWhile index etiquette, to use it at the end of the instruction.
		markup = "" # If the expression is an IF, it will store an else etiquette. If not, it will store an endWhile etiquette.
		markupIndex = -1 # Current index of the end etiquette. If it is -1, there is a bug in the code.
		opExpression = "^\s*([A-z]+[0-9]*)\s*=\s*([A-z]+[0-9]*|[0-9]+)(\s*([-|+|*|/])\s*([A-z]+[0-9]*|[0-9]+))*;\s*$"
		if(condition == "if"):
			markup = "ELSE"
			markupIndex = currentElse
			counterList[0] = counterList[0] + 1  # Adds 1 to the else index, in case there's a nesting of IF instructions.
			algorithm.pop(0)
		if(condition == "while"):
			markup = "ENDWHILE"
			markupIndex = currentEndWhile
			counterList[1] = counterList[1] + 1  # Adds 1 to the while index, in case there's a nesting of WHILE instructions.
			counterList[2] = counterList[2] + 1  # Adds 1 to the while index, in case there's a nesting of WHILE instructions.
			outputText.insert(END, "WHILE{}:\n".format(currentWhile))
			algorithm.pop(0)
		cycles = logicOperation(register1, register2, operator, markup, markupIndex, cycles)
		while(re.match("^\s*}$", algorithm[0]) == None):
			cycles = branchWhile(algorithm, cycles)
			cycles = operations(algorithm[0], cycles, 3, 0, opExpression)
			cycles = doWhile(algorithm, cycles)
			cycles = forInstruction(algorithm, cycles)
			algorithm.pop(0)
		outputText.config(state = NORMAL)
		if(condition == "while"):
			outputText.delete("end-1c", END) # Removes the last end of line in the translation box, just because.
			outputText.insert(END, "    JUMP WHILE{}\n\n".format(currentWhile))
			cycles = cycles + 5
		outputText.insert(END, "{}{}:\n".format(markup, markupIndex))
		outputText.config(state = DISABLED)
	for i in range(len(counterList)): # Empties the counter list after iterating the code.
		counterList[i] = 0
	return cycles
	
def compiler(cycles):
	algorithm = (inputText.get("1.0", END)).split("\n") # Separates the algorithm by end of line and puts it in a list.
	balancedList[:] = [] # Empties the list, just in case.
	opExpression = "^\s*([A-z]+[0-9]*)\s*=\s*([A-z]+[0-9]*|[0-9]+)(\s*([-|+|*|/])\s*([A-z]+[0-9]*|[0-9]+))*;\s*$"
	if(validAlgorithm(algorithm)):
		algorithm = (inputText.get("1.0", END)).split("\n") # Re initializes the variable in case it was emptied before.
		outputText.config(state = NORMAL)
		outputText.insert(END, "    MOV R0, 0\n\n") # Inserts the base pointer of the array.
		cycles = cycles + 5
		outputText.config(state = DISABLED)
		while(algorithm != [] and cycles != 0):
			cycles = branchWhile(algorithm, cycles)
			cycles = operations(algorithm[0], cycles, 3, 0, opExpression)
			cycles = doWhile(algorithm, cycles)
			cycles = forInstruction(algorithm, cycles)
			algorithm.pop(0)
	return cycles

def translate():
	cycles = 1
	outputText.config(state = NORMAL)
	outputText.delete("1.0", END) # Deletes the current text of the translated 
	outputText.config(state = DISABLED)
	registerList[:] = []
	timeParameter[:] = [0, 0]
	if(inputText.get("1.0", END) != "\n"):
		cycles = compiler(cycles)
	outputFile = open("output.txt", "w")
	outputFile.write(outputText.get("1.0", "end-1c"))
	outputFile.close()
	execText.config(state = NORMAL)
	execText.delete("1.0", END)
	if(timeParameter[0] != 0):
		execText.insert(END, "{} ns".format(cycles * timeParameter[0]))
	elif(timeParameter[1] != 0):
		execText.insert(END, "{} ns".format(cycles / timeParameter[1]))
	execText.config(state = DISABLED)

def clear():
	"""Procedure that clears all the text boxes."""
	inputText.delete("1.0", END)
	outputText.config(state = NORMAL)
	outputText.delete("1.0", END)
	outputText.config(state = DISABLED)
	periodText.config(state = NORMAL)
	periodText.delete("1.0", END)
	periodText.config(state = DISABLED)
	frequencyText.config(state = NORMAL)
	frequencyText.delete("1.0", END)
	frequencyText.config(state = DISABLED)
	execText.config(state = NORMAL)
	execText.delete("1.0", END)
	execText.config(state = DISABLED)
	registerList[:] = []
	balancedList[:] = []
	timeParameter[:] = [0, 0]
	for i in range(len(counterList)):
		counterList[i] = 0

def period():
	"""Procedure that enables the periodText text box and clears the frequencyText text box."""
	frequencyText.config(state = NORMAL)
	frequencyText.delete("1.0", END)
	frequencyText.config(state = DISABLED)
	periodText.config(state = NORMAL)

def frequency():
	"""Procedure that enables the frequencyText text box and clears the frequencyText text box."""
	periodText.config(state = NORMAL)
	periodText.delete("1.0", END)
	periodText.config(state = DISABLED)
	frequencyText.config(state = NORMAL)

translateButton = Button(text = "Traducir", font = ("Inconsolata", 12), command = translate)
translateButton.place(x = 365, y = 250)
clearButton = Button(text = "Limpiar", font = ("Inconsolata", 12), command = clear)
clearButton.place(x = 365, y = 300)
periodButton = Button(text = "Periodo de reloj", font = ("Inconsolata", 9), command = period)
periodButton.place(x = 165, y = 500)
frequencyButton = Button(text = "Frecuencia de reloj", font = ("Inconsolata", 9), command = frequency)
frequencyButton.place(x = 180, y = 555)