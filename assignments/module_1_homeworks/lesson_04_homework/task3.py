# AI log: none

input_value = input("Enter a string: ")
chars_count = 0
digits_count = 0
punctuations_count = 0
n = 0

while n < len(input_value):
    if input_value[n].isalpha():
        chars_count += 1
    elif input_value[n].isdigit():
        digits_count += 1
    elif not input_value[n].isalnum() and not input_value[n] == " ":
        punctuations_count += 1
    n += 1

print(f"{input_value} -> Chars: {chars_count}, Digits: {digits_count}, Punctuations: {punctuations_count}")

# Hi, 2026! -> Chars: 2, Digits: 4, Punctuations: 2