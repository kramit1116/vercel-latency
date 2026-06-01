from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import math

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

with open("q-vercel-latency.json") as f:
    DATA = json.load(f)

def p95(values):
    values = sorted(values)
    k = math.ceil(0.95 * len(values)) - 1
    return values[k]

@app.post("/")
def metrics(payload: dict):
    regions = payload["regions"]
    threshold = payload["threshold_ms"]

    result = {}

    for region in regions:
        rows = [r for r in DATA if r["region"] == region]

        latencies = [r["latency_ms"] for r in rows]
        uptimes = [r["uptime_pct"] for r in rows]

        result[region] = {
            "avg_latency": sum(latencies)/len(latencies),
            "p95_latency": p95(latencies),
            "avg_uptime": sum(uptimes)/len(uptimes),
            "breaches": sum(1 for x in latencies if x > threshold)
        }

    return result
