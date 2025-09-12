import json
p = r'2_openai/2_lab2.ipynb'
with open(p, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Find exercise cell index
exercise_idx = None
for i, c in enumerate(nb['cells']):
    if c.get('cell_type') == 'markdown' and any('>Exercise<' in line or 'Exercise</h2>' in line for line in c.get('source', [])):
        exercise_idx = i
        break
assert exercise_idx is not None, 'Exercise cell not found'

intro_md = {
  "cell_type": "markdown",
  "metadata": {},
  "source": [
    "## Extensions: Research, Guardrails, and Mail Merge\n",
    "These cells add: (1) a lightweight research/personalization agent, (2) output guardrails for email bodies, and (3) a mail‑merge sender (dry‑run by default).\n"
  ]
}

research_code = {
  "cell_type": "code",
  "execution_count": None,
  "metadata": {},
  "outputs": [],
  "source": [
    "# Research tool: fetch URL text and a personalization agent\n",
    "from typing import Dict\n",
    "import requests\n",
    "from bs4 import BeautifulSoup\n",
    "from agents import Agent, Runner, function_tool\n",
    "\n",
    "@function_tool\n",
    "def fetch_url_text(url: str) -> Dict[str, str]:\n",
    "    \"\"\"Fetch and extract main text content from a web page.\n",
    "    Returns { 'text': '...'}; keep inputs small to avoid long prompts.\n",
    "    \"\"\"\n",
    "    resp = requests.get(url, timeout=15)\n",
    "    resp.raise_for_status()\n",
    "    soup = BeautifulSoup(resp.text, 'html.parser')\n",
    "    # Remove script/style\n",
    "    for tag in soup(['script','style','noscript']):\n",
    "        tag.decompose()\n",
    "    text = ' '.join(soup.get_text(" ").split())\n",
    "    return { 'text': text[:8000] }\n",
    "\n",
    "personalizer_instructions = \"\"\"\n",
    "You research a prospect and write 2–3 short bullet points we can use to personalize a cold email.\n",
    "- Use ONLY the provided fetched text; do not invent facts.\n",
    "- Focus on recent initiatives, products, metrics, or pains that map to SOC 2 or audit readiness.\n",
    "- Each bullet: <= 18 words, specific and verifiable.\n",
    "- If the text is generic, return neutral, safe bullets.\n",
    "Return bullets only.\n",
    "\"\"\"\n",
    "personalizer = Agent(name=\"Personalization Researcher\", instructions=personalizer_instructions, tools=[fetch_url_text], model=\"gpt-5\")\n"
  ]
}

guardrails_code = {
  "cell_type": "code",
  "execution_count": None,
  "metadata": {},
  "outputs": [],
  "source": [
    "# Guardrails: validate email body before sending\n",
    "from typing import List, Tuple\n",
    "from agents import function_tool\n",
    "\n",
    "def _word_count(s: str) -> int:\n",
    "    return len([w for w in s.replace('\\n',' ').split(' ') if w])\n",
    "\n",
    "@function_tool\n",
    "def validate_email_body(body: str, min_words: int = 50, max_words: int = 180) -> Dict[str, str]:\n",
    "    \"\"\"Ensure no 'Subject:' line and enforce word-count bounds.\n",
    "    Returns {'status': 'ok'|'adjusted', 'body': '...', 'notes': '...'}\n",
    "    \"\"\"\n",
    "    cleaned = body.strip()\n",
    "    if cleaned.lower().startswith('subject:'):\n",
    "        cleaned = '\\n'.join(cleaned.splitlines()[1:]).lstrip()\n",
    "    wc = _word_count(cleaned)\n",
    "    notes = []\n",
    "    if wc < min_words:\n",
    "        notes.append(f\"too short: {wc} words (<{min_words})\")\n",
    "    if wc > max_words:\n",
    "        notes.append(f\"too long: {wc} words (>{max_words})\")\n",
    "        # trim to max words\n",
    "        tokens = [w for w in cleaned.split(' ') if w]\n",
    "        cleaned = ' '.join(tokens[:max_words])\n",
    "    status = 'ok' if not notes else 'adjusted'\n",
    "    return { 'status': status, 'body': cleaned, 'notes': '; '.join(notes) }\n"
  ]
}

mailmerge_code = {
  "cell_type": "code",
  "execution_count": None,
  "metadata": {},
  "outputs": [],
  "source": [
    "# Mail merge sender (dry run by default)\n",
    "from typing import List, Dict\n",
    "import os, sendgrid\n",
    "from sendgrid.helpers.mail import Mail, Email, To, Content\n",
    "from agents import function_tool\n",
    "\n",
    "@function_tool\n",
    "def send_bulk_html_email(recipients: List[str], subject: str, html_body: str, dry_run: bool = True, max_recipients: int = 10) -> Dict[str, str]:\n",
    "    \"\"\"Send the same HTML email to multiple recipients (guarded).\n",
    "    Set dry_run=True to print instead of send. Hard-caps recipients to avoid mistakes.\n",
    "    \"\"\"\n",
    "    if len(recipients) > max_recipients:\n",
    "        return { 'status': 'blocked', 'reason': f'exceeds max_recipients ({max_recipients})' }\n",
    "    if dry_run:\n",
    "        return { 'status': 'dry_run', 'count': str(len(recipients)) }\n",
    "    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))\n",
    "    from_email = Email(os.environ.get('SENDGRID_FROM', 'caliguidpaul@gmail.com'))\n",
    "    for addr in recipients:\n",
    "        to_email = To(addr)\n",
    "        content = Content(\"text/html\", html_body)\n",
    "        mail = Mail(from_email, to_email, subject, content).get()\n",
    "        sg.client.mail.send.post(request_body=mail)\n",
    "    return { 'status': 'sent', 'count': str(len(recipients)) }\n"
  ]
}

orchestrator_demo = {
  "cell_type": "code",
  "execution_count": None,
  "metadata": {},
  "outputs": [],
  "source": [
    "# Demo: research → personalize → draft → validate → convert → (dry‑run) mail‑merge\n",
    "# Assumes sales_agent1/2/3, subject_writer/html_converter agents, and tools exist from earlier cells\n",
    "company_url = 'https://example.com'  # replace during real use\n",
    "prospect_recipients = ['someone@example.com']  # replace with verified recipients during real use\n",
    "\n",
    "# 1) Research personalization bullets\n",
    "bullets = await Runner.run(personalizer, f'Please research and personalize using: {company_url}')\n",
    "personalization = bullets.final_output\n",
    "\n",
    "# 2) Generate 3 drafts with the same brief + personalization\n",
    "brief = 'Write a cold sales email to a Director of Security about SOC 2.'\n",
    "message = brief + '\\n\\nPersonalization bullets to incorporate (verbatim):\\n' + personalization\n",
    "results = await asyncio.gather(\n",
    "    Runner.run(sales_agent1, message),\n",
    "    Runner.run(sales_agent2, message),\n",
    "    Runner.run(sales_agent3, message),\n",
    ")\n",
    "outputs = [r.final_output for r in results]\n",
    "emails_blob = 'Cold sales emails:\\n\\n' + '\\n\\nEmail:\\n\\n'.join(outputs)\n",
    "\n",
    "# 3) Pick best\n",
    "best = await Runner.run(sales_picker, emails_blob)\n",
    "best_body = best.final_output\n",
    "\n",
    "# 4) Validate/adjust length and remove any stray Subject: lines\n",
    "val = validate_email_body(body=best_body)\n",
    "best_body = val['body']\n",
    "\n",
    "# 5) Create subject and HTML\n",
    "subject = (await Runner.run(subject_writer, best_body)).final_output\n",
    "html = (await Runner.run(html_converter, best_body)).final_output\n",
    "\n",
    "# 6) Dry-run bulk send\n",
    "status = send_bulk_html_email(recipients=prospect_recipients, subject=subject, html_body=html, dry_run=True)\n",
    "print(status)\n"
  ]
}

cells_to_insert = [intro_md, research_code, guardrails_code, mailmerge_code, orchestrator_demo]
nb['cells'][exercise_idx:exercise_idx] = cells_to_insert

with open(p, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)
print('Inserted extension cells before the Exercise cell')
