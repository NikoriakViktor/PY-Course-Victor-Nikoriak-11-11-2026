have_umbrella = True
rain_level = 0.0
have_hood = True
is_workday = True

"""
the condition that will return incorrect result
have_umbrella = False
rain_level = 5
have_hood = False
is_workday = False
"""
prepared = have_umbrella or rain_level < 5 and have_hood or not rain_level > 0 and is_workday
"""
incorrect result because we have a default order that doesn't meet the conditions of the problem
the is default logic with explicit conditions
"""
prepared_explicit = have_umbrella or ((rain_level < 5) and have_hood) or ((not (rain_level > 0)) and is_workday)
#by default, we get an incorrect condition in case it rains and not working day
prepared_correct = have_umbrella or (rain_level < 5 and have_hood) or not (rain_level > 0 and is_workday)
print(prepared)
print(prepared_explicit)
print(prepared_correct)


