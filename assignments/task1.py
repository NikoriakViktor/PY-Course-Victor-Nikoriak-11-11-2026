# Завдання 1.
# Програма привітання. Створіть програму, яка зберігає ваше ім'я та поточний день тижня як окремі змінні,
# а потім виводить повідомлення такого вигляду:
# "Good day <name>! <day> is a perfect day to learn some python.
# "Використовуйте f-рядок. Зверніть увагу, що <name>та <day>є попередньо визначеними змінними у вихідному коді.

name = 'Yaroslav'
day = 'Wednesday'
f_str = f"Good day {name}! {day} is a perfect day to learn some python."
format_str = 'Good day {}! {} is a perfect day to learn some python.'.format(name, day)
str_with_percent = 'Good day %s! %s is a perfect day to learn some python.' % (name, day)
print(f_str)
print(format)
print(str_with_percent)

# Відправив би 1-й рядок (f-рядок). Причина: найзручніший спосіб
# для підстановки змінних у рядок. Видно, де яка змінна стоїть,
# і не потрібно слідкувати за порядком аргументів.