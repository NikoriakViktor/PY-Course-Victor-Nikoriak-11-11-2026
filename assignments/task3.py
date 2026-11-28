#Результат для для 'Hi, 2026!.' буде - Символів:2, Чисел:4, Розділових знаків:3

i = input('Введіть значення: ') # задаємо значення

chars_count = 0   # всі параметри прирівнюємо до нуля
digits_count = 0
punctuations_count = 0
counter = 0       #додаємо лічильник для реалізації циклу while

while counter < len(i):
    chars = i[counter]

    if chars.isalpha():
        chars_count += 1
    elif chars.isdigit():
        digits_count += 1
    elif chars != ' ':
        punctuations_count += 1

    counter +=1

print("Chars:", chars_count, "Digits:", digits_count, "Punctuations:", punctuations_count)


