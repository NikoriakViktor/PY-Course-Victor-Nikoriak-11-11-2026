"""
Task 2. Creating a dictionary Create a function called make_country, which takes in a country's name and capital
as parameters. Then create a dictionary from those two, with 'name' as a key and 'capital' as a key.
Call the function twice: once with positional arguments and once with keyword arguments in a different order.
Before running, write as a comment what make_country("Kyiv", "Ukraine") returns – the arguments are swapped on purpose.
"""
def make_country(name, capital):
    return {name: capital}
# normal order
print(make_country('Ukraine', 'Kyiv'))
# normal order
print(make_country(capital='Kyiv', name='Ukraine'))
# incorrect order because positional arguments have incorrect position for capital and name {'Kyiv', 'Ukraine'}
print(make_country("Kyiv", "Ukraine"))