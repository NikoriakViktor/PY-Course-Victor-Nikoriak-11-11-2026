from datetime import date

name = 'Sasha'
day = date.today().strftime("%A")

print(f"Good day {name}! {day}")
print("Good day {}! {}".format(name, day))
print("Good day %s! %s" % (name, day))