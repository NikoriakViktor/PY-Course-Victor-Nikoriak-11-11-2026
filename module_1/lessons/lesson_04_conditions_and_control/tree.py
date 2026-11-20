input_string = input('Input a string: ')

chars_count = 0
digits_count = 0
punctuations_count = 0
index = 0

while index < len(input_string):
    if input_string[index].isalpha():
        chars_count += 1
    elif input_string[index].isdigit():
        digits_count += 1
    elif input_string[index].isspace():
        pass
    else:
        punctuations_count += 1
    index += 1

# for character in input_string:
#     if character.isalpha():
#         chars_count += 1
#     elif character.isdigit():
#         digits_count += 1
#     elif character.isspace():
#         pass
#     else:
#         punctuations_count += 1

print(f"Chars: {chars_count}\nDigits: {digits_count}\nPunctuations: {punctuations_count}")
