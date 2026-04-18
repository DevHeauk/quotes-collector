"""앱 아이콘 PNG 생성 스크립트.

다크 배경(#0f172a) + 큰따옴표 심볼(#38bdf8) + 밑줄 액센트.
Android mipmap 크기별 + Play Store용 512x512 생성.
"""

from PIL import Image, ImageDraw, ImageFont
import os

# 컬러
BG_COLOR = (15, 23, 42)        # #0f172a
PRIMARY_COLOR = (56, 189, 248)  # #38bdf8
ACCENT_COLOR = (56, 189, 248, 102)  # #38bdf8 40% opacity

# Android mipmap 크기
SIZES = {
    "mipmap-mdpi": 48,
    "mipmap-hdpi": 72,
    "mipmap-xhdpi": 96,
    "mipmap-xxhdpi": 144,
    "mipmap-xxxhdpi": 192,
}

PLAY_STORE_SIZE = 512
MASTER_SIZE = 1024


def _draw_quotation_marks(draw: "ImageDraw.Draw", size: int):
    """큰따옴표(") 심볼을 도형으로 직접 그린다."""
    # 두 개의 따옴표 점 + 꼬리
    dot_r = int(size * 0.09)
    tail_len = int(size * 0.13)
    gap = int(size * 0.22)  # 두 따옴표 사이 간격

    cx = size // 2
    cy = int(size * 0.42)

    for offset in [-gap // 2, gap // 2]:
        x = cx + offset
        # 원형 점
        draw.ellipse(
            [x - dot_r, cy - dot_r, x + dot_r, cy + dot_r],
            fill=PRIMARY_COLOR,
        )
        # 꼬리 (커브 느낌의 삼각형)
        tail_points = [
            (x - dot_r * 0.3, cy + dot_r * 0.5),
            (x - dot_r * 1.1, cy + dot_r + tail_len),
            (x + dot_r * 0.5, cy + dot_r * 0.8),
        ]
        draw.polygon(tail_points, fill=PRIMARY_COLOR)

APP_DIR = os.path.join(os.path.dirname(__file__), "..", "app")
RES_DIR = os.path.join(APP_DIR, "android", "app", "src", "main", "res")


def draw_icon(size: int, round_mask: bool = False) -> Image.Image:
    """아이콘 이미지를 생성한다."""
    img = Image.new("RGBA", (size, size), BG_COLOR + (255,))
    draw = ImageDraw.Draw(img)

    # 큰따옴표 두 개를 직접 그리기 (원형 + 꼬리)
    _draw_quotation_marks(draw, size)

    # 밑줄 그리기는 아래에서 처리

    # 밑줄 액센트
    line_y = int(size * 0.72)
    line_x1 = int(size * 0.27)
    line_x2 = int(size * 0.73)
    line_width = max(2, int(size * 0.02))
    accent_img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    accent_draw = ImageDraw.Draw(accent_img)
    accent_draw.line(
        [(line_x1, line_y), (line_x2, line_y)],
        fill=ACCENT_COLOR,
        width=line_width,
    )
    img = Image.alpha_composite(img, accent_img)

    # 라운드 마스크
    if round_mask:
        mask = Image.new("L", (size, size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse([0, 0, size - 1, size - 1], fill=255)
        bg = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        img = Image.composite(img, bg, mask)
    else:
        # 둥근 모서리 (크기의 22%)
        corner_radius = int(size * 0.22)
        mask = Image.new("L", (size, size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=corner_radius, fill=255)
        bg = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        img = Image.composite(img, bg, mask)

    return img


def main():
    # Android mipmap 디렉토리에 저장
    for dir_name, size in SIZES.items():
        dir_path = os.path.join(RES_DIR, dir_name)
        os.makedirs(dir_path, exist_ok=True)

        # 일반 아이콘
        icon = draw_icon(size, round_mask=False)
        icon.save(os.path.join(dir_path, "ic_launcher.png"), "PNG")

        # 라운드 아이콘
        icon_round = draw_icon(size, round_mask=True)
        icon_round.save(os.path.join(dir_path, "ic_launcher_round.png"), "PNG")

        print(f"  {dir_name}: {size}x{size} px")

    # Play Store용 512x512
    docs_dir = os.path.join(os.path.dirname(__file__), "..", "docs")
    os.makedirs(docs_dir, exist_ok=True)
    store_icon = draw_icon(PLAY_STORE_SIZE, round_mask=False)
    store_icon.save(os.path.join(docs_dir, "icon_512.png"), "PNG")
    print(f"  Play Store: 512x512 px")

    # 마스터 1024x1024
    master_icon = draw_icon(MASTER_SIZE, round_mask=False)
    master_icon.save(os.path.join(docs_dir, "icon_1024.png"), "PNG")
    print(f"  Master: 1024x1024 px")

    print("\nDone!")


if __name__ == "__main__":
    main()
