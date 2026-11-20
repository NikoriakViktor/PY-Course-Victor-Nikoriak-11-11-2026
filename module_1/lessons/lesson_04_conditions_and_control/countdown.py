import sys

# YOUR CODE HERE
# BEGIN SOLUTION
if len(sys.argv) != 2 or not sys.argv[1].isdigit():
    print("Використання: python countdown.py <ціле число>")
else:
    n = int(sys.argv[1])
    while n > 0:
        print(n)
        n -= 1
    print("Поїхали!")
# END SOLUTION
