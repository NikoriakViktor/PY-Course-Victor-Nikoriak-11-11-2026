import sys

str_ret = ""
n = 0

if len(sys.argv) != 2 or not sys.argv[1].isdigit():
    str_ret = "Usage: python countdown.py <integer>\n"
else:
    n = int(sys.argv[1])
    for n in range(n, 0, -1):
        str_ret += f"{n}\n"
    str_ret += "Let's go!\n"
print(str_ret, end="")
