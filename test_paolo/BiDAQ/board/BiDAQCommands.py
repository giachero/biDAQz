import os
import pathlib


# Simple function to convert an empty string to 0 instead of giving an error
def StrToInt(val):
    return int(val or 0)


# Import the CAN bus commands to a dictionary from the C header file used by the firmware
def Import():
    # Defined in another .h and required by the eval() function
    CAN_CMD_DATA_LENGTH = 6

    commandDict = dict()

    with open(os.path.join(pathlib.Path(__file__).parent.absolute(), "Commands.h"), encoding="ascii",
              errors="surrogateescape") as fp:

        while True:

            # Read new line an break loop at EOF
            line = fp.readline()
            if not line:
                break

            # Parse only lines starting with "#define"
            if not line.find("#define"):

                # Remove "#define", strip tabs and spaces
                lineDef = line.replace("#define", "")
                lineDef = lineDef.strip(" \t")

                # Split at first tab
                lineDefSplit = lineDef.split("\t", 1)
                if len(lineDefSplit) == 1:
                    continue

                # The define name is the first element of the list
                DefineName = lineDefSplit[0]

                # Strip spaces, tabs and new lines and split at the first tab
                DefineStr = lineDefSplit[1].strip(" \t\n")
                DefineStr = DefineStr.split("\t", 1)

                # The define value is the first element of the list
                DefineVal = DefineStr[0]

                # Output parameters (if any) are in the second element of the list
                if len(DefineStr) == 2:

                    # Strip spaces, tabs, new lines and slashes and split at commas
                    DefineOut = DefineStr[1].strip(" \t\n/")
                    DefineOut = DefineOut.split(",")

                    # If length of list is greater than 4, more than 2 output parameters are present
                    DefineOutList = [0, 4] if len(DefineOut) > 4 else [0]

                    # Create the list of output parameters
                    OutList = []
                    for i in DefineOutList:
                        TmpOut = DefineOut[i].split(":")
                        TmpOut = list(map(StrToInt, TmpOut))
                        OutList = OutList + [TmpOut]

                else:
                    OutList = [[0]]

                # Convert the one- or two-element lists (range extremities) to a full range
                OutListFinal = []
                for OutCurr in OutList:
                    if len(OutCurr) == 1:
                        OutListFinal = OutListFinal + [[x for x in range(OutCurr[0])]]
                    elif len(OutCurr) == 2:
                        OutListFinal = OutListFinal + [[x for x in range(OutCurr[0], OutCurr[1] + 1)]]

                # Evaluate the define value to resolve any OR, or other C expressions
                Val = eval(DefineVal)

                # Make the output parameter list unique
                OutListFinalUnique = [list(x) for x in set(tuple(x) for x in OutListFinal)]

                # Fill the dictionary
                commandDict[DefineName] = {"CommandByte": Val, "OutputByteList": OutListFinalUnique}

                # Create a local variable, used by next eval() calls
                locals()[DefineName] = Val

    return commandDict


# Main function executed within Python
if __name__ == "__main__":
    ret = Import()
    print(ret)
