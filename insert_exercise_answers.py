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

answers_md = {
  "cell_type": "markdown",
  "metadata": {},
  "source": [
    "**Exercise Answers**\n",
    "- **Design patterns:** Manager–worker orchestration (Sales Manager), Agents‑as‑tools, tool sequencing (Email Manager pipeline), handoffs (delegation to Email Manager), and parallel draft generation with asyncio.\n",
    "- **Workflow → Agent (Anthropic):** Adding tools to an Agent so the model autonomously invokes them, e.g. `sales_manager = Agent(..., tools=tools, ...)`.\n",
    "- **Extensions:** Add mail‑merge sender tool, a research/personalization agent, and stricter guardrails (length, tone, compliance).\n"
  ]
}

hard_md = {
  "cell_type": "markdown",
  "metadata": {},
  "source": [
    "**Hard Challenge: Handle SendGrid replies via Parse Webhook**\n",
    "- **Configure:** In SendGrid, set up Inbound Parse for a subdomain (e.g., `reply.example.com`) to POST to your public URL (use ngrok in dev).\n",
    "- **Receive:** Implement a webhook endpoint to accept multipart form (fields: `from`, `to`, `subject`, `text`, `html`).\n",
    "- **Respond:** Pass the inbound text to an SDR agent to craft a short, helpful reply; send with a reply tool preserving the thread.\n",
    "- **Security:** Lock down the endpoint (allowlist IPs, secret path, or a signature check), validate sender, and sanitize content.\n"
  ]
}

code_src = r'''
# Optional: pip install fastapi uvicorn
# !uv pip install fastapi uvicorn

from fastapi import FastAPI, Request
from typing import Dict
from agents import Agent, Runner, function_tool
import sendgrid, os
from sendgrid.helpers.mail import Mail, Email, To, Content

@function_tool
def send_reply_email(to_email: str, subject: str, body: str) -> Dict[str, str]:
    """Send a reply email to the given address (plain text)."""
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email(os.environ.get('SENDGRID_FROM', 'caliguidpaul@gmail.com'))  # verified sender
    to_email_obj = To(to_email)
    content = Content("text/plain", body)
    mail = Mail(from_email, to_email_obj, subject, content).get()
    sg.client.mail.send.post(request_body=mail)
    return {"status": "sent"}

sdr_instructions = """
You are an SDR continuing an email thread. Read the inbound message and write a concise, helpful reply that advances the conversation.
- Tone: professional, friendly, and helpful.
- Length: <= 120 words.
- Focus: answer questions, propose the next step, and offer two time options; one clear CTA.
- No subject line; body only. Do not include signatures unless provided.
- Do not fabricate facts; ask a clarifying question if needed.
"""

sdr_responder = Agent(name="SDR Responder", instructions=sdr_instructions, model="gpt-5")

app = FastAPI()

@app.post("/sendgrid/inbound")
async def sendgrid_inbound(request: Request):
    # NOTE: Inbound Parse posts multipart/form-data with fields like 'from', 'to', 'subject', 'text', 'html'
    form = await request.form()
    sender = str(form.get('from') or '')
    subject = str(form.get('subject') or '').strip()
    text = str(form.get('text') or '')

    # Very light validation; in production, add IP allowlist / secret path / verification
    to_addr = sender.split('<')[-1].split('>')[0].strip() if '<' in sender else sender
    reply_subject = subject if subject.lower().startswith('re:') else f"Re: {subject}" if subject else "Re: Your email"

    result = await Runner.run(sdr_responder, text)
    body = result.final_output

    # Send the reply back to the original sender
    _ = send_reply_email(to_email=to_addr, subject=reply_subject, body=body)
    return {"ok": True}

# To run locally: uvicorn.run(app, host="0.0.0.0", port=8000)
# Then expose with ngrok and paste the public URL into SendGrid Inbound Parse settings
'''

hard_code = {
  "cell_type": "code",
  "execution_count": None,
  "metadata": {},
  "outputs": [],
  "source": [line + ("\n" if not line.endswith("\n") else "") for line in code_src.splitlines()]
}

# Insert after the exercise cell
nb['cells'][exercise_idx+1:exercise_idx+1] = [answers_md, hard_md, hard_code]

with open(p, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)
print('Inserted answers and hard challenge cells after the Exercise cell')
