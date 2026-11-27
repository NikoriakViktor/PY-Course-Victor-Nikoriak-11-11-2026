import sys

if len(sys.argv) != 2:
    print("Usage: python grade.py <score>")
elif not sys.argv[1].isdigit():
    print("The score must be a whole number: ", sys.argv[1])
else:
    score = int(sys.argv[1])
    if score > 100:
        print("The score cannot be greater than 100.")
    elif score >= 90:
        print("A")
    elif score >= 75:
        print("B")
    elif score >= 60:
        print("C")
    else:
        print("F")
