"""STEP: AI / LLM ENGINEER  +  AI FINOPS

Ask a plain-English question. A local Gemma model (via LM Studio, fully offline)
writes the SQL, DuckDB runs it, and the script reports how many tokens it cost.

Usage:
  python ask.py "Which area had the most late deliveries?"
  python ask.py "..." --model <id>        pick a specific LM Studio model
  python ask.py "..." --backend ollama     use Ollama instead
  python ask.py "..." --price-in 0.10 --price-out 0.40 --users 10000
        (prices are USD per 1 million tokens: look up a real cloud model's
         current pricing before the session; nothing is assumed here)
  python ask.py "..." --show-prompt     print the prompt sent to the model

Needs: LM Studio's local server switched on with Gemma downloaded, data/orders_clean.parquet (written by
step 05), and `pip install duckdb`. No internet needed.
"""
import argparse
import json
import re
import sys
import time
import urllib.request

import duckdb

SCHEMA = """Table: orders_clean   (one row per food-delivery order in Agra, Jan-Jun 2026)
  order_id                  TEXT     e.g. 'ORD-00042'
  order_date                DATE
  order_month               TEXT     e.g. '2026-03'
  customer_id               TEXT
  area                      TEXT     UPPERCASE, one of: TAJGANJ, SIKANDRA, KAMLA NAGAR, DAYALBAGH,
                                     SHAHGANJ, CIVIL LINES, SANJAY PLACE, BALKESHWAR
  restaurant                TEXT
  amount_inr                DOUBLE   order value in rupees
  delivery_minutes          INTEGER
  is_late                   INTEGER  1 if delivery took over 45 minutes, else 0
  reordered_within_30_days  INTEGER  1 if the customer ordered again within 30 days, 0 if not,
                                     NULL if the order is too recent to know"""

SYSTEM = f"""You write DuckDB SQL. Answer with ONE SQL query and nothing else:
no explanation, no markdown fences.
{SCHEMA}
Rules: query only orders_clean. Use AVG over a 0/1 column for rates and multiply by 100
for percentages. Round numbers to 1 decimal. Add ORDER BY and LIMIT 10 where sensible."""


def http_json(url, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.loads(resp.read())


def pick_lmstudio_model(host):
    """Use the first Gemma model LM Studio knows about (or the first model at all)."""
    models = [m["id"] for m in http_json(f"{host}/v1/models").get("data", [])]
    if not models:
        sys.exit("LM Studio has no models available. Download Gemma 4 E4B in LM Studio first.")
    gemma = [m for m in models if "gemma" in m.lower()]
    return (gemma or models)[0]


def ask_model(backend, model, question, host):
    """Returns (response_text, tokens_in, tokens_out)."""
    if backend == "lmstudio":
        r = http_json(f"{host}/v1/chat/completions", {
            "model": model,
            "messages": [{"role": "system", "content": SYSTEM},
                         {"role": "user", "content": question}],
            "temperature": 0,
            "stream": False,
        })
        usage = r.get("usage", {})
        return (r["choices"][0]["message"]["content"],
                usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0))
    r = http_json(f"{host}/api/generate", {
        "model": model, "system": SYSTEM, "prompt": question,
        "stream": False, "think": False, "options": {"temperature": 0},
    })
    return r.get("response", ""), r.get("prompt_eval_count", 0), r.get("eval_count", 0)


def extract_sql(text):
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S)
    fenced = re.search(r"```(?:sql)?\s*(.*?)```", text, flags=re.S | re.I)
    if fenced:
        text = fenced.group(1)
    start = re.search(r"\b(WITH|SELECT)\b", text, flags=re.I)
    sql = text[start.start():] if start else text
    return sql.strip().rstrip(";").strip()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("question")
    p.add_argument("--backend", choices=["lmstudio", "ollama"], default="lmstudio")
    p.add_argument("--model", help="model id; LM Studio: auto-picks your Gemma model if omitted")
    p.add_argument("--data", default="data/orders_clean.parquet")
    p.add_argument("--host", help="default: localhost:1234 (LM Studio) or localhost:11434 (Ollama)")
    p.add_argument("--price-in", type=float, help="USD per 1M input tokens (cloud model)")
    p.add_argument("--price-out", type=float, help="USD per 1M output tokens (cloud model)")
    p.add_argument("--users", type=int, default=10000)
    p.add_argument("--per-day", type=int, default=5, help="questions per user per day")
    p.add_argument("--usd-inr", type=float, default=None, help="optional rate to show rupees")
    p.add_argument("--show-prompt", action="store_true")
    a = p.parse_args()

    if a.show_prompt:
        print(SYSTEM, "\n\nQUESTION:", a.question)
        return

    host = a.host or ("http://localhost:1234" if a.backend == "lmstudio" else "http://localhost:11434")
    app = "LM Studio" if a.backend == "lmstudio" else "Ollama"
    try:
        model = a.model or (pick_lmstudio_model(host) if a.backend == "lmstudio" else "gemma4:e4b")
        print(f"\n🧠  Asking {model} (offline, via {app}) ...")
        t0 = time.time()
        text, tin, tout = ask_model(a.backend, model, a.question, host)
    except SystemExit:
        raise
    except Exception as e:
        hint = ("In LM Studio, open the Developer tab and switch the local server on (port 1234)."
                if a.backend == "lmstudio" else "Is the Ollama app running?")
        sys.exit(f"Could not reach {app} at {host}: {e}\n{hint}")
    secs = time.time() - t0

    sql = extract_sql(text)
    print(f"\n📝  SQL written by the model in {secs:.1f}s:\n\n{sql}\n")

    try:
        con = duckdb.connect()
        con.execute(f"CREATE VIEW orders_clean AS SELECT * FROM '{a.data}'")
        print(con.execute(sql).df().to_string(index=False))
    except Exception as e:
        print(f"⚠️  The query failed: {e}")
        print("    Teaching moment: this is why companies still need people who can read SQL.")

    print(f"\n💰  AI FINOPS\n    Tokens in: {tin}   Tokens out: {tout}   Total: {tin + tout}")
    print("    Cost on this laptop: ₹0 (you already paid for the hardware and electricity)")
    if a.price_in is not None and a.price_out is not None:
        per_q = tin / 1e6 * a.price_in + tout / 1e6 * a.price_out
        daily = per_q * a.users * a.per_day
        yearly = daily * 365
        print(f"    On a cloud model at ${a.price_in}/M in, ${a.price_out}/M out:")
        print(f"      one question        ${per_q:.6f}")
        print(f"      {a.users:,} users x {a.per_day}/day  ${daily:,.2f} per day   ${yearly:,.0f} per year")
        if a.usd_inr:
            print(f"      ≈ ₹{yearly * a.usd_inr:,.0f} per year")
    print()


if __name__ == "__main__":
    main()
