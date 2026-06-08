#!/usr/bin/env python3
"""Apply redesign patches to learn.html"""
import re, sys

LEARN = '/app/smartlearn/learn.html'

with open(LEARN, 'r', encoding='utf-8') as f:
    html = f.read()

with open('/app/smartlearn/_new_styles.txt', 'r', encoding='utf-8') as f:
    new_styles = f.read()

with open('/app/smartlearn/_new_upload.html', 'r', encoding='utf-8') as f:
    new_upload = f.read()

# -------- 1) REPLACE STYLE BLOCK --------
# The original style block spans from `<style>` (line 18) to `}` before line 226
# We need to find from `<style>` to the closing `}` of `.btn-primary:hover`
old_styles_pattern = re.compile(
    r"<style>\s*@import url\('https://fonts\.googleapis\.com/css2\?family=Plus\+Jakarta\+Sans:wght@300;400;500;600;700&display=swap'\);.*?\.btn-primary:hover \{\s*opacity: 0\.9;\s*transform: scale\(1\.02\);\s*box-shadow: 0 10px 20px rgba\(59, 130, 246, 0\.3\);\s*\}",
    re.DOTALL
)
m = old_styles_pattern.search(html)
if not m:
    print("ERROR: old styles block not found", file=sys.stderr)
    sys.exit(1)

print(f"Old styles block: lines roughly {html[:m.start()].count(chr(10))+1} to {html[:m.end()].count(chr(10))+1}")
html = html[:m.start()] + new_styles + html[m.end():]
print("✅ Replaced styles block")

# -------- 2) REPLACE UPLOAD + ROLE + HISTORY SECTIONS --------
# Original starts at `<div class="w-full py-16">` (line 811)
# and we need to include everything until end of history `{% endif %}` (line 985)
# But we want to KEEP `<!-- Active Study Mode Flex Container -->` (line 987 onwards)

# Find the exact start and end markers
start_marker = '<div class="w-full py-16">'
end_marker = "        <!-- Active Study Mode Flex Container -->"

start = html.find(start_marker)
if start == -1:
    print("ERROR: start marker not found", file=sys.stderr)
    sys.exit(1)
end = html.find(end_marker, start)
if end == -1:
    print("ERROR: end marker not found", file=sys.stderr)
    sys.exit(1)

# The new_upload content already includes the hero + upload + role + history.
# We must wrap them inside a similar container to keep the rest of the layout working.
# After the new content, we'll close out properly and let `<!-- Active Study Mode Flex Container -->` continue.

# Old block was:
#   <div class="w-full py-16">
#     <div class="max-w-6xl mx-auto px-4">
#       step-upload section
#       camera modal
#       role-setup
#       history
#       <!-- Active Study Mode Flex Container -->  <- this is what we keep onwards
# So we need to replace from `<div class="w-full py-16">` up to (but not including) `<!-- Active Study Mode Flex Container -->`
# And our new content must end with the opening of `<div class="max-w-6xl mx-auto px-4">` left intact
# Actually looking carefully — the legacy code has:
#   <div class="w-full py-16">    (outer)
#     <div class="max-w-6xl mx-auto px-4">   (inner)
#       step-upload
#       camera-modal
#       role-setup
#       history
#       <!-- Active Study Mode Flex Container -->
#       ...
#     </div>
#   </div>
# So `<!-- Active Study Mode Flex Container -->` is INSIDE the .max-w-6xl div.
# Our new content already opens a <div class="w-full pb-16"> and <div class="max-w-6xl mx-auto px-4">,
# but does NOT close them. That's fine because the original closing </div></div> is far below.

html = html[:start] + new_upload + '\n        ' + html[end:]
print("✅ Replaced upload + role + history sections")

# Write back
with open(LEARN, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\n✅ Done. New file size: {len(html)} bytes")
