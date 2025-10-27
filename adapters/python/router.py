import yaml, json
from typing import Any, Dict, List

def load_yaml(p): return yaml.safe_load(open(p,"r",encoding="utf-8"))

REG = load_yaml("tool_definitions/q4.tools.yaml")
ROUT = load_yaml("core/q4.router.yaml")

def coverage(items: List[Dict], req: List[str])->float:
    if not items: return 0.0
    return sum(1 for it in items if all(f in it for f in req))/len(items)

def route_tool(inp: Dict[str,Any]) -> Dict[str,Any] | None:
    tools: List[Dict] = REG["tools"]
    if inp.get("mode")=="force" and inp.get("framework_hint"):
        for t in tools:
            if t["name"] == str(inp["framework_hint"]).lower(): return t
    b = inp.get("buckets") or {}
    if all(k in b and isinstance(b[k], list) and len(b[k])>0 for k in ["S","W","O","T"]):
        return next(t for t in tools if t["name"]=="swot")
    items = inp.get("items") or []
    best=None; best_score=-1.0
    for t in tools:
        req = t.get("detect",{}).get("required_fields")
        if not req: continue
        sc = coverage(items, req)
        if sc>best_score: best=t; best_score=sc
    if best and best_score >= ROUT["routing"]["thresholds"]["coverage"]: return best
    hint = {s.lower() for s in (inp.get("axes_hint") or [])}
    if hint:
        for t in tools:
            ax = (t.get("detect",{}).get("axes") or {})
            if {str(ax.get("x","")).lower(), str(ax.get("y","")).lower()} & hint: return t
    return None