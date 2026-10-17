import json
import os

import pytest
from PIL import Image

from favicon_maker.cli import main

SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
    '<rect width="100" height="100" fill="#1b4dff"/></svg>'
)

PNG_FILES = [
    'favicon-512.png', 'favicon-192.png', 'favicon-152.png', 'favicon-144.png',
    'favicon-120.png', 'favicon-114.png', 'favicon-72.png', 'favicon-57.png',
    'favicon-maskable-512.png', 'apple-touch-icon.png', 'apple-touch-icon-precomposed.png',
    'apple-touch-icon-120x120.png', 'apple-touch-icon-120x120-precomposed.png',
]
OTHER_FILES = ['favicon.ico', 'site.webmanifest', 'head.html', 'preview.html']


def make_png(path, size=(512, 512)):
    Image.new('RGBA', size, (200, 30, 30, 255)).save(path)
    return str(path)


def run(*argv):
    main([str(a) for a in argv])


def test_png_source_writes_every_file(tmp_path):
    src = make_png(tmp_path / 'logo.png')
    out = tmp_path / 'out'
    run(src, '-o', out, '--name', 'Test Site')

    assert sorted(os.listdir(out)) == sorted(PNG_FILES + OTHER_FILES)
    for name in PNG_FILES:
        with Image.open(out / name) as im:
            assert im.width == im.height
    assert not (out / 'favicon.svg').exists()


def test_icon_sizes_and_opacity(tmp_path):
    out = tmp_path / 'out'
    run(make_png(tmp_path / 'logo.png'), '-o', out)

    with Image.open(out / 'favicon.ico') as ico:
        assert sorted(ico.info['sizes']) == [(16, 16), (32, 32), (48, 48)]
    with Image.open(out / 'apple-touch-icon.png') as im:
        assert im.size == (180, 180)
        assert im.mode == 'RGB'  # opaque: iOS paints transparency black
    with Image.open(out / 'favicon-maskable-512.png') as im:
        assert im.mode == 'RGB'


def test_default_output_folder_is_next_to_source(tmp_path):
    run(make_png(tmp_path / 'logo.png'))
    assert (tmp_path / 'logo-favicons' / 'favicon.ico').exists()


def test_manifest_defaults(tmp_path):
    out = tmp_path / 'out'
    run(make_png(tmp_path / 'logo.png'), '-o', out)

    m = json.loads((out / 'site.webmanifest').read_text(encoding='utf-8'))
    assert m['name'] == 'logo'
    assert m['short_name'] == 'logo'
    assert m['lang'] == 'en'
    assert m['dir'] == 'ltr'
    assert m['theme_color'] == '#ffffff'
    assert [i['purpose'] for i in m['icons']] == ['any', 'any', 'maskable']


def test_manifest_options(tmp_path):
    out = tmp_path / 'out'
    run(
        make_png(tmp_path / 'logo.png'), '-o', out,
        '--name', 'سایت نمونه', '--short-name', 'نمونه',
        '--lang', 'fa', '--dir', 'rtl', '--theme-color', '#0B0B0C',
    )
    m = json.loads((out / 'site.webmanifest').read_text(encoding='utf-8'))
    assert (m['name'], m['short_name'], m['lang'], m['dir']) == ('سایت نمونه', 'نمونه', 'fa', 'rtl')
    assert m['theme_color'] == '#0b0b0c'
    assert '<meta name="theme-color" content="#0b0b0c">' in (out / 'head.html').read_text()
    assert 'dir="rtl"' in (out / 'preview.html').read_text(encoding='utf-8')


def test_head_html_links_png_set(tmp_path):
    out = tmp_path / 'out'
    run(make_png(tmp_path / 'logo.png'), '-o', out)

    head = (out / 'head.html').read_text()
    assert '<link rel="manifest" href="/site.webmanifest">' in head
    assert 'href="/apple-touch-icon.png"' in head
    assert 'favicon.svg' not in head


def test_svg_source(tmp_path):
    src = tmp_path / 'logo.svg'
    src.write_text(SVG)
    out = tmp_path / 'out'
    run(src, '-o', out)

    assert (out / 'favicon.svg').read_text() == SVG
    head = (out / 'head.html').read_text()
    assert '<link href="/favicon.svg" type="image/svg+xml" rel="icon">' in head
    assert 'sizes="32x32"' in head
    with Image.open(out / 'favicon-512.png') as im:
        assert im.getpixel((256, 256))[:3] == (0x1b, 0x4d, 0xff)


def test_broken_svg_fails(tmp_path, capsys):
    src = tmp_path / 'logo.svg'
    src.write_text('<svg')
    with pytest.raises(SystemExit) as e:
        run(src, '-o', tmp_path / 'out')
    assert e.value.code == 1
    assert 'cannot read' in capsys.readouterr().err


def test_non_square_is_refused(tmp_path, capsys):
    src = make_png(tmp_path / 'wide.png', (600, 300))
    with pytest.raises(SystemExit) as e:
        run(src, '-o', tmp_path / 'out')
    assert e.value.code == 2
    assert 'not square' in capsys.readouterr().err


def test_pad_to_square(tmp_path):
    out = tmp_path / 'out'
    run(make_png(tmp_path / 'wide.png', (600, 300)), '-o', out, '--pad-to-square')
    with Image.open(out / 'favicon-512.png') as im:
        assert im.getpixel((256, 10))[3] == 0  # transparent band above the image
        assert im.getpixel((256, 256))[3] == 255


def test_small_source_warns(tmp_path, capsys):
    run(make_png(tmp_path / 'small.png', (64, 64)), '-o', tmp_path / 'out')
    assert 'upscaled' in capsys.readouterr().err


def test_non_empty_output_needs_force(tmp_path, capsys):
    src = make_png(tmp_path / 'logo.png')
    out = tmp_path / 'out'
    out.mkdir()
    (out / 'old.txt').write_text('x')
    with pytest.raises(SystemExit) as e:
        run(src, '-o', out)
    assert e.value.code == 1
    assert '--force' in capsys.readouterr().err

    run(src, '-o', out, '--force')
    assert (out / 'favicon.ico').exists()


def test_zip(tmp_path):
    out = tmp_path / 'out'
    run(make_png(tmp_path / 'logo.png'), '-o', out, '--zip')
    assert (tmp_path / 'out.zip').exists()


@pytest.mark.parametrize('flag, value', [('--theme-color', 'blue'), ('--padding', '0.6')])
def test_bad_option_values(tmp_path, flag, value):
    with pytest.raises(SystemExit) as e:
        run(make_png(tmp_path / 'logo.png'), flag, value)
    assert e.value.code == 2


def test_missing_source(tmp_path, capsys):
    with pytest.raises(SystemExit):
        run(tmp_path / 'nope.png')
    assert 'not found' in capsys.readouterr().err
