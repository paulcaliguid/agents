import json
p = r'2_openai/2_lab2.ipynb'
with open(p, 'r', encoding='utf-8') as f:
    nb = json.load(f)

for c in nb['cells']:
    src = ''.join(c.get('source', []))
    if 'sales_picker = Agent(' in src:
        new = ('sales_picker = Agent(\n'
               '    name="sales_picker",\n'
               '    instructions="""\n'
               'You are an impartial evaluator. You receive multiple cold email candidates and must select the single best one.\n'
               'Selection criteria (in order): (1) clarity and credibility, (2) relevance to SOC 2 and audit readiness, (3) specificity and personalization, (4) brevity and readability, (5) a single, clear CTA.\n'
               'If two are equally strong, pick the shorter one.\n'
               'Return exactly the chosen email text and nothing else. Do not add commentary, labels, or quotes.\n'
               '""",\n'
               '    model="gpt-5"\n'
               ')')
        c['source'] = [l+'\n' for l in new.splitlines()]
        break

with open(p, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)
print('Updated sales_picker instructions')
