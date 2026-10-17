"""
favicon-maker — build a full favicon set + web manifest from one image.

    favicon-maker logo.png --name "My Site" --short-name "Site"

Give it the highest-quality square image you have (SVG, or PNG/WebP/JPG at
512px or larger). It writes a folder with everything a site's web root needs:

    favicon.ico                    16 + 32 + 48, three real frames
    favicon.svg                    only for an SVG source — a sharp icon at any size
    favicon-57/72/114/120/144/152.png   legacy apple-touch-icon sizes
    favicon-192.png                rel="icon" (Google Search) + manifest
    favicon-512.png                manifest (Android install / splash)
    favicon-maskable-512.png       manifest, purpose "maskable" (Android shapes)
    apple-touch-icon.png           180, opaque — current iPhones/iPads
    apple-touch-icon-precomposed.png, apple-touch-icon-120x120(-precomposed).png
                                   well-known paths some clients probe directly
    site.webmanifest
    head.html                      the <link>/<meta> tags to paste into <head>
    preview.html                   open it to check the icons; do not upload it

A non-square source is refused with a message (use --pad-to-square to centre it
on a transparent square instead). A raster source under 512px still works but
prints a warning, because the large icons are then upscaled.
"""

import argparse
import io
import json
import os
import re
import shutil
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit('error: Pillow is not installed. Run:  pip install -r requirements.txt')

from . import __version__
from .preview import preview_html

ICO_SIZES = (16, 32, 48)
LEGACY_APPLE_SIZES = (152, 144, 120, 114, 72)  # linked largest first, as iOS expects
PNG_SIZES = (512, 192, 152, 144, 120, 114, 72, 57)
APPLE_SIZE = 180
RECOMMENDED_MIN = 512
SVG_RENDER_SIZE = 1024  # long side of the raster made from an SVG source
HEX = re.compile(r'^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$')


def fail(msg, code=1):
    print('error: ' + msg, file=sys.stderr)
    sys.exit(code)


def warn(msg):
    print('warning: ' + msg, file=sys.stderr)


def hex_color(value):
    if not HEX.match(value):
        raise argparse.ArgumentTypeError('%r is not a hex colour like #0b0b0c' % value)
    return value.lower()


def fraction(value):
    f = float(value)
    if not 0 <= f < 0.5:
        raise argparse.ArgumentTypeError('must be between 0 and 0.5, got %s' % value)
    return f


def is_svg(path):
    return path.lower().endswith(('.svg', '.svgz'))


def rasterize_svg(path):
    """Render an SVG so its long side is SVG_RENDER_SIZE pixels."""
    try:
        import resvg_py
    except ImportError:
        fail('SVG needs the resvg-py package. Run:  pip install -r requirements.txt')
    try:
        natural = Image.open(io.BytesIO(resvg_py.svg_to_bytes(svg_path=path)))
        w, h = natural.size
        size = {'width': SVG_RENDER_SIZE} if w >= h else {'height': SVG_RENDER_SIZE}
        return Image.open(io.BytesIO(resvg_py.svg_to_bytes(svg_path=path, **size)))
    except ValueError as e:
        fail('cannot read %s as an SVG (%s)' % (path, e))


