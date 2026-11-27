# Task 5 — your own nameplate
# Write a program that prints a small "nameplate" about you: your name, your city, and one reason you started this course.

# Conditions:

# use sep at least once and end at least once;
# use \n or \t to line the output up;
# no new syntax — only what you met today. No variables, no if, no loops; they come in lessons 3 and 4;
# the last line of your output must be a separator you designed yourself (for example, a row of - or =).

print(72 * "=")
print("My name is:", "I live in:\t", "I'm in this course because:", sep="\t|")
print("Arsenii\t", "Krakow, Poland\t", "I want to become a Python Developer", sep="\t|")
print(72 * "=")


# AI log: Asked how to align items, answer: additional \t
