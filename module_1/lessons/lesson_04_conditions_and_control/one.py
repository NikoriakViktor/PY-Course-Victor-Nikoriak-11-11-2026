number_for_check = input('Input a number: ')
if number_for_check.isdigit() or number_for_check.startswith('-') and number_for_check.replace('-', '').isdigit():
    new_number_for_check = number_for_check.replace('-', '')
    if int(new_number_for_check) % 2 != 0:
        print(f"The number {number_for_check} is odd")
    else:
        print(f"The number {number_for_check} is even")
else:
    print('Input a integer number!')