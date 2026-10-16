"""Hosted-model API client. Reads STACKAI_API_URL / STACKAI_API_KEY from the environment or .env.
Thread-safe, in-memory + on-disk response cache keyed by prompt (+ optional nonce for independent resamples)."""
import os, json, time, hashlib, pathlib, threading, requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "results" / "api_cache.jsonl"
_lock = threading.Lock()
_mem = None


def _load_env():
    f = ROOT / ".env"
    if f.exists():
        for line in f.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip("\"'"))


def _extract(resp):
    out = resp.get("outputs", resp)
    if isinstance(out, dict):
        for v in out.values():
            if isinstance(v, str):
                return v
    return json.dumps(resp)


def _cache():
    global _mem
    if _mem is None:
        _mem = {}
        if CACHE.exists():
            for line in CACHE.read_text().splitlines():
                d = json.loads(line)
                _mem[d["k"]] = d["v"]
    return _mem


def call(system, user, nonce="", retries=5):
    _load_env()
    prompt = f"{system}\n\n{user}"
    key = hashlib.sha256((prompt + nonce).encode()).hexdigest()
    with _lock:
        if key in _cache():
            return _cache()[key]
    in_key = os.environ.get("STACKAI_INPUT_KEY", "in-0")
    last = None
    for i in range(retries):
        try:
            r = requests.post(os.environ["STACKAI_API_URL"],
                              headers={"Authorization": f"Bearer {os.environ['STACKAI_API_KEY']}",
                                       "Content-Type": "application/json"},
                              json={"user_id": "whose-side-experiment", in_key: prompt}, timeout=90)
            r.raise_for_status()
            txt = _extract(r.json())
            with _lock:
                CACHE.parent.mkdir(exist_ok=True)
                with CACHE.open("a") as f:
                    f.write(json.dumps({"k": key, "v": txt}) + "\n")
                _cache()[key] = txt
            return txt
        except Exception as e:  # retry on transient errors
            last = e
            time.sleep(2 ** i)
    raise last
