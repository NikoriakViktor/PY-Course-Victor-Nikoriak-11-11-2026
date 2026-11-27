# AI log: запитав як правильно використати в f-рядку оператор if-else
value_in = input("Enter a number: ")
if value_in.isdigit():
    num = int(value_in)
    is_even = num % 2 == 0
    str_ret = f"{num} is {'even' if is_even else 'odd'}"
else:
    str_ret = f"{value_in} is not a number!"
print(str_ret)    