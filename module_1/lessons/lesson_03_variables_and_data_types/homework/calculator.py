try:
    a = float(input("Input number a:"))
    b = float(input("Input number b:"))
    print(f"a + b = {a + b:.2f}")
    print(f"a - b = {a - b:.2f}")
    print(f"a / b = {a / b:.2f}")
    print(f"a * b = {a * b:.2f}")
    print(f"a ** b = {a ** b:.2f}")
    print(f"a % b = {a % b:.2f}")
    print(f"a // b = {a // b:.2f}")
except ValueError:
    print("Invalid input")

