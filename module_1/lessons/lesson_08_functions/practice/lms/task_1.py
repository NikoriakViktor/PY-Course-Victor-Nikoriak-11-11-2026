"""
Task 1. A simple function Create a simple function called favorite_movie, which takes a string containing
the name of your favorite movie. The function should then return the string "My favorite movie is named {name}".
At the end of the program, create the variable new_string with your favorite movie
(for example, new_string = "2001: A Space Odyssey"), call the function with new_string and print the result.
 Below, call the function once more without print: favorite_movie("Dune"). Then make a copy of the function where
  return is replaced with print, and call it as print(favorite_movie_2(new_string)). Before running, write as
   comments what each of the two new lines will show on the screen and why.
"""
def favorite_movie(name):
    return f"My favorite movie is {name}"

def favorite_movie_2(name):
    print(f"My favorite movie is {name}")

new_string = "2001: A Space Odyssey"

print(favorite_movie(new_string))

print('======')
# won't print anything
favorite_movie("Dune")
# will return print() from function and value None as function return
print(favorite_movie_2(new_string))