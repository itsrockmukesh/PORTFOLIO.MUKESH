import os
import base64

ROOT_DIR = "/Users/mukeshkumar/PORTFOLIO/Personal"

print("Reading assets for standalone.html bundle...")
with open(os.path.join(ROOT_DIR, "dots.bin"), "rb") as f:
    dots_b64 = base64.b64encode(f.read()).decode("ascii")

with open(os.path.join(ROOT_DIR, "photo_cutout.png"), "rb") as f:
    photo_b64 = base64.b64encode(f.read()).decode("ascii")
photo_data_url = f"data:image/png;base64,{photo_b64}"

with open(os.path.join(ROOT_DIR, "anton.woff2"), "rb") as f:
    font_b64 = base64.b64encode(f.read()).decode("ascii")
font_data_url = f"data:font/woff2;base64,{font_b64}"

with open(os.path.join(ROOT_DIR, "three.min.js"), "r", encoding="utf-8") as f:
    three_js_code = f.read()

# Load index.html template and adapt for embedded assets
with open(os.path.join(ROOT_DIR, "index.html"), "r", encoding="utf-8") as f:
    html_content = f.read()

# Replace font url
html_content = html_content.replace("url('./anton.woff2')", f"url('{font_data_url}')")

# Replace three.min.js script tag with inlined code
html_content = html_content.replace(
    '<script src="./three.min.js"></script>',
    f'<script>\n{three_js_code}\n</script>'
)

# Replace texture loading with data URL
html_content = html_content.replace(
    "const photoTexture = textureLoader.load('./photo_cutout.png');",
    f"const photoTexture = textureLoader.load('{photo_data_url}');"
)

# Replace fetch('./dots.bin') with inlined base64 decoding and simulated progress
embedded_fetch_snippet = f"""
    async function loadDotData() {{
      try {{
        const b64Data = "{dots_b64}";
        const total = b64Data.length;
        
        // Fast base64 decode with smooth visual preloader progress
        let pct = 0;
        const progressTimer = setInterval(() => {{
          pct += 8;
          if (pct > 95) pct = 95;
          const offset = CIRCUMFERENCE - (pct / 100) * CIRCUMFERENCE;
          ringBar.style.strokeDashoffset = offset;
          ringPct.textContent = `${{pct}}%`;
        }}, 20);

        // Decode base64 to binary
        const binaryStr = atob(b64Data);
        const len = binaryStr.length;
        const bytes = new Uint8Array(len);
        for (let i = 0; i < len; i++) {{
          bytes[i] = binaryStr.charCodeAt(i);
        }}

        clearInterval(progressTimer);
        ringBar.style.strokeDashoffset = 0;
        ringPct.textContent = '100%';

        createDotsMesh(bytes.buffer);

        setTimeout(() => {{
          preloader.classList.add('hidden');
          revealBtn.style.opacity = '1';
          revealBtn.style.pointerEvents = 'auto';
          isLoaded = true;
        }}, 400);

      }} catch (err) {{
        console.error("Error loading embedded dot buffer:", err);
        ringPct.textContent = 'Err';
      }}
    }}
"""

# Replace loadDotData function in index.html
start_marker = "async function loadDotData() {"
end_marker = "loadDotData();"
start_idx = html_content.find(start_marker)
end_idx = html_content.find(end_marker, start_idx) + len(end_marker)

html_content = html_content[:start_idx] + embedded_fetch_snippet.strip() + "\n    loadDotData();" + html_content[end_idx:]

standalone_path = os.path.join(ROOT_DIR, "standalone.html")
with open(standalone_path, "w", encoding="utf-8") as f:
    f.write(html_content)

out_size_mb = os.path.getsize(standalone_path) / (1024 * 1024)
print(f"Generated standalone.html: {out_size_mb:.2f} MB")
