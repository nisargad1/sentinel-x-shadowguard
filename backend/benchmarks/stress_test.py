import time
import json
import statistics
import concurrent.futures
from typing import List, Dict, Any
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8000"

def run_stress_benchmark(total_requests: int = 100, concurrency: int = 15):
    """
    Executes a high-concurrency multi-threaded load test against the live gateway.
    Measures throughput (RPS), error rates, and percentile latencies (P50, P90, P95, P99).
    Uses pure Python standard library for zero-dependency portability.
    """
    print("=" * 75)
    print("SENTINEL-X SmartGuard -- Scalability & High-Throughput Stress Benchmark")
    print(f"Target: {BASE_URL} | Total Requests: {total_requests} | Concurrency: {concurrency}")
    print("=" * 75)

    payloads = [
        # Type A: Authorized Document Access (ALLOW)
        {
            "workspace_id": "ws-default",
            "agent_id": "finance-analyst-agent",
            "user_intent": "Summarize Q3 financial report",
            "tool_name": "read_demo_file",
            "action_name": "read",
            "parameters": {"filename": "report.pdf"},
            "estimated_cost_cents": 2
        },
        # Type B: Redundant Search Query (OPTIMIZE - Cache Hit)
        {
            "workspace_id": "ws-default",
            "agent_id": "market-research-agent",
            "user_intent": "Analyze competitor tier pricing",
            "tool_name": "search_demo_documents",
            "action_name": "query",
            "parameters": {"query": "enterprise tier pricing benchmark"},
            "estimated_cost_cents": 5
        },
        # Type C: Path Traversal (Contained in Honeypot)
        {
            "workspace_id": "ws-default",
            "agent_id": "finance-analyst-agent",
            "user_intent": "System credential probe",
            "tool_name": "read_demo_file",
            "action_name": "read",
            "parameters": {"filename": "../../../etc/passwd"},
            "estimated_cost_cents": 2
        }
    ]

    latencies_ms: List[float] = []
    status_codes: Dict[int, int] = {}
    decisions: Dict[str, int] = {}
    errors = 0

    # Prime cache once
    try:
        data = json.dumps(payloads[1]).encode("utf-8")
        req = urllib.request.Request(
            f"{BASE_URL}/api/v1/actions/propose",
            data=data,
            headers={"Content-Type": "application/json", "X-API-Key": "sg_live_enterprise_default_key_2026"}
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass

    start_bench_time = time.perf_counter()

    def send_request(idx: int):
        payload = payloads[idx % len(payloads)]
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{BASE_URL}/api/v1/actions/propose",
            data=data,
            headers={"Content-Type": "application/json", "X-API-Key": "sg_live_enterprise_default_key_2026"}
        )
        t0 = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                elapsed_ms = (time.perf_counter() - t0) * 1000
                res_body = json.loads(resp.read().decode("utf-8"))
                return resp.status, res_body.get("decision", "UNKNOWN"), elapsed_ms, None
        except urllib.error.HTTPError as e:
            elapsed_ms = (time.perf_counter() - t0) * 1000
            try:
                body = json.loads(e.read().decode("utf-8"))
                return e.code, body.get("decision", "ERROR"), elapsed_ms, str(e)
            except Exception:
                return e.code, "ERROR", elapsed_ms, str(e)
        except Exception as e:
            elapsed_ms = (time.perf_counter() - t0) * 1000
            return 500, "ERROR", elapsed_ms, str(e)

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(send_request, i) for i in range(total_requests)]
        for f in concurrent.futures.as_completed(futures):
            code, dec, lat, err = f.result()
            latencies_ms.append(lat)
            status_codes[code] = status_codes.get(code, 0) + 1
            decisions[dec] = decisions.get(dec, 0) + 1
            if err or code >= 500:
                errors += 1

    total_wall_time = time.perf_counter() - start_bench_time
    rps = round(total_requests / total_wall_time, 2)

    latencies_sorted = sorted(latencies_ms)
    p50 = round(statistics.median(latencies_sorted), 2)
    p90 = round(latencies_sorted[int(len(latencies_sorted) * 0.90)], 2)
    p95 = round(latencies_sorted[int(len(latencies_sorted) * 0.95)], 2)
    p99 = round(latencies_sorted[int(len(latencies_sorted) * 0.99)], 2)
    avg_lat = round(statistics.mean(latencies_sorted), 2)

    print("\nBENCHMARK RESULTS:")
    print(f" -> Completed Requests: {total_requests}")
    print(f" -> Total Duration:     {round(total_wall_time, 3)} seconds")
    print(f" -> Throughput:         {rps} Requests/Second (RPS)")
    print(f" -> Error Rate:         {errors} / {total_requests} ({(errors / total_requests) * 100}%)")
    print("\nLATENCY DISTRIBUTION (Milliseconds):")
    print(f" -> Average: {avg_lat} ms")
    print(f" -> P50:     {p50} ms")
    print(f" -> P90:     {p90} ms")
    print(f" -> P95:     {p95} ms")
    print(f" -> P99:     {p99} ms")
    print("\nDECISION BREAKDOWN:")
    for d, count in decisions.items():
        print(f" -> {d}: {count} ({(count / total_requests) * 100:.1f}%)")
    print("\nSTATUS CODES:")
    for s, count in status_codes.items():
        print(f" -> HTTP {s}: {count}")
    print("=" * 75)

if __name__ == "__main__":
    run_stress_benchmark(total_requests=100, concurrency=15)
