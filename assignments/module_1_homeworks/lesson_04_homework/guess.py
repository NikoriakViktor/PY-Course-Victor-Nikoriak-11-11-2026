import sys

SECRET = 13
if len(sys.argv) != 2 or not sys.argv[1].isdigit():
    print("Usage: python guess.py <number of attempts>")
else:
    attempts = int(sys.argv[1])
    while attempts > 0:
        text = input("Your number: ").strip()
        if not text.isdigit():
            print("An integer is required")
            continue
        attempts -= 1
        guess = int(text)
        if guess == SECRET:
            print("You guessed it!")
            break
        elif guess < SECRET:
            print("Higher")
        else:
            print("Lower")
    else:
        print("You're out of attempts. The number was:", SECRET)
