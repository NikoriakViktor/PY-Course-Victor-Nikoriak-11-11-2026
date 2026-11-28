"""
Task 3. A simple calculator Create a function called make_operation, which takes in a simple arithmetic operator
as a first parameter (to keep things simple let it only be '+', '-' or '*') and an arbitrary number of arguments
(only numbers) as the second parameter. Then return the result of applying the operator
 to all the numbers from left to right.

the call make_operation('+', 7, 7, 2) should return 16
the call make_operation('-', 5, 5, -10, -20) should return 30
the call make_operation('*', 7, 6) should return 42
Before running, write as comments what make_operation('-', 10) and make_operation('*', 2, 0.5, 3) will return. Then add both calls to your file and compare.
"""
def make_operation(operator, *args):
    calc_types = ['int', 'float']
    result = None
    if len(args) > 1:
        for arg in args:
            if type(arg).__name__ in calc_types:
                if result is None:
                    result = arg
                else:
                    match operator:
                        case "+":
                            result += arg
                        case "-":
                            result -= arg
                        case "*":
                            result *= arg
                        case _:
                            return "Incorrect operator"
            else:
                return "Incorrect or single argument {arg}"
        return result
    else:
        return "Incorrect argument {arg}"

print(make_operation('+', 7, 7, 2))
print(make_operation('-', 5, 5, -10, -20))
print(make_operation('*', 7, 6))
# return 10 because no condition that describe this case (error, add -arg or etc.)
# add validation for one argument
print(make_operation('-', 10))
# return normal result because my function processing int, float. result = 3
print(make_operation('*', 2, 0.5, 3))
print(make_operation('4', 2, 'b', 3))