"""Дашборд диспетчерської: читає Redis раз на секунду. Мапа, KPI, рейтинг, стрічка подій."""
import json
import logging
import time

import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html

from . import config as C
from .config import get_redis
from .log import log
from .seed import seed_redis

# Dash опитує сервер щосекунди — без цього кожне опитування давало б рядок у лозі
logging.getLogger("werkzeug").setLevel(logging.WARNING)

r = get_redis()
seed_redis(r)

COLORS = {"free": "#27ae60", "busy": "#e67e22"}
CARD = {"background": "white", "borderRadius": "10px", "padding": "12px 16px",
        "boxShadow": "0 1px 4px rgba(0,0,0,.12)", "flex": "1"}

app = Dash(__name__, title="Смачно + Таксі · Диспетчерська")
app.layout = html.Div(style={"fontFamily": "system-ui", "background": "#f4f6f8", "padding": "20px"}, children=[
    html.H2("🍕🚕 Смачно + Таксі · диспетчерська (Redis live)"),
    html.Div(id="kpis", style={"display": "flex", "gap": "12px", "marginBottom": "14px"}),
    html.Div(style={"display": "flex", "gap": "14px"}, children=[
        html.Div(dcc.Graph(id="map", style={"height": "560px"}), style={**CARD, "flex": "3"}),
        html.Div(style={"flex": "2", "display": "flex", "flexDirection": "column", "gap": "12px"}, children=[
            html.Div([html.H4("🏆 Рейтинг кур'єрів (ZSET)"), html.Div(id="leaderboard")], style=CARD),
            html.Div([html.H4("📡 Події (Pub/Sub + LIST)"), html.Div(id="feed")], style=CARD),
        ]),
    ]),
    dcc.Interval(id="tick", interval=1000),
])


def kpi(title: str, value, hint: str):
    return html.Div([html.Div(title, style={"fontSize": 12, "color": "#777"}),
                     html.Div(str(value), style={"fontSize": 28, "fontWeight": 700}),
                     html.Div(hint, style={"fontSize": 11, "color": "#999"})], style=CARD)


@app.callback(Output("kpis", "children"), Output("map", "figure"),
              Output("leaderboard", "children"), Output("feed", "children"), Input("tick", "n_intervals"))
def refresh(_):
    hit, miss = int(r.get(C.STAT_CACHE_HIT) or 0), int(r.get(C.STAT_CACHE_MISS) or 0)
    kpis = [
        kpi("Замовлень сьогодні", r.get(f"stats:orders:{time.strftime('%Y-%m-%d')}") or 0, "INCR"),
        kpi("Активних", r.zcard(C.ORDERS_ACTIVE), "ZSET orders:active"),
        kpi("Доставлено", r.get(C.STAT_DELIVERED) or 0, "INCR"),
        kpi("Унікальних клієнтів", r.pfcount(C.CUSTOMERS_UNIQUE), "HyperLogLog"),
        kpi("Вільних кур'єрів", r.scard(C.COURIERS_FREE), "SET couriers:free"),
        kpi("Cache hit", f"{hit / (hit + miss):.0%}" if hit + miss else "—", f"{hit} hit / {miss} miss"),
    ]

    fig = go.Figure()
    rests = [(rid, r.hgetall(C.restaurant_key(rid))) for rid in r.zrange(C.RESTAURANTS_GEO, 0, -1)]
    fig.add_trace(go.Scattermap(
        lat=[float(x["lat"]) for _, x in rests], lon=[float(x["lon"]) for _, x in rests],
        text=[x["name"] for _, x in rests], mode="markers+text", textposition="top center",
        marker={"size": 16, "color": "#c0392b"}, name="Ресторани", hoverinfo="text"))

    active = [r.hgetall(C.order_key(o)) for o in r.zrange(C.ORDERS_ACTIVE, 0, -1)]
    active = [o for o in active if o]
    fig.add_trace(go.Scattermap(
        lat=[float(o["lat"]) for o in active], lon=[float(o["lon"]) for o in active],
        text=[f"#{o['id']} · {o['status']}" for o in active], mode="markers",
        marker={"size": 11, "color": "#2980b9"}, name="Клієнти", hoverinfo="text"))

    for status, label in (("free", "Кур'єр вільний"), ("busy", "Кур'єр у дорозі")):
        pts = []
        for cid in r.smembers(C.COURIERS_ALL):
            c = r.hgetall(C.courier_key(cid))
            pos = r.geopos(C.COURIERS_GEO, cid)[0]
            if c.get("status") == status and pos:
                pts.append((pos[1], pos[0], f"{c['name']} ({cid})"))
        fig.add_trace(go.Scattermap(
            lat=[p[0] for p in pts], lon=[p[1] for p in pts], text=[p[2] for p in pts],
            mode="markers", marker={"size": 14, "color": COLORS[status]}, name=label, hoverinfo="text"))
    fig.update_layout(map={"style": "open-street-map", "center": {"lat": C.CITY_LAT, "lon": C.CITY_LON},
                           "zoom": 10.2}, margin={"l": 0, "r": 0, "t": 0, "b": 0},
                      legend={"orientation": "h", "y": 0.01}, uirevision="keep")

    top = r.zrevrange(C.LB_COURIERS, 0, 4, withscores=True)
    board = [html.Div(f"{i}. {r.hget(C.courier_key(cid), 'name')} — {int(s)} доставок")
             for i, (cid, s) in enumerate(top, 1)] or [html.Div("Ще немає доставок…", style={"color": "#999"})]

    feed = []
    for raw in r.lrange(C.EVENTS_LOG, 0, 11):
        ev = json.loads(raw)
        feed.append(html.Div(ev["text"], style={"fontSize": 13, "padding": "2px 0"}))
    return kpis, fig, board, feed


if __name__ == "__main__":
    log.task("дашборд читає Redis раз на секунду → http://localhost:8060")
    app.run(host="0.0.0.0", port=8050, debug=False)
