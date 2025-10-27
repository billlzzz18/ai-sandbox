import fs from "node:fs"; import yaml from "js-yaml";
type Inp = any; type Tool = {name:string;module:string;output:string;detect:any};
const reg = yaml.load(fs.readFileSync("tool_definitions/q4.tools.yaml","utf8")) as any;
const routing = yaml.load(fs.readFileSync("core/q4.router.yaml","utf8")) as any;
const tools: Tool[] = reg.tools;

const hasBuckets = (inp:Inp)=> !!inp.buckets && ["S","W","O","T"].every(k=>Array.isArray(inp.buckets[k])&&inp.buckets[k].length>0);
const coverage = (items:any[], req:string[]) => items.length===0?0:items.filter((it)=>req.every(f=>f in it)).length/items.length;

export function routeTool(inp:Inp): Tool | null {
  if (inp.mode==="force" && inp.framework_hint) { return tools.find(t=>t.name===String(inp.framework_hint).toLowerCase())||null; }
  if (hasBuckets(inp)) { return tools.find(t=>t.name==="swot")||null; }
  const items = inp.items||[];
  let best:Tool|null=null; let bestScore=-1;
  for (const t of tools) {
    const req=t.detect?.required_fields;
    if (!req) continue;
    const sc=coverage(items, req);
    if (sc>bestScore) {best=t; bestScore=sc;}
  }
  if (best && bestScore>=routing.routing.thresholds.coverage) return best;
  const hint = new Set((inp.axes_hint||[]).map((s:string)=>s.toLowerCase()));
  if (hint.size) return tools.find(t=>hint.has(String(t.detect?.axes?.x))||hint.has(String(t.detect?.axes?.y)))||null;
  return null;
}