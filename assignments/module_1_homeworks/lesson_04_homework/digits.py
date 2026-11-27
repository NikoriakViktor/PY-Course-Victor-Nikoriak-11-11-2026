import sys

sum_digits = 0

if len(sys.argv) != 2 or not sys.argv[1].isdigit():
    ret_str = "Usage: python digits.py <number>\n"
else:
    n = int(sys.argv[1])    
    while n > 0:
        sum_digits += n % 10
        n //= 10
    ret_str = f"Total sum of digits: {sum_digits}\n"
print(ret_str, end="")