def load_source(path, pad_to_square):
    if not os.path.isfile(path):
        fail('source not found: %s' % path)
    if is_svg(path):
        im = rasterize_svg(path)
    else:
        try:
            im = Image.open(path)
            im.load()
        except Exception as e:  # Pillow raises several unrelated types here
            fail('cannot read %s as an image (%s)' % (path, e))

    im = im.convert('RGBA')
    w, h = im.size
    if w != h:
        if not pad_to_square:
            fail(
                'the image is not square: %dx%d.\n'
                '  Favicons must be square, so it would be squashed.\n'
                '  Crop it to a square, or re-run with --pad-to-square to centre it\n'
                '  on a transparent %dx%d canvas.' % (w, h, max(w, h), max(w, h)),
                code=2,
            )
        side = max(w, h)
        canvas = Image.new('RGBA', (side, side), (0, 0, 0, 0))
        canvas.alpha_composite(im, ((side - w) // 2, (side - h) // 2))
        warn('image was %dx%d — centred on a transparent %dx%d square.' % (w, h, side, side))
        im = canvas

    if im.width < RECOMMENDED_MIN:
        warn(
            'source is only %dpx. Icons larger than that (up to 512px) will be upscaled '
            'and look soft. Use a %dpx+ original if you have one.' % (im.width, RECOMMENDED_MIN)
        )
    return im


def render(source, size, padding=0.0, background=None):
    """One icon: the source scaled into a size x size canvas, with optional margin and fill."""
    inner = max(1, round(size * (1 - 2 * padding)))
    mark = source.resize((inner, inner), Image.LANCZOS)
    fill = (0, 0, 0, 0) if background is None else background
    icon = Image.new('RGBA', (size, size), fill)
    offset = (size - inner) // 2
    icon.alpha_composite(mark, (offset, offset))
    return icon if background is None else icon.convert('RGB')


def save_png(im, path):
    im.save(path, format='PNG', optimize=True)


def manifest(args):
    return {
        'name': args.name,
        'short_name': args.short_name,
        'lang': args.lang,
        'dir': args.dir,
        'start_url': args.start_url,
        'scope': args.start_url,
        'display': args.display,
        'theme_color': args.theme_color,
        'background_color': args.background_color,
        'icons': [
            {'src': '/favicon-192.png', 'sizes': '192x192', 'type': 'image/png', 'purpose': 'any'},
            {'src': '/favicon-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'any'},
            {
                'src': '/favicon-maskable-512.png',
                'sizes': '512x512',
                'type': 'image/png',
                'purpose': 'maskable',
            },
        ],
    }


def head_html(theme_color, svg=False):
    if svg:
        # sizes="32x32" on the .ico stops Chrome from preferring it over the SVG.
        lines = [
            '<link href="/favicon.ico" type="image/x-icon" rel="icon" sizes="32x32">',
            '<link href="/favicon.svg" type="image/svg+xml" rel="icon">',
        ]
    else:
        lines = ['<link href="/favicon.ico" type="image/x-icon" rel="icon">']
    lines += [
        '<link href="/favicon.ico" type="image/x-icon" rel="shortcut icon">',
        '<link rel="icon" type="image/png" sizes="192x192" href="/favicon-192.png">',
        '<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">',
    ]
    for s in LEGACY_APPLE_SIZES:
        lines.append('<link rel="apple-touch-icon" sizes="%dx%d" href="/favicon-%d.png">' % (s, s, s))
    lines += [
        '<link rel="apple-touch-icon-precomposed" href="/favicon-57.png">',
        '<link rel="manifest" href="/site.webmanifest">',
        '<meta name="theme-color" content="%s">' % theme_color,
    ]
    return '\n'.join(lines) + '\n'


def hex_to_rgba(value):
    v = value.lstrip('#')
    if len(v) == 3:
        v = ''.join(c * 2 for c in v)
    return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def parse_args(argv=None):
    ap = argparse.ArgumentParser(
        prog='favicon-maker',
        description='Build a full favicon set and site.webmanifest from one square image.',
    )
    ap.add_argument('source', help='high-quality square image (SVG, or PNG/WebP/JPG at 512px+)')
    ap.add_argument('-o', '--out', help='output folder (default: <source name>-favicons next to the source)')
    ap.add_argument('--name', help='manifest "name" — the full site name (default: the file name)')
    ap.add_argument('--short-name', help='manifest "short_name" — shown under the home-screen icon (default: --name)')
    ap.add_argument('--lang', default='en', help='manifest language (default: en)')
    ap.add_argument('--dir', default='ltr', choices=('rtl', 'ltr', 'auto'), help='text direction (default: ltr)')
    ap.add_argument('--start-url', default='/', help='manifest start_url and scope (default: /)')
    ap.add_argument(
        '--display',
        default='minimal-ui',
        choices=('browser', 'minimal-ui', 'standalone', 'fullscreen'),
        help='how the installed site opens (default: minimal-ui — keeps back/reload)',
    )
    ap.add_argument('--theme-color', type=hex_color, default='#ffffff', help='browser UI colour (default: #ffffff)')
    ap.add_argument(
        '--background-color',
        type=hex_color,
        default='#ffffff',
        help='splash screen + fill behind the opaque Apple and maskable icons (default: #ffffff)',
    )
    ap.add_argument('--padding', type=fraction, default=0.0, help='margin around the image on the regular icons, 0–0.5 (default: 0)')
    ap.add_argument('--apple-padding', type=fraction, default=0.08, help='margin on the Apple icons (default: 0.08)')
    ap.add_argument('--maskable-padding', type=fraction, default=0.12, help='margin on the maskable icon (default: 0.12)')
    ap.add_argument('--pad-to-square', action='store_true', help='centre a non-square image on a transparent square instead of refusing it')
    ap.add_argument('--zip', action='store_true', help='also write <out>.zip')
    ap.add_argument('-f', '--force', action='store_true', help='overwrite a non-empty output folder')
    ap.add_argument('-V', '--version', action='version', version='%(prog)s ' + __version__)
    return ap.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    stem = os.path.splitext(os.path.basename(args.source))[0]
    out = args.out or os.path.join(os.path.dirname(os.path.abspath(args.source)), stem + '-favicons')
    if os.path.isdir(out) and os.listdir(out) and not args.force:
        fail('%s already exists and is not empty. Use --force to overwrite, or pick another --out.' % out)

    source = load_source(args.source, args.pad_to_square)
    os.makedirs(out, exist_ok=True)

    if not args.name:
        args.name = stem
        warn('no --name given; the manifest uses "%s". Pass --name "Site name" to set it.' % stem)
    args.short_name = args.short_name or args.name

    bg = hex_to_rgba(args.background_color)
    written = []

    def put(name, im):
        path = os.path.join(out, name)
        save_png(im, path)
        written.append(path)

    for size in PNG_SIZES:
        put('favicon-%d.png' % size, render(source, size, args.padding))
    put('favicon-maskable-512.png', render(source, 512, args.maskable_padding, bg))

    # Apple icons are opaque: iOS paints a transparent pixel black.
    apple = render(source, APPLE_SIZE, args.apple_padding, bg)
    apple120 = render(source, 120, args.apple_padding, bg)
    put('apple-touch-icon.png', apple)
    put('apple-touch-icon-precomposed.png', apple)
    put('apple-touch-icon-120x120.png', apple120)
    put('apple-touch-icon-120x120-precomposed.png', apple120)

    # One .ico with three real frames, each rendered at its own size rather
    # than left to Pillow to derive from a single image.
    frames = [render(source, s, args.padding) for s in ICO_SIZES]
    ico = os.path.join(out, 'favicon.ico')
    frames[-1].save(ico, format='ICO', sizes=[f.size for f in frames], append_images=frames[:-1])
    written.append(ico)

    svg = is_svg(args.source) and not args.source.lower().endswith('.svgz')
    if svg:
        svg_path = os.path.join(out, 'favicon.svg')
        shutil.copyfile(args.source, svg_path)
        written.append(svg_path)

    mpath = os.path.join(out, 'site.webmanifest')
    with open(mpath, 'w', encoding='utf-8') as f:
        json.dump(manifest(args), f, ensure_ascii=False, indent=2)
        f.write('\n')
    written.append(mpath)

    hpath = os.path.join(out, 'head.html')
    with open(hpath, 'w', encoding='utf-8') as f:
        f.write(head_html(args.theme_color, svg))
    written.append(hpath)

    ppath = os.path.join(out, 'preview.html')
    with open(ppath, 'w', encoding='utf-8') as f:
        f.write(preview_html(args, [os.path.basename(p) for p in written], svg))
    written.append(ppath)

    print('\n%d files in %s' % (len(written), out))
    for p in written:
        print('  %-42s %6.1f KB' % (os.path.basename(p), os.path.getsize(p) / 1024))

    if args.zip:
        z = shutil.make_archive(out, 'zip', out)
        print('\nzip: %s' % z)

    print(
        '\nNext:\n'
        '  1. Open preview.html to check the icons.\n'
        '  2. Copy every file except head.html and preview.html to the site\'s web root.\n'
        '  3. Paste head.html into <head>.'
    )
