import json
p = r'2_openai/2_lab2.ipynb'
with open(p,'r',encoding='utf-8') as f:
    nb=json.load(f)

def find_idx_contains(substr):
    for i,c in enumerate(nb['cells']):
        if substr in ''.join(c.get('source', [])):
            return i
    return None

def find_all_idx_contains(substr):
    return [i for i,c in enumerate(nb['cells']) if substr in ''.join(c.get('source', []))]

def move_cell(from_idx, to_idx):
    if from_idx is None or to_idx is None: return False
    cell=nb['cells'].pop(from_idx)
    if to_idx>from_idx: to_idx -= 1
    nb['cells'].insert(to_idx, cell)
    return True

# Locate extension cells
idx_ext_header = find_idx_contains('## Extensions: Research, Guardrails, and Mail Merge')
idx_personalizer = find_idx_contains('personalizer = Agent(name="Personalization Researcher"')
idx_personalizer_tool = find_idx_contains('personalizer.as_tool')
idx_orch_demo = find_idx_contains('Demo: research → personalize')
if idx_orch_demo is None:
    idx_orch_demo = find_idx_contains('# Demo: research')

# Find target area: Sales Manager tools cell
idx_sales_tools = find_idx_contains('tools = [tool1, tool2, tool3, personalizer_tool]')
if idx_sales_tools is None:
    idx_sales_tools = find_idx_contains('tools = [tool1, tool2, tool3]')

# Move personalizer and its tool before the Sales Manager tools cell
if idx_personalizer is not None and idx_sales_tools is not None and idx_personalizer > idx_sales_tools:
    move_cell(idx_personalizer, idx_sales_tools)
    # recompute dependent indices after move
    idx_sales_tools = find_idx_contains('tools = [tool1, tool2, tool3, personalizer_tool]') or find_idx_contains('tools = [tool1, tool2, tool3]')
    idx_personalizer = find_idx_contains('personalizer = Agent(name="Personalization Researcher"')

# Ensure personalizer_tool immediately follows personalizer
if idx_personalizer is not None and idx_personalizer_tool is not None and idx_personalizer_tool != idx_personalizer+1:
    move_cell(idx_personalizer_tool, idx_personalizer+1)

# Remove the extension header and orchestrator demo cells if present
to_delete = sorted([i for i in [idx_ext_header, idx_orch_demo] if i is not None], reverse=True)
for i in to_delete:
    nb['cells'].pop(i)

with open(p,'w',encoding='utf-8') as f:
    json.dump(nb,f,ensure_ascii=False,indent=1)
print('Relocated personalizer cells and removed extension header/demo')
