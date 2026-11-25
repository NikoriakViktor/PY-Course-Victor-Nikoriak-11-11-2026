"""
Task 1. Total price of the stock

stock = {
    "banana": 6,
    "apple": 0,
    "orange": 32,
    "pear": 15
}

prices = {
    "banana": 4,
    "apple": 2,
    "orange": 1.5,
    "pear": 3
}
The stock dictionary contains quantities; prices contains the price of one item. Compute and print the total value of
the stock. Before running, write as a comment how much all oranges cost and what total you expect.
"""
stock = {
    "banana": 6,
    "apple": 0,
    "orange": 32,
    "pear": 15
}
prices = {
    "banana": 4,
    "apple": 2,
    "orange": 1.5,
    "pear": 3
}

total_value = 0
total_stock = 0
for key, value in stock.items():
    if value > 0:
        total_value += prices[key] * value
        total_stock += value

print(f"Total value: {total_value}")
print(f"Total stock: {total_stock}")