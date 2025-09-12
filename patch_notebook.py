import json, re
p = r'2_openai/2_lab2.ipynb'
with open(p, 'r', encoding='utf-8') as f:
    nb = json.load(f)

def find_cell_index(predicate):
    for i, c in enumerate(nb.get('cells', [])):
        src = ''.join(c.get('source', []))
        if predicate(src):
            return i
    return None

# 1) Overwrite original sales agent instructions cell
idx = find_cell_index(lambda s: 'instructions1 = "You are a sales agent working for ComplAI' in s)
if idx is not None:
    improved = '''instructions1 = """
Role: Senior outbound sales specialist at ComplAI (AI-powered SOC 2 compliance SaaS).
Goal: Write a single cold email body that earns a positive reply or a 15–20 minute call.
Inputs: You may receive prospect context (company, role, pains, industry). If none, write a general version for a mid-market tech company.

Guidelines:
- Tone: professional, clear, credible; avoid hype/jargon.
- Personalization: use given details; do not fabricate. If none, stay neutral.
- Length: 120–160 words, 4–6 short paragraphs, skimmable.
- Value: tie ComplAI to SOC 2 speed, audit readiness, and reduced overhead; include 1 proof point only if provided.
- CTA: propose two time options and invite an alternative; one clear ask only.
- Compliance: no sensitive data, no unverifiable claims; be respectful and lawful.
- Formatting: plain text only; no 'Subject:' line; no markdown; minimal signature (name, company).

Output: Return only the email body ready to send.
"""

instructions2 = """
Role: Engaging outbound sales specialist at ComplAI (AI-powered SOC 2 compliance SaaS).
Goal: Write a single cold email body that feels personable and earns a reply.

Guidelines:
- Tone: warm, light, and tasteful; a single crisp, clever line is fine; never sarcastic or unprofessional.
- Personalization: use given details; do not invent specifics.
- Length: 100–140 words, short paragraphs.
- Clarity: emphasize how ComplAI reduces SOC 2 toil and smooths audits without buzzwords.
- CTA: invite a brief chat with two concrete time options; one clear ask.
- Formatting: plain text only; no 'Subject:' line; no emojis; minimal signature.

Output: Return only the email body ready to send.
"""

instructions3 = """
Role: Efficient outbound sales specialist at ComplAI (AI-powered SOC 2 compliance SaaS).
Goal: Write an ultra-concise cold email that earns a quick yes/no.

Guidelines:
- Tone: concise, direct, respectful; no fluff.
- Length: 60–90 words, 3–4 short paragraphs or a tight list.
- Focus: 1–2 concrete outcomes (faster SOC 2, audit readiness, less overhead).
- CTA: single-line ask with two time options; accept alternatives.
- Formatting: plain text only; no 'Subject:' line; minimal signature.

Output: Return only the email body ready to send.
"""
'''
    nb['cells'][idx]['source'] = [line + ('\n' if not line.endswith('\n') else '') for line in improved.splitlines()]

# 2) Overwrite original Sales Manager instructions cell
idx_sm = find_cell_index(lambda s: 'You are a Sales Manager at ComplAI' in s)
if idx_sm is not None:
    src = ''.join(nb['cells'][idx_sm]['source'])
    start = src.find('instructions = """')
    end = src.find('"""', start + len('instructions = """'))
    if start != -1 and end != -1:
        before = src[:start]
        after = src[end+3:]
        new_block = 'instructions = """\nYou are the Sales Manager orchestrating three writer agents (sales_agent1/2/3) and one delivery tool (send_email). Your objective is to send exactly one high-quality cold email body.\n\nProcess:\n1) Generate: Call all three sales_agent tools with the same brief to produce three distinct drafts. Do not write drafts yourself.\n2) Evaluate: Compare drafts for clarity, relevance to SOC 2 and audit readiness, specificity/personalization, brevity, and a single, clear CTA. If tied, choose the shorter.\n3) Send: Use send_email with the chosen draft as the body. Send exactly one email.\n\nConstraints:\n- Do not include a \"Subject:\" line in bodies you evaluate or send.\n- Do not modify the chosen draft beyond removing any leading \"Subject:\" line, if present.\n- Do not fabricate facts; prefer neutral language if information is missing.\n- After calling send_email successfully, stop.\n"""'
        new_src = before + new_block + after
        nb['cells'][idx_sm]['source'] = [l if l.endswith('\n') else l+'\n' for l in new_src.splitlines()]

# 3) Overwrite original Email Manager instructions cell
idx_em = find_cell_index(lambda s: 'instructions =\\"You are an email formatter and sender' in s or 'instructions =\"You are an email formatter and sender' in s or 'You are an email formatter and sender' in s and 'emailer_agent = Agent(' in s)
if idx_em is not None:
    src = nb['cells'][idx_em]['source']
    joined = ''.join(src)
    pos = joined.find('emailer_agent = Agent(')
    tail = ''
    if pos != -1:
        tail = joined[pos:]
    improved_em = 'instructions = """\nYou are the Email Manager. Given a plain-text email body, you must:\n1) Call subject_writer to generate a single strong subject (6–9 words, non-spammy).\n2) Call html_converter to transform the same body into clean, mobile-friendly HTML.\n3) Call send_html_email with the subject from (1) and HTML from (2).\nRules: Do not write the subject yourself; always use the tools in this order. Do not alter content other than HTML formatting. After send_html_email succeeds, stop.\n"""\n\n' + tail
    nb['cells'][idx_em]['source'] = [l if l.endswith('\n') else l+'\n' for l in improved_em.splitlines()]

# 4) Remove the extra inserted improvement cells
remove_terms = [
    'Improved prompts for sales agents',
    'Improved Email Manager instructions and agent',
    'Improved Sales Manager orchestration',
]
nb['cells'] = [c for c in nb['cells'] if not any(term in ''.join(c.get('source', [])) for term in remove_terms)]

with open(p, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)
print('Updated and cleaned notebook cells')
