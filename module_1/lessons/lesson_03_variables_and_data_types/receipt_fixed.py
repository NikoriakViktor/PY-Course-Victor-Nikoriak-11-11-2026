check = "receipt"
item = "coffee"
price = float("45.5")
quantity = 3

item = item.upper()
print(f"Item: {item}, quantity: {quantity}")

total = price * quantity
print(f"Total: {total} UAH")
print(f"Average: {total / quantity:.2f}")

# 1 - str shadows the built-in str;
# 3 - number was a string;
# 6 - need to assign the result;
# 7 - simultaneous use of string and an integer;
# 10 - simultaneous use of string and a float.
#AI log: used to check my code.