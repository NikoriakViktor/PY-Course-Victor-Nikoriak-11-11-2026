"""
Task 3. Days of the week

Create a list with the days of the week.
Create a dictionary such as {1: "Monday", 2: "Tuesday", ...}, preferably with a dict comprehension.
Create the reverse dictionary {"Monday": 1, "Tuesday": 2, ...}.
Before running, write comments predicting days[0], week[1] and reverse_week["Sunday"]. Print and compare.
"""

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
week = {day: name for day, name in enumerate(days, start=1)}
reverse_week = {name: day for day, name in week.items()}

print(f"The days[0] == 'Monday' -> {days[0] == 'Monday'}")
print(f"The week[1] == 'Monday' -> {week[1] == 'Monday'}")
print(f"The reverse_week['Sunday'] == 7 -> {reverse_week['Sunday'] == 7}")