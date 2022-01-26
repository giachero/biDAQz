import os
import pathlib


# Simple function to convert an empty string to 0 instead of giving an error
def StrToInt(val):
    return int(val or 0)


# Import the CAN bus commands to a dictionary from the C header file used by the firmware
def Import():

    ErrorDict = dict()

    with open(os.path.join(pathlib.Path(__file__).parent.absolute(), "Error_Handling.h"), encoding="ascii",
              errors="surrogateescape") as fp:

        FirstDefine = True

        while True:

            # Read new line an break loop at EOF
            line = fp.readline()
            if not line:
                break

            # Parse only lines starting with "#define"
            if not line.find("#define"):

                # skip first #define (#define __ERROR_HANDLING_H)
                if FirstDefine:
                    FirstDefine = False
                    continue

                # Remove "#define", strip tabs and spaces
                lineDef = line.replace("#define", "")
                lineDef = lineDef.strip(" \t")

                # Split at first tab
                lineDefSplit = lineDef.split("\t", 1)
                if len(lineDefSplit) == 1:
                    continue

                # The define name is the first element of the list
                DefineName = lineDefSplit[0]

                if "SUBSYS" in DefineName:
                    SubDict = dict()
                    MainKey = True
                else:
                    MainKey = False

                # Strip spaces, tabs and new lines and split at the first tab
                DefineStr = lineDefSplit[1].strip(" \t\n")
                DefineStr = DefineStr.split("\t", 1)

                # The define value is the first element of the list
                DefineVal = DefineStr[0]

                # Evaluate the define value to resolve any OR, or other C expressions
                Val = eval(DefineVal)

                # Fill the dictionary
                if MainKey:
                    ErrorDict["{}".format(Val)] = {"SubSys": DefineName, "SubDict": SubDict}
                else:
                    SubDict["{}".format(Val)] = {"Error": DefineName}

                # Create a local variable, used by next eval() calls
                locals()[DefineName] = Val

    return ErrorDict


# Main function executed within Python
if __name__ == "__main__":
    ret = Import()
    print(ret)
