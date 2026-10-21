"""Делает легкие копии картинок сайта в формате WebP.

Запуск из папки проекта (нужна библиотека Pillow: pip install pillow):

    python tools/optimize_images.py

Что появляется рядом с исходными файлами:
- images/people/<имя>-360.webp и <имя>-720.webp: верхний квадрат фото,
  ровно та часть, которую показывает карточка;
- images/brochures/<имя>.webp: обложка той же ширины;
- images/logos/gorny.webp: логотип высотой 160 px.

Исходные JPEG и PNG не меняются: их показывают старые браузеры без WebP.
Новое фото человека: положите JPEG в images/people, запустите скрипт
и добавьте карточку в index.html по образцу соседних.
"""

from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / 'images'
QUALITY = 78

# Photos where the person is too small in the top square: (left, top, side) of a closer square
CLOSE_UPS = {
    'kuzmin': (80, 60, 470),
}


def open_image(path, mode):
    # Photos from phones may be stored sideways with a rotation flag
    return ImageOps.exif_transpose(Image.open(path)).convert(mode)


def save_webp(image, path, quality=QUALITY, **options):
    image.save(path, 'WEBP', quality=quality, method=6, **options)
    print(f'{path.relative_to(ROOT)}: {path.stat().st_size // 1024} KB')


def people():
    for source in sorted((IMAGES / 'people').glob('*.jpg')):
        photo = open_image(source, 'RGB')
        if source.stem in CLOSE_UPS:
            left, top, side = CLOSE_UPS[source.stem]
        else:
            side = min(photo.size)
            left, top = (photo.width - side) // 2, 0  # the card shows the top of the photo
        square = photo.crop((left, top, left + side, top + side))
        for size in (360, 720):
            version = square.resize((size, size), Image.LANCZOS) if side > size else square
            save_webp(version, source.with_name(f'{source.stem}-{size}.webp'))


def brochures():
    for source in sorted((IMAGES / 'brochures').glob('*.jpg')):
        save_webp(open_image(source, 'RGB'), source.with_suffix('.webp'))


def logo():
    source = IMAGES / 'logos' / 'gorny.png'
    image = open_image(source, 'RGBA')
    height = 160
    width = round(image.width * height / image.height)
    save_webp(image.resize((width, height), Image.LANCZOS), source.with_suffix('.webp'), quality=90, alpha_quality=100)


if __name__ == '__main__':
    people()
    brochures()
    logo()
