"""
clean_app.py  –  Remove all orphaned "# ----- Existing session configuration UI -----"
blocks from app.py, keeping only the content inside the proper with st.sidebar: and
with tab_*: blocks.

Strategy:
  Keep every line EXCEPT lines that fall inside a "# ----- Existing..." orphan block
  at the TOP LEVEL (indentation == 0, outside any with tab_).
  An orphan block starts with the comment "# ----- Existing session configuration UI -----"
  and ends just before the next top-level `# ==` or `with tab_` line.
"""

import re

with open("app.py", "r") as f:
    lines = f.readlines()

# Identify line numbers (0-indexed) of orphan block starts
orphan_starts = [i for i, l in enumerate(lines) if l.strip() == "# ----- Existing session configuration UI -----"]
print("Orphan block starts (0-indexed):", orphan_starts)

# For each orphan start, find where it ends (next line that starts a new top-level section)
TOP_LEVEL_RE = re.compile(r'^(# ==|with tab_|$)', re.MULTILINE)

def find_orphan_end(lines, start):
    """Return the index of the first line AFTER the orphan block."""
    for i in range(start + 1, len(lines)):
        l = lines[i]
        if re.match(r'^(# ==|with tab_)', l):
            return i
    return len(lines)

# Build a set of line indices to REMOVE
remove_lines = set()
for start in orphan_starts:
    end = find_orphan_end(lines, start)
    print(f"  Removing lines {start+1}..{end} (inclusive start, exclusive end)")
    for i in range(start, end):
        remove_lines.add(i)

kept = [l for i, l in enumerate(lines) if i not in remove_lines]
print(f"Original lines: {len(lines)}  →  After cleanup: {len(kept)}")

with open("app.py", "w") as f:
    f.writelines(kept)

print("Done.")
