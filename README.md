# favicon-maker

یک تصویر مربعِ باکیفیت می‌گیرد و کل ست فاوآیکون یک سایت را با `site.webmanifest`
و تگ‌های `<head>` تحویل می‌دهد.

> Build a complete favicon set (`.ico`, PNG sizes, Apple touch icons, maskable icon),
> a `site.webmanifest` and the `<head>` tags from a single square image.
> Python 3 + Pillow.

## نصب

```bash
git clone https://github.com/cybex7/favicon-maker.git
cd favicon-maker
pip install -r requirements.txt
```

فقط Python 3 و Pillow (نسخهٔ ۱۰ به بالا) لازم است.

## استفاده

```bash
python3 favicon_maker.py logo.png \
  --name "نام کامل سایت" \
  --short-name "نام کوتاه" \
  --theme-color "#0b0b0c" \
  --background-color "#0b0b0c"
```

خروجی در پوشهٔ `logo-favicons/` کنار همان فایل ساخته می‌شود (با `-o` عوضش کنید).
با `--zip` یک فایل zip هم می‌سازد.

بعد:

1. همهٔ فایل‌ها به‌جز `head.html` را در ریشهٔ وب سایت بگذارید (مثلاً در CakePHP:
   `app/webroot/`).
2. محتوای `head.html` را در `<head>` بگذارید.

## فایل ورودی

- **مربع باشد.** اگر نباشد، اسکریپت با پیغام خطا متوقف می‌شود (کد خروج ۲)، چون
  آیکون کج و کشیده می‌شد. یا مربعش کنید، یا با `--pad-to-square` آن را وسط یک مربع
  شفاف بگذارید.
- **دست‌کم ۵۱۲ پیکسل.** کوچک‌تر هم کار می‌کند ولی هشدار می‌دهد، چون آیکون‌های بزرگ
  تار می‌شوند.
- PNG، WebP یا JPG. SVG را قبول نمی‌کند؛ اول آن را PNG کنید.

## چه چیزهایی می‌سازد

| فایل                                                 | کاربرد                                                          |
| ---------------------------------------------------- | --------------------------------------------------------------- |
| `favicon.ico`                                        | ۱۶ + ۳۲ + ۴۸، سه فریم واقعی — تب مرورگر                         |
| `favicon-192.png`                                    | `rel="icon"` — گوگل سرچ (مضرب ۴۸) و manifest                    |
| `favicon-512.png`                                    | manifest — نصب در اندروید و صفحهٔ بارگذاری                      |
| `favicon-maskable-512.png`                           | manifest با `purpose: maskable` — اندروید آیکون را گرد/شکل می‌دهد |
| `apple-touch-icon.png`                               | ۱۸۰، مات (بدون شفافیت) — آیفون و آیپد امروزی                    |
| `favicon-57/72/114/120/144/152.png`                  | سایزهای قدیمی iOS                                               |
| `apple-touch-icon-precomposed.png`، `-120x120*.png`  | مسیرهای شناخته‌شده‌ای که بعضی کلاینت‌ها مستقیم سراغشان می‌روند   |
| `site.webmanifest`                                   | اسم، رنگ، زبان و آیکون‌ها برای «Add to Home screen»              |
| `head.html`                                          | تگ‌های `<link>` و `theme-color` برای کپی در `<head>`             |

آیکون‌های Apple و maskable روی `--background-color` مات می‌شوند، چون iOS جای شفاف
را سیاه پر می‌کند و اندروید لبهٔ آیکون maskable را می‌بُرد.

## گزینه‌ها

| گزینه                  | پیش‌فرض       | توضیح                                                     |
| ---------------------- | ------------- | --------------------------------------------------------- |
| `-o, --out`            | `<نام>-favicons` | پوشهٔ خروجی                                            |
| `--name`               | نام فایل      | اسم کامل سایت در manifest                                 |
| `--short-name`         | همان `--name` | اسم کوتاه زیر آیکون در گوشی                               |
| `--theme-color`        | `#ffffff`     | رنگ نوار مرورگر                                           |
| `--background-color`   | `#ffffff`     | صفحهٔ بارگذاری + پس‌زمینهٔ آیکون‌های Apple و maskable       |
| `--lang`, `--dir`      | `fa`, `rtl`   | زبان و جهت manifest                                       |
| `--display`            | `minimal-ui`  | سایت نصب‌شده چطور باز شود (دکمهٔ برگشت و رفرش می‌ماند)      |
| `--start-url`          | `/`           | `start_url` و `scope`                                     |
| `--padding`            | `0`           | حاشیه دور تصویر در آیکون‌های معمولی (۰ تا ۰٫۵)             |
| `--apple-padding`      | `0.08`        | حاشیه در آیکون‌های Apple                                   |
| `--maskable-padding`   | `0.12`        | حاشیه در آیکون maskable                                   |
| `--pad-to-square`      | —             | تصویر غیرمربع را وسط مربع شفاف بگذار به‌جای خطا            |
| `--zip`                | —             | یک zip هم بساز                                            |
| `-f, --force`          | —             | روی پوشهٔ خروجیِ پر بازنویسی کن                            |

`python3 favicon_maker.py --help` همهٔ گزینه‌ها را نشان می‌دهد.
