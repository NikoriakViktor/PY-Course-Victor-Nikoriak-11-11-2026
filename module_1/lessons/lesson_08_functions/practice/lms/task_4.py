"""
Task 4. Minesweeper in functions Take the minesweeper code from Lesson 6. It works, but it is one long script, and the code that prints the board appears twice. Split it into functions:

create_bombs(size, count=10) – returns a set of bomb positions;
count_around(bombs, row, col) – returns how many bombs touch a cell;
create_board(size) – returns a new hidden board;
print_board(board) – prints the board;
read_move(size) – asks for a move until the input is correct and returns (row, col).
Every function gets what it needs through parameters and gives its result back with return (print_board only prints). The game loop stays at the bottom of the file and calls your functions. The game must work the same way as before.

At the top of the file, add a comment: which code is no longer repeated, and why read_move can stop its while loop with return instead of break.
"""
import random

SIZE = 8
BOMBS = 10

# Bombs: a set of (row, col) tuples, so one cell cannot get two bombs
def create_bombs(size, count=BOMBS):
    bombs = set()
    while len(bombs) < BOMBS:
        bombs.add((random.randint(0, SIZE - 1), random.randint(0, SIZE - 1)))

    return bombs

def count_around(bombs, row, col):
    counts = {}
    for row in range(SIZE):
        for col in range(SIZE):
            if (row, col) in bombs:
                continue
            around = 0
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if (row + dr, col + dc) in bombs:
                        around += 1
            counts[(row, col)] = around

    return counts

def create_board(size=SIZE):
    return [["." for col in range(SIZE)] for row in range(SIZE)]

def print_board(board):
    print("   0 1 2 3 4 5 6 7")
    for row in range(SIZE):
        line = str(row) + " "
        for cell in hidden[row]:
            line += " " + cell
        print(line)

def read_move(opened):
    while opened < SIZE * SIZE - BOMBS:
        print_board(hidden)

        answer = input("Row and column, for example 3 5: ").split()
        if len(answer) != 2 or not answer[0].isdigit() or not answer[1].isdigit():
            print("Type two numbers from 0 to 7")
            continue
        row, col = int(answer[0]), int(answer[1])
        if row >= SIZE or col >= SIZE:
            print("This cell is outside the board")
            continue
        if hidden[row][col] != ".":
            print("This cell is already open")
            continue
        if (row, col) in bombs:
            print("Boom! Game over.")
            break
        hidden[row][col] = str(counts[(row, col)])
        opened += 1
    else:
        print("You win!")

bombs = create_bombs(SIZE, BOMBS)
row_size = range(SIZE)
col_size = range(SIZE)
counts = count_around(bombs, row_size, col_size)
hidden = create_board(SIZE)
opened = 0
read_move(opened)

# Show where the bombs were
for row, col in bombs:
    hidden[row][col] = "*"
print("   0 1 2 3 4 5 6 7")
for row in range(SIZE):
    line = str(row) + " "
    for cell in hidden[row]:
        line += " " + cell
    print(line)