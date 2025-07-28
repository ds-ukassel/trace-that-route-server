from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum
from typing import List, Dict

from fastapi import FastAPI, Query
from pydantic import BaseModel
from trace_that_route import traceroute, Protocol


class ProtocolChoice(str, Enum):
    tcp = "tcp"
    udp = "udp"
    icmp = "icmp"


class TracerouteRequest(BaseModel):
    ips: List[str]

app = FastAPI()
MAX_GLOBAL_THREADS = 32
global_executor = ThreadPoolExecutor(max_workers=MAX_GLOBAL_THREADS)

@app.on_event("shutdown")
def shutdown_event():
    global_executor.shutdown(wait=True)

@app.post("/trace", response_model=Dict[str, dict])
def trace_route(
        request: TracerouteRequest,
        queries: int = Query(3, ge=1, le=5),
        max_steps: int = Query(30, ge=1, le=64),
        protocol: ProtocolChoice = Query("tcp")
):
    protocol_map = {
        "tcp": Protocol.TCP,
        "udp": Protocol.UDP,
        "icmp": Protocol.ICMP
    }

    results = {}

    futures = {
        global_executor.submit(run_trace, ip, queries, max_steps, protocol_map[protocol]): ip
        for ip in request.ips
    }
    for future in as_completed(futures):
        ip, data = future.result()
        results[ip] = data

    return results


def run_trace(ip: str, queries: int = 3, max_steps: int = 30, protocol: Protocol = Protocol.TCP):
    try:
        result = traceroute(ip, queries=queries, max_steps=max_steps, protocol=protocol)
        return ip, result.to_dict()
    except Exception as e:
        return ip, {"error": str(e)}
