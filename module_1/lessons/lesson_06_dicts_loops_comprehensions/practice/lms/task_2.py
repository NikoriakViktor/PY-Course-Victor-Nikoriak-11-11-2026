"""
Task 2. List comprehension exercise

Use a list comprehension to make and print a list of tuples (i, j), where i goes from 1 to 10 and j is i squared.
 Below it, build the same list with a regular for loop and append(). In a comment, state which version
  is easier to read and why.
"""
comprehension_list = [(i, i**2) for i in range(1, 11)]

for_loop_list = []
for i in range(1, 11):
    for_loop_list.append((i, i**2))

print(f"The type of for_loop_list is {type(for_loop_list)}")
print(f"The {for_loop_list = }")
print(f"The type of comprehension_list is {type(comprehension_list)}")
print(f"The {comprehension_list = }")