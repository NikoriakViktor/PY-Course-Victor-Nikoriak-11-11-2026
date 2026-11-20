import sys

if len(sys.argv) != 2:
    print("Використання: python grade.py <бал>")
elif not sys.argv[1].isdigit():
    print("Бал має бути цілим числом, отримано:", sys.argv[1])
else:
    score = int(sys.argv[1])
    if score > 100:
        print("Бал не може бути більшим за 100")
    elif score >= 90:
        print("A")
    elif score >= 75:
        print("B")
    elif score >= 60:
        print("C")
    else:
        print("F")
