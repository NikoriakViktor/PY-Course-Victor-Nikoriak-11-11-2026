have_umbrella = False
rain_level = 3.0
have_hood = False
is_workday = False

prepared = have_umbrella or (rain_level < 5 and have_hood) or not (rain_level > 0 and is_workday)
print(prepared)
# Bug: Python evaluates not before and, and before or.
# AI log: used to check my code.