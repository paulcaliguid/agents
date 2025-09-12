import json
p = r'2_openai/2_lab2.ipynb'
with open(p,'r',encoding='utf-8') as f:
    nb=json.load(f)

# find exercise cell
exercise_idx=None
for i,c in enumerate(nb['cells']):
    if c.get('cell_type')=='markdown' and any('>Exercise<' in s or 'Exercise</h2>' in s for s in c.get('source', [])):
        exercise_idx=i
        break
assert exercise_idx is not None

instr_src = '''# Second Sales Manager (handoffs-oriented)
sales_manager2_instructions = """
You are the Sales Manager orchestrating three writer agents (sales_agent1/2/3) with optional research, and you hand off to the appropriate email manager to deliver.

Process:
0) Optional research: If the message contains a line like "research_url: https://...", call the personalizer tool with that URL and prepend the returned bullets (verbatim) to the brief you send to writers.
1) Generate: Call all three sales_agent tools with the same brief to produce three distinct drafts. Do not write drafts yourself.
2) Evaluate: Compare drafts for clarity, SOC 2 relevance, specificity/personalization, brevity, and a single, clear CTA. If tied, choose the shorter.
3) Handoff: If the message contains a line like "recipients: a@x.com,b@y.com", hand off to Bulk Email Manager and include the recipients; otherwise hand off to Email Manager.
4) Stop: Do not send directly yourself; rely on the Email Manager/Bulk Email Manager to deliver.

Constraints:
- Do not include a 'Subject:' line in bodies you evaluate or pass.
- Do not modify the chosen draft beyond removing any leading 'Subject:' line, if present.
- Do not fabricate facts; prefer neutral language if information is missing.
"""

sales_manager_2 = Agent(
    name="Sales Manager (handoffs)",
    instructions=sales_manager2_instructions,
    tools=tools,
    handoffs=handoffs,
    model="gpt-5",
)
'''

run_src = '''# Run the second Sales Manager
example = """Send a cold sales email addressed to 'Dear CEO' from Alice
# Optional controls for the manager:
# research_url: https://example.com
# recipients: someone@example.com
"""

with trace("Automated SDR (handoffs)"):
    result = await Runner.run(sales_manager_2, example)
'''

cells=[
  {"cell_type":"code","execution_count":None,"metadata":{},"outputs":[],"source":[l+("\n" if not l.endswith("\n") else "") for l in instr_src.splitlines()]},
  {"cell_type":"code","execution_count":None,"metadata":{},"outputs":[],"source":[l+("\n" if not l.endswith("\n") else "") for l in run_src.splitlines()]},
]

nb['cells'][exercise_idx:exercise_idx]=cells
with open(p,'w',encoding='utf-8') as f:
    json.dump(nb,f,ensure_ascii=False,indent=1)
print('Inserted second Sales Manager before Exercise')
