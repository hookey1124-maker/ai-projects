"""Clash node rotation via REST API for batch eBay scraping."""
import sys
import io
# Fix Windows GBK encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import urllib.request
import json
import time
import random

CLASH_API = "http://127.0.0.1:9098"
GROUP_NAME = "🔰 选择节点"


def _quote(name):
    return urllib.request.quote(name.encode("utf-8"))


def get_current_node():
    """Return the currently selected node name."""
    url = f"{CLASH_API}/proxies/{_quote(GROUP_NAME)}"
    resp = urllib.request.urlopen(url, timeout=5)
    info = json.loads(resp.read())
    return info.get("now", "")


def list_nodes():
    """Return all available node names."""
    url = f"{CLASH_API}/proxies/{_quote(GROUP_NAME)}"
    resp = urllib.request.urlopen(url, timeout=5)
    info = json.loads(resp.read())
    return info.get("all", [])


def switch_node(name):
    """Switch to the given node. Returns True on success."""
    url = f"{CLASH_API}/proxies/{_quote(GROUP_NAME)}"
    data = json.dumps({"name": name}).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="PUT")
    try:
        resp = urllib.request.urlopen(req, timeout=5)
        return resp.status == 204
    except Exception as e:
        print(f"  [WARN] Node switch failed: {e}")
        return False


def get_us_nodes():
    """Return US nodes sorted — these are preferred for eBay."""
    all_nodes = list_nodes()
    us_keywords = ["美国", "us", "usa", "united", "🇺🇸"]
    us = []
    other = []
    for n in all_nodes:
        nl = n.lower()
        if any(kw in nl for kw in us_keywords):
            us.append(n)
        elif n not in ("DIRECT", "REJECT"):
            other.append(n)
    return us, other


def rotate_node(prefer_us=True):
    """
    Rotate to a random node. US nodes are preferred (2x weight).
    Returns the new node name.
    """
    us, other = get_us_nodes()

    if prefer_us and us:
        # US nodes get 2x weight in random selection
        pool = us * 2 + other
    else:
        pool = us + other

    if not pool:
        print("  [WARN] No nodes available")
        return None

    # Avoid selecting the same node
    current = get_current_node()
    candidates = [n for n in pool if n != current]
    if not candidates:
        candidates = pool

    new_node = random.choice(candidates)
    if switch_node(new_node):
        return new_node
    return None


if __name__ == "__main__":
    print(f"Current: {get_current_node()}")
    print(f"Total nodes: {len(list_nodes())}")
    us, other = get_us_nodes()
    print(f"US: {len(us)}, Other: {len(other)}")
    print()
    new = rotate_node()
    if new:
        print(f"Switched to: {new}")
    else:
        print("Switch failed")
