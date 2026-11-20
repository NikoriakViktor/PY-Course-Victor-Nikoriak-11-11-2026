import sys

# YOUR CODE HERE
# BEGIN SOLUTION
if len(sys.argv) != 2 or not sys.argv[1].isdigit():
    print("Використання: python digits.py <ціле число>")
else:
    number = int(sys.argv[1])
    total = 0
    while number > 0:
        total += number % 10
        number //= 10
    print("Сума цифр:", total)
# END SOLUTION
