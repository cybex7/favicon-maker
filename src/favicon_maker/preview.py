"""preview.html — shows the icons the way browsers and phones will show them."""

from html import escape

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Favicon preview — {name}</title>
<style>
  :root {{
    --bg: #f6f6f4; --card: #ffffff; --ink: #1d1d1b; --muted: #6b6b66; --line: #e3e3de;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --bg: #151514; --card: #1f1f1d; --ink: #ececea; --muted: #9a9a94; --line: #33332f; }}
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; padding: 32px 16px 64px; background: var(--bg); color: var(--ink);
    font: 15px/1.5 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  }}
  main {{ max-width: 920px; margin: 0 auto; }}
  h1 {{ font-size: 22px; margin: 0 0 4px; }}
  .lead {{ color: var(--muted); margin: 0 0 28px; }}
  section {{
    background: var(--card); border: 1px solid var(--line); border-radius: 14px;
    padding: 20px; margin-bottom: 16px;
  }}
  h2 {{ font-size: 15px; margin: 0 0 4px; }}
  .note {{ color: var(--muted); font-size: 13px; margin: 0 0 16px; }}
  .row {{ display: flex; flex-wrap: wrap; gap: 16px; }}

  /* browser tabs */
  .tabs {{ flex: 1 1 320px; border-radius: 10px; padding: 8px 8px 0; }}
  .tabs.light {{ background: #dfe3e8; }}
  .tabs.dark {{ background: #202124; }}
  .tab {{
    display: flex; align-items: center; gap: 8px; width: 240px; max-width: 100%;
    padding: 9px 12px; border-radius: 8px 8px 0 0; font-size: 13px;
  }}
  .light .tab {{ background: #fff; color: #202124; }}
  .dark .tab {{ background: #35363a; color: #e8eaed; }}
  .tab img {{ width: 16px; height: 16px; flex: none; }}
  .tab span {{ overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }}

  /* search result */
  .serp {{ display: flex; align-items: center; gap: 12px; }}
  .serp .disc {{
    width: 28px; height: 28px; border-radius: 50%; background: #f1f3f4;
    border: 1px solid #dadce0; display: grid; place-items: center; flex: none;
  }}
  .serp .disc img {{ width: 18px; height: 18px; }}
  .serp b {{ display: block; font-weight: 500; font-size: 14px; }}
  .serp small {{ color: var(--muted); }}

  /* phones */
  .phone {{
    width: 228px; height: 300px; padding: 28px 14px; border-radius: 28px; flex: none;
    align-content: start;
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px 10px; justify-items: center;
  }}
  .ios {{ background: linear-gradient(160deg, #3a6186, #89253e); }}
  .android {{ background: linear-gradient(160deg, #1f4037, #99a36f); }}
  .app {{ display: grid; justify-items: center; gap: 4px; width: 56px; }}
  .app img, .app i {{ width: 48px; height: 48px; display: block; }}
  .app i {{ background: rgba(255,255,255,.25); }}
  .app span {{
    color: #fff; font-size: 10px; max-width: 56px; overflow: hidden;
    white-space: nowrap; text-overflow: ellipsis; text-shadow: 0 1px 2px rgba(0,0,0,.4);
  }}
  .ios .app img, .ios .app i {{ border-radius: 22.5%; }}
  .android .app img, .android .app i {{ border-radius: 50%; }}

  /* maskable shapes */
  .shape {{ display: grid; justify-items: center; gap: 6px; font-size: 12px; color: var(--muted); }}
  .shape img {{ width: 96px; height: 96px; display: block; }}
  .safe {{ position: relative; }}
  .safe::after {{
    content: ""; position: absolute; inset: 9.6px; border-radius: 50%;
    border: 1.5px dashed #e5484d;
  }}

  /* splash */
  .splash {{
    width: 170px; height: 300px; border-radius: 28px; flex: none; border: 1px solid var(--line);
    display: grid; place-content: center; justify-items: center; gap: 14px;
  }}
  .splash img {{ width: 96px; height: 96px; }}
  .splash span {{ font-size: 14px; }}

  /* files */
  .files {{ display: flex; flex-wrap: wrap; align-items: flex-end; gap: 14px; }}
  .files figure {{ margin: 0; display: grid; justify-items: center; gap: 4px; }}
  .files img {{ background: repeating-conic-gradient(#ccc 0 25%, #fff 0 50%) 0 0 / 12px 12px; }}
  .files figcaption {{ font-size: 11px; color: var(--muted); }}
  code {{ font-size: 13px; white-space: nowrap; }}
</style>
</head>
<body>
<main>
  <h1>Favicon preview</h1>
  <p class="lead">Check the icons here. Do not upload this file or <code>head.html</code> to your site.</p>

  <section>
    <h2>Browser tab</h2>
    <p class="note">The icon must be clear at 16px, on light and dark tabs.</p>
    <div class="row">
      <div class="tabs light"><div class="tab"><img src="{tab_icon}" alt=""><span{text}>{name}</span></div></div>
      <div class="tabs dark"><div class="tab"><img src="{tab_icon}" alt=""><span{text}>{name}</span></div></div>
    </div>
  </section>

  <section>
    <h2>Google search result</h2>
    <p class="note">Google shows <code>favicon-192.png</code> in a small circle.</p>
    <div class="serp">
      <div class="disc"><img src="favicon-192.png" alt=""></div>
      <div><b{text}>{name}</b><small>https://example.com{start_url}</small></div>
    </div>
  </section>

  <section>
    <h2>Phone</h2>
    <p class="note">iPhone uses <code>apple-touch-icon.png</code>. Android uses the maskable icon.
      The splash screen shows while the installed site opens. It uses <code>--background-color</code>.</p>
    <div class="row">
      <div class="phone ios">
        <div class="app"><i></i></div><div class="app"><img src="apple-touch-icon.png" alt=""><span{text}>{short_name}</span></div><div class="app"><i></i></div>
        <div class="app"><i></i></div><div class="app"><i></i></div><div class="app"><i></i></div>
      </div>
      <div class="phone android">
        <div class="app"><i></i></div><div class="app"><img src="favicon-maskable-512.png" alt=""><span{text}>{short_name}</span></div><div class="app"><i></i></div>
        <div class="app"><i></i></div><div class="app"><i></i></div><div class="app"><i></i></div>
      </div>
      <div class="splash" style="background:{background}">
        <img src="favicon-512.png" alt="">
        <span style="color:{splash_ink}"{text}>{name}</span>
      </div>
    </div>
  </section>

  <section>
    <h2>Android icon shapes</h2>
    <p class="note">Android cuts the maskable icon into a shape. Keep the logo inside the red circle.</p>
    <div class="row">
      <div class="shape"><img src="favicon-maskable-512.png" alt="" style="border-radius:50%">Circle</div>
      <div class="shape"><img src="favicon-maskable-512.png" alt="" style="border-radius:32%">Squircle</div>
      <div class="shape"><img src="favicon-maskable-512.png" alt="" style="border-radius:16%">Rounded square</div>
      <div class="shape"><div class="safe"><img src="favicon-maskable-512.png" alt=""></div>Safe zone</div>
    </div>
  </section>

  <section>
    <h2>All files</h2>
    <p class="note">Checkered areas are transparent.</p>
    <div class="files">
{files}
    </div>
  </section>
</main>
</body>
</html>
"""


def _ink_for(background):
    """Black or white text, whichever reads better on the background colour."""
    v = background.lstrip('#')
    if len(v) == 3:
        v = ''.join(c * 2 for c in v)
    r, g, b = (int(v[i:i + 2], 16) for i in (0, 2, 4))
    return '#000000' if (0.299 * r + 0.587 * g + 0.114 * b) > 150 else '#ffffff'


def preview_html(args, filenames, svg=False):
    images = [f for f in filenames if f.endswith(('.png', '.ico', '.svg'))]
    figures = '\n'.join(
        '      <figure><img src="{0}" alt="" width="{1}" height="{1}"><figcaption>{0}</figcaption></figure>'.format(
            escape(f), 32 if f.endswith(('.ico', '.svg')) else 48
        )
        for f in images
    )
    return PAGE.format(
        name=escape(args.name),
        short_name=escape(args.short_name),
        text=' lang="%s" dir="%s"' % (escape(args.lang, quote=True), escape(args.dir, quote=True)),
        tab_icon='favicon.svg' if svg else 'favicon.ico',
        start_url=escape(args.start_url),
        background=args.background_color,
        splash_ink=_ink_for(args.background_color),
        files=figures,
    )
