str_line = "receipt" #use reserved variable name
item = "coffee"
price = "45.5"
quantity = 3

item_upper = item.upper() #method not change the string
print("Item: " + item_upper + ", quantity: " + str(quantity)) #TypeError: can only concatenate str (not "int") to str ///int->str

total = float(price) * quantity #incorrect type price->string->convert->float
print("Total: " + str(total) + " UAH") #TypeError: can only concatenate str (not "float") to str
print(f"Average: {total / quantity:.2f}")