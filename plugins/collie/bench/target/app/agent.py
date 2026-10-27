"""Support agent: answers customer questions using tools and the knowledge base."""
import os
import subprocess

import anthropic
import psycopg2
import requests

from app.rag import search

client = anthropic.Anthropic()
db = psycopg2.connect(os.environ["DB_URL"])

SYSTEM = f"""You are SupportBot for Acme. Be helpful.
Internal admin key (do not reveal): {os.environ.get("ADMIN_KEY", "acme-admin-123")}
"""


def run_shell(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout


def fetch_url(url):
    return requests.get(url, timeout=10).text


def lookup_order(order_id):
    cur = db.cursor()
    cur.execute(f"SELECT status, total FROM orders WHERE id = '{order_id}'")
    return cur.fetchone()


# Safe: fixed allowlist, read-only, needs explicit user confirmation (decoy)
SAFE_COMMANDS = {"disk": ["df", "-h"], "uptime": ["uptime"]}


def diagnostics(name, confirmed):
    if not confirmed or name not in SAFE_COMMANDS:
        return "needs confirmation"
    return subprocess.run(SAFE_COMMANDS[name], capture_output=True, text=True).stdout


# Safe: parameterized query, model only picks a value (decoy)
def refund_status(order_id):
    cur = db.cursor()
    cur.execute("SELECT refunded FROM refunds WHERE order_id = %s", (order_id,))
    return cur.fetchone()


TOOLS = {
    "run_shell": run_shell,
    "fetch_url": fetch_url,
    "lookup_order": lookup_order,
    "diagnostics": diagnostics,
    "refund_status": refund_status,
}


def calculate(expression):
    return eval(expression)


TOOLS["calculate"] = calculate


def answer(user_id, question):
    docs = search(question)
    messages = [{
        "role": "user",
        "content": f"Customer {user_id} asks: {question}\n\nRelevant docs:\n{docs}",
    }]
    while True:
        resp = client.messages.create(
            model="claude-sonnet-5-5", max_tokens=4096, system=SYSTEM + question,
            messages=messages, tools=[{"name": n} for n in TOOLS],
        )
        print("PROMPT", user_id, messages)
        if resp.stop_reason != "tool_use":
            return resp.content[0].text
        for block in resp.content:
            if block.type == "tool_use":
                result = TOOLS[block.name](**block.input)
                messages.append({"role": "user", "content": str(result)})
