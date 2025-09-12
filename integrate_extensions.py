import json
p = r'2_openai/2_lab2.ipynb'
with open(p,'r',encoding='utf-8') as f:
    nb=json.load(f)

def find_index_contains(substr):
    for i,c in enumerate(nb['cells']):
        if substr in ''.join(c.get('source', [])):
            return i
    return None

def move_cell(from_idx, to_idx):
    c=nb['cells'].pop(from_idx)
    if to_idx>from_idx: to_idx -= 1
    nb['cells'].insert(to_idx, c)

# 1) Ensure validate_email_body appears before Email Manager tools
idx_subject_tool = find_index_contains('subject_tool = subject_writer.as_tool')
idx_validate = find_index_contains('def validate_email_body(')
if idx_subject_tool is not None and idx_validate is not None and idx_validate < idx_subject_tool:
    pass
elif idx_subject_tool is not None and idx_validate is not None:
    move_cell(idx_validate, idx_subject_tool+1)

# 2) Ensure send_bulk_html_email appears before handoffs
idx_handoffs = find_index_contains('handoffs = [emailer_agent]')
idx_bulk = find_index_contains('def send_bulk_html_email(')
if idx_handoffs is not None and idx_bulk is not None and idx_bulk > idx_handoffs:
    move_cell(idx_bulk, idx_handoffs)

# 3) After personalizer definition, add personalizer_tool cell if missing
idx_personalizer = find_index_contains('personalizer = Agent(name="Personalization Researcher"')
needs_tool = True
for c in nb['cells']:
    if 'personalizer.as_tool' in ''.join(c.get('source', [])):
        needs_tool=False
        break
if idx_personalizer is not None and needs_tool:
    tool_cell = {
      "cell_type":"code","execution_count":None,"metadata":{},"outputs":[],
      "source":[
        "# Expose personalizer as a tool for orchestration\n",
        "personalizer_tool = personalizer.as_tool(tool_name=\"personalizer\", tool_description=\"Research a URL and produce 2–3 personalization bullets\")\n"
      ]
    }
    nb['cells'].insert(idx_personalizer+1, tool_cell)

# 4) Update Sales Manager tools list to include personalizer_tool
for c in nb['cells']:
    src=''.join(c.get('source', []))
    if 'tools = [tool1, tool2, tool3]' in src:
        new_src = src.replace('tools = [tool1, tool2, tool3]', 'tools = [tool1, tool2, tool3, personalizer_tool]')
        c['source']=[l if l.endswith('\n') else l+'\n' for l in new_src.splitlines()]
        break

# 5) Update Email Manager tools to include validate_email_body
for c in nb['cells']:
    src=''.join(c.get('source', []))
    if 'tools = [subject_tool, html_tool, send_html_email]' in src:
        new_src = src.replace('tools = [subject_tool, html_tool, send_html_email]', 'tools = [subject_tool, html_tool, validate_email_body, send_html_email]')
        c['source']=[l if l.endswith('\n') else l+'\n' for l in new_src.splitlines()]

# 6) Update Email Manager instructions to include validate step
for c in nb['cells']:
    src=''.join(c.get('source', []))
    if 'You are the Email Manager. Given a plain-text email body, you must:' in src and 'validate' not in src:
        new_src = src.replace('1) Call subject_writer to generate a single strong subject', '1) Call subject_writer to generate a single strong subject')
        new_src = new_src.replace('2) Call html_converter', '2) Call validate_email_body to ensure no Subject: line and acceptable length.\n3) Call html_converter')
        new_src = new_src.replace('3) Call send_html_email', '4) Call send_html_email')
        c['source']=[l if l.endswith('\n') else l+'\n' for l in new_src.splitlines()]

# 7) Add Bulk Email Manager agent before handoffs, if missing
has_bulk=False
for c in nb['cells']:
    if 'bulk_emailer_agent' in ''.join(c.get('source', [])):
        has_bulk=True
        break
if not has_bulk and idx_handoffs is not None:
    bulk_cell={
      "cell_type":"code","execution_count":None,"metadata":{},"outputs":[],
      "source":[
        "# Bulk Email Manager: validates, converts to HTML, and bulk sends (dry_run default)\n",
        "bulk_instructions = \"\"\"\n",
        "You are the Bulk Email Manager. Given a plain-text email body and a list of recipients, you must:\n",
        "1) Call subject_writer to generate a single strong subject (6–9 words, non-spammy).\n",
        "2) Call validate_email_body to ensure no Subject: line and acceptable length; use the cleaned body.\n",
        "3) Call html_converter to transform the body into clean, mobile-friendly HTML.\n",
        "4) Call send_bulk_html_email with the subject and HTML. Default to dry_run=True unless explicitly told dry_run=false.\n",
        "Stop after sending.\n",
        "\"\"\"\n",
        "bulk_emailer_agent = Agent(\n",
        "    name=\"Bulk Email Manager\",\n",
        "    instructions=bulk_instructions,\n",
        "    tools=[subject_tool, html_tool, validate_email_body, send_bulk_html_email],\n",
        "    model=\"gpt-5\",\n",
        "    handoff_description=\"Format and bulk send an email to a list\")\n"
      ]
    }
    nb['cells'].insert(idx_handoffs, bulk_cell)
    idx_handoffs += 1

# 8) Update handoffs to include bulk agent
for c in nb['cells']:
    src=''.join(c.get('source', []))
    if 'handoffs = [emailer_agent]' in src:
        new_src = src.replace('handoffs = [emailer_agent]', 'handoffs = [emailer_agent, bulk_emailer_agent]')
        c['source']=[l if l.endswith('\n') else l+'\n' for l in new_src.splitlines()]
        break

# 9) Update Sales Manager instructions to optionally use personalizer and bulk
for c in nb['cells']:
    src=''.join(c.get('source', []))
    if 'sales_manager_instructions = """' in src and 'personalizer' not in src:
        new_block = src.replace('Process:\n1) Generate:', 'Process:\n0) Optional research: If the message contains a line like \"research_url: https://...\", call the personalizer tool with that URL and prepend the returned bullets (verbatim) to the brief you send to writers.\n1) Generate:')
        new_block = new_block.replace('3) Handoff:', '3) Handoff: If the message contains a line like \"recipients: a@x.com,b@y.com\", hand off to Bulk Email Manager and include the recipients; otherwise hand off to Email Manager.\n\n4) Stop: Do not send directly yourself; rely on the Email Manager/Bulk Email Manager to deliver.\n\n3) Handoff:')
        c['source']=[l if l.endswith('\n') else l+'\n' for l in new_block.splitlines()]

with open(p,'w',encoding='utf-8') as f:
    json.dump(nb,f,ensure_ascii=False,indent=1)
print('Integrated extensions into workflow, tools, instructions, and handoffs')
