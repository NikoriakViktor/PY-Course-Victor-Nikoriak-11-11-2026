"""
Розібраний приклад: звіт кафе за днями¶
"""
from typing import NamedTuple


class Order(NamedTuple):
    waiter: str
    total_bill: float
    tip: float
    day: str
    time: str
    size: int


orders = [
    Order("Тарас", 540.0, 50.0, "пт", "вечеря", 2),
    Order("Марія", 320.0, 30.0, "пт", "обід", 1),
    Order("Тарас", 980.0, 120.0, "сб", "вечеря", 4),
    Order("Олексій", 760.0, 70.0, "сб", "вечеря", 3),
    Order("Марія", 450.0, 0.0, "нд", "обід", 5),
]

orders_by_day = {}
revenue_by_day = {}
tips_by_day = {}
bills_by_time = {}
for order in orders:
    orders_by_day[order.day] = orders_by_day.get(order.day, 0) + 1
    revenue_by_day[order.day] = revenue_by_day.get(order.day, 0) + order.total_bill
    bills_by_time.setdefault(order.time, []).append(order.total_bill)
    tips_by_day[order.day] = tips_by_day.setdefault(order.day, 0.0) + order.tip

average_by_day = {day: revenue_by_day[day] / orders_by_day[day] for day in revenue_by_day}
"""
Зміни приклад: чайові за днями¶
Додай до програми словник, який для кожного дня зберігає частку чайових від виторгу у відсотках,
 округлену до одного знака після коми. Для чеків з прикладу:
"""
avg_tips_by_day = {day: round(tips_by_day[day] / revenue_by_day[day] * 100, 1) for day in tips_by_day}

best_day = None
for day, revenue in revenue_by_day.items():
    if best_day is None or revenue > revenue_by_day[best_day]:
        best_day = day

for day in revenue_by_day:
    print(day, "— чеків:", orders_by_day[day], "виторг:", revenue_by_day[day], "середній:", average_by_day[day])
print("Найкращий день:", best_day)
print("За прийомом їжі:", bills_by_time)
print(f"Tips by days in percentages of day revenue: {avg_tips_by_day}")