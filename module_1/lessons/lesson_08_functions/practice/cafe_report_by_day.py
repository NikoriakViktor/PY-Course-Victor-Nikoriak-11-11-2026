from typing import NamedTuple


class Order(NamedTuple):
    total_bill: float
    tip: float
    day: str
    time: str
    size: int


def count_by_day(orders):
    """Кількість чеків у кожен день."""
    counts = {}
    for order in orders:
        counts[order.day] = counts.get(order.day, 0) + 1
    return counts


def revenue_by_day(orders):
    """Сума чеків за кожен день."""
    revenue = {}
    for order in orders:
        revenue[order.day] = revenue.get(order.day, 0) + order.total_bill
    return revenue


def average_by_day(counts, revenue):
    """Середній чек за кожен день."""
    return {day: revenue[day] / counts[day] for day in revenue}


def best_day(revenue):
    """День з найбільшим виторгом."""
    best = None
    for day, amount in revenue.items():
        if best is None or amount > revenue[best]:
            best = day
    return best

def bills_by_time(orders):
    """Суми чеків, згруповані за прийомом їжі."""
    groups = {}
    for order in orders:
        groups.setdefault(order.time, []).append(order.total_bill)
    return groups

def orders_by_time(orders, time = 'вечеря'):
    return {order for order in orders if order.time == time}

def orders_tip_percent(orders):
    return [round(order.tip / order.total_bill * 100, 1) for order in orders]

def average_tips(orders):
    if (orders):
        return sum(orders_tip_percent(orders)) / len(orders)

    return 0

def print_report(orders):
    """Друкує звіт кафе за списком чеків."""
    counts = count_by_day(orders)
    revenue = revenue_by_day(orders)
    average = average_by_day(counts, revenue)
    evening_orders = orders_by_time(orders)
    for day in revenue:
        print(day, "— чеків:", counts[day], "виторг:", revenue[day], "середній:", average[day])
    print("Найкращий день:", best_day(revenue))
    print("За прийомом їжі:", bills_by_time(orders))
    print("Вечерь:", len(evening_orders))
    print(f"Чайові на вечері, %: {orders_tip_percent(evening_orders)}")
    print(f"Середні чайові на вечері: {average_tips(evening_orders):.1f}")


orders = [
    Order(540.0, 50.0, "пт", "вечеря", 2),
    Order(320.0, 30.0, "пт", "обід", 1),
    Order(980.0, 120.0, "сб", "вечеря", 4),
    Order(760.0, 70.0, "сб", "вечеря", 3),
    Order(450.0, 0.0, "нд", "обід", 5),
]

next_weekend = [
    Order(610.0, 60.0, "сб", "обід", 2),
    Order(1200.0, 150.0, "нд", "вечеря", 6),
]

print_report(orders)
print('=' * 79)
print_report(next_weekend)