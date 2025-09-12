import json
p = r'2_openai/2_lab2.ipynb'
with open(p, 'r', encoding='utf-8') as f:
    nb = json.load(f)

def replace_block_by_var(c, varname, new_block):
    src = ''.join(c['source'])
    key = varname + ' = """'
    start = src.find(key)
    if start == -1:
        return False
    end = src.find('"""', start + len(key))
    if end == -1:
        return False
    before = src[:start]
    after = src[end+3:]
    new_src = before + varname + ' = """\n' + new_block + '\n"""' + after
    c['source'] = [l if l.endswith('\n') else l+'\n' for l in new_src.splitlines()]
    return True

new_sm_handoff = (
    "You are the Sales Manager orchestrating three writer agents (sales_agent1/2/3) and handing off to the Email Manager to format and send. Your objective is to pass exactly one high-quality cold email body via handoff.\n\n"
    "Process:\n"
    "1) Generate: Call all three sales_agent tools with the same brief to produce three distinct drafts. Do not write drafts yourself.\n"
    "2) Evaluate: Compare drafts for clarity, SOC 2 relevance, specificity/personalization, brevity, and a single, clear CTA. If tied, choose the shorter.\n"
    "3) Handoff: Create a handoff to the Email Manager with the chosen draft as the input. Do not send yourself.\n\n"
    "Constraints:\n"
    "- Do not include a 'Subject:' line in the body you pass.\n"
    "- Do not modify the chosen draft beyond removing any leading 'Subject:' line, if present.\n"
    "- Do not fabricate facts; prefer neutral language if information is missing.\n"
)

changed = False
for c in nb['cells']:
    src = ''.join(c.get('source', []))
    if 'sales_manager_instructions = """' in src:
        if replace_block_by_var(c, 'sales_manager_instructions', new_sm_handoff):
            changed = True

if changed:
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    print('Updated sales_manager_instructions in handoff section')
else:
    print('No matching sales_manager_instructions found')
