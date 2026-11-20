import sys

SECRET = 13

# YOUR CODE HERE
# BEGIN SOLUTION
if len(sys.argv) != 2 or not sys.argv[1].isdigit():
    print("Використання: python guess.py <кількість спроб>")
else:
    attempts = int(sys.argv[1])
    while attempts > 0:
        text = input("Твоє число: ").strip()
        if not text.isdigit():
            print("Потрібне ціле число")
            continue
        attempts -= 1
        guess = int(text)
        if guess == SECRET:
            print("Вгадав!")
            break
        elif guess < SECRET:
            print("Більше")
        else:
            print("Менше")
    else:
        print("Спроби закінчились. Було загадано:", SECRET)
# END SOLUTION
