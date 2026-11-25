"""
Task 5. Your own shop

Adapt stock and prices from Task 1 to a shop with 5–7 products.

In a while loop, ask for a product and quantity. Stop when the buyer enters done.
- Handle missing or unavailable products and requests larger than the available quantity.
- Decrease stock and store the order in cart = {product: quantity}.
- Print a receipt with quantity, price, cost and total.
- Print products that are out of stock, using a list comprehension.
At the top of the file, explain in a comment why cart is a dictionary rather than a list.
"""
from typing import NamedTuple

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

cart = {}

print(f"Welcome to the shop!")
print("We sell:")
print('-' + '\n-'.join(prices.keys()))
while True:
    product = input("Enter product name: ").strip().lower()
    if product == 'done':
        break
    elif product == 'cart' and cart:
        print("Your cart:")
        print(f"{'Name':<8} | {'QTY':<4} | {'Price':<8} | {'Cost':<4}")
        cart_total = 0
        for p, qty in cart.items():
            print(f"{p:<8} | {qty:<4} | {prices[p]:<8} | {str(prices[p] * qty):<4}")
            cart_total += prices[p] * qty
        print(f"{'=' * 33}")
        print(f"{'Total':<8}   {'':<4}   {'':<8}   {str(cart_total):<4}")

        print()
        continue
    elif product not in {p: qty for p, qty in prices.items() if qty > 0}:
        print(f"Sorry, {product} is not available.")
        continue

    quantity = input(f"Enter {product} quantity: ")
    if quantity.isdigit():
        quantity = int(quantity)
        if product in stock and quantity > stock[product]:
            print(f"Sorry, {product} in qty {quantity} is not available.")
        elif product in stock:
            cart[product] = cart.get(product, 0) + int(quantity)
            stock[product] = stock.get(product, 0) - quantity
            print(f"You added {quantity} {product} to your cart.")

    else:
        print(f"Sorry, {product} qty is not available or incorrect number symbol, please try again.")

print(f"{'Your Order':*^33}")
print(f"We sell: {cart}")
print(f"{'Name':<8} | {'QTY':<4} | {'Price':<8} | {'Cost':<4}")
for p, qty in cart.items():
    print(f"{p:<8} | {qty:<4} | {prices[p]:<8} | {str(prices[p] * qty):<4}")
print(f"{'=' * 33}")
print(f"{'Total':<8}   {'':<4}   {'':<8}   {str(sum(qty * prices[p] for p, qty in cart.items())):<4}")