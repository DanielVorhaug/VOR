import sys
from time import sleep

# Known last words in a data type. Does not include custom data types
# Todo: Add detection of typedef's that add to this list
c_data_types = ["void", "char", "short", "int", "signed", "unsigned", "long", "float", "double", "bool"]


def error_invalid_number_of_arguments():
    print("Error: Invalid number of arguments.")
    sys.exit(1)


def error_invalid_file_name():
    print("Error: Invalid file name.")
    sys.exit(1)

def error_no_main():
    print("Error: No main function found.")
    sys.exit(1)

def error_multiple_main_functions():
    print("Error: Multiple main functions found.")
    sys.exit(1)

def error_could_not_find_main_body():
    print("Error: Could not find main function body.")
    sys.exit(1)

def error_function_calls_not_to_main():
    print("Error: Function call to a function other than main is found. This is not the way of VOR.")
    sys.exit(1)


def remove_comments(code):
    # Remove single line comments
    code = code.split("//")
    for i in range(1, len(code)):
        code[i] = code[i].split("\n")[1:]

    # Combine code back together
    first_part = code[0]
    code = "".join((j+"\n") for i in code[1:] for j in i)
    code = first_part + code

    # Remove multi line comments
    code = [i.split("*/") for i in code.split("/*")]
    for i in range(1, len(code)):
        code[i] = code[i][1:]

    # Combine code back together
    code = "".join(i[0] for i in code)

    return code

def get_code():
    code_file_name = sys.argv[1]
    # Read main file
    try:
        file = open(code_file_name, "r")
    except:
        error_invalid_file_name()
    code = file.read()
    file.close()
    return code

def get_main_body():
    code = remove_comments(get_code())

    # Find indexes of the word "main"
    main_index = []
    potential_index = code.find("main")
    offset = 0
    while potential_index != -1:
        main_index.append(potential_index + offset)
        offset = main_index[-1] + 4
        potential_index = code[offset:].find("main")
    if len(main_index) == 0:
        error_no_main()
    
    # Find index of the main function declaration
    main_function_index = []
    for index in main_index:
        code = code[:index].strip(" \n\t\r")
        if code[-1] == "*":
            code = code[:-1].strip(" \n\t\r")
        code = code.split()[-1].split("}")[-1].split(";")[-1].strip(" \n\t\r")
        if code in c_data_types or code[-2:] == "_t":
            main_function_index.append(index)
        code = remove_comments(get_code())
    if len(main_function_index) > 1:
        error_multiple_main_functions()

    # Determine the starting and ending index of the main function body
    bracket_level = 0
    first_bracket_found = False
    starting_index = 0
    for i in range(main_function_index[0], len(code)):
        if code[i] == "{":
            bracket_level += 1
            if not first_bracket_found:
                first_bracket_found = True
                starting_index = i + 1
        elif code[i] == "}":
            bracket_level -= 1
        if first_bracket_found and bracket_level == 0:
            return code[starting_index:i]
    error_could_not_find_main_body()


def check_num_arguments():
    if len(sys.argv) != 2:
        error_invalid_number_of_arguments()

def check_function_calls():
    main_body = get_main_body()

    # Look for cases of where '(' is used
    main_body = main_body.split("(")[:-1] # Remove the last element since that one cannot be a function call
    for part in main_body:
        if len(part.strip(" \n\t\r")) == 0:
            continue
        potential_function = part.split()[-1].strip(" \n\t\r")
        print(potential_function)
        # Determine if this is an illegal function call
        if potential_function not in ["main", "for", "while", "if", "switch", "return"] and potential_function[-1].isalnum():
            error_function_calls_not_to_main()
        
def main():
    check_num_arguments()
    check_function_calls()

main()
