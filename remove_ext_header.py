import json
p = r'2_openai/2_lab2.ipynb'
with open(p,'r',encoding='utf-8') as f:
    nb=json.load(f)

keywords = ['## Extensions: Research, Guardrails, and Mail Merge']
nb['cells'] = [c for c in nb['cells'] if not any(k in ''.join(c.get('source', [])) for k in keywords)]

with open(p,'w',encoding='utf-8') as f:
    json.dump(nb,f,ensure_ascii=False,indent=1)
print('Removed Extensions header cell(s)')
