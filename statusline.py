#!/usr/bin/env python3
import json, sys, time

try:
    data = json.load(sys.stdin)
except Exception:
    print("claude")
    sys.exit(0)

G, Y, R, RESET = "\033[92m", "\033[93m", "\033[91m", "\033[0m"
DIM = "\033[2m"
SEP = f"{DIM} · {RESET}"

def remaining_dot_color(remaining_pct):
    return G if remaining_pct > 50 else Y if remaining_pct > 20 else R

def used_dot_color(used_pct):
    return G if used_pct < 50 else Y if used_pct < 80 else R

# Context dot — green < 50%, yellow < 80%, red >= 80%
ctx = data.get("context_window", {})
pct = ctx.get("used_percentage") or 0
ctx_str = f"{used_dot_color(pct)}●{RESET}\033[1m {pct:.0f}%{RESET}"

# Friendly model name from statusline JSON's display_name field
model_obj = data.get("model", {})
if isinstance(model_obj, dict):
    friendly = model_obj.get("display_name") or model_obj.get("id", "")
else:
    friendly = str(model_obj)

max_ctx = ctx.get("context_window_size")
if max_ctx:
    size_str = f"{max_ctx // 1_000_000}M" if max_ctx >= 1_000_000 else f"{max_ctx // 1000}k"
    friendly = f"{friendly} ({size_str})"

effort_obj = data.get("effort")
if isinstance(effort_obj, dict) and effort_obj.get("level"):
    friendly = f"{friendly} [{effort_obj['level']}]"

def fmt_reset(rl):
    resets_at = rl.get("resets_at")
    used = rl.get("used_percentage")
    if resets_at is None or used is None:
        return None
    secs = max(0, int(resets_at - time.time()))
    d, rem = divmod(secs, 86400)
    h, rem = divmod(rem, 3600)
    m = rem // 60
    if d:
        countdown = f"{d}d {h}h"
    elif h:
        countdown = f"{h}h {m:02d}m"
    else:
        countdown = f"{m}m"
    c = used_dot_color(used)
    return f"{c}●{RESET}\033[1m {used:.0f}%{RESET} ({countdown})"

rate = data.get("rate_limits", {})
rl_parts = [s for s in [fmt_reset(rate.get("five_hour", {})), fmt_reset(rate.get("seven_day", {}))] if s]

parts = [ctx_str, f"\033[1m{friendly}{RESET}"] + rl_parts

print(SEP.join(parts))
