import io
import zipfile
from pathlib import Path

import streamlit as st
from PIL import Image

WIDTHS = [400, 800, 1200]
WEBP_QUALITY = 80


def resize_to_webp(image: Image.Image, target_width: int) -> bytes:
    """Resize image to target width (keeping aspect ratio) and encode as WebP."""
    ratio = target_width / image.width
    target_height = int(image.height * ratio)
    resized = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    resized.save(buf, format="WEBP", quality=WEBP_QUALITY)
    return buf.getvalue()


def build_zip(variants: dict[int, bytes], stem: str) -> bytes:
    """Pack all WebP variants into a ZIP archive."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for width, data in variants.items():
            zf.writestr(f"{stem}-{width}.webp", data)
    return buf.getvalue()


def html_snippet(stem: str) -> str:
    return f"""\
<img
  src="{stem}-800.webp"
  srcset="
    {stem}-400.webp 400w,
    {stem}-800.webp 800w,
    {stem}-1200.webp 1200w
  "
  sizes="(max-width: 600px) 400px,
         (max-width: 1024px) 800px,
         1200px"
  alt="Optimized image"
/>"""


# ── UI ────────────────────────────────────────────────────────────────

st.set_page_config(page_title="Squish", page_icon="🫠", layout="wide")

st.title("🫠 Squish")
st.caption("Upload one image → get 3 responsive WebP variants + HTML snippet")

uploaded = st.file_uploader(
    "Drop an image here",
    type=["png", "jpg", "jpeg", "webp"],
)

if uploaded:
    image = Image.open(uploaded).convert("RGB")
    stem = Path(uploaded.name).stem

    st.subheader("Original")
    col_orig, col_info = st.columns([2, 1])
    with col_orig:
        st.image(image, use_column_width=True)
    with col_info:
        st.metric("Dimensions", f"{image.width} × {image.height}")
        st.metric("Upload size", f"{uploaded.size / 1024:.1f} KB")

    st.divider()
    st.subheader("Generated variants")

    # Generate variants (skip widths larger than original)
    variants: dict[int, bytes] = {}
    for w in WIDTHS:
        if w <= image.width:
            variants[w] = resize_to_webp(image, w)
        else:
            variants[w] = resize_to_webp(image, image.width)

    cols = st.columns(len(WIDTHS))
    for col, width in zip(cols, WIDTHS):
        data = variants[width]
        with col:
            st.image(data, caption=f"{width}w", use_column_width=True)
            st.caption(f"{len(data) / 1024:.1f} KB")

    st.divider()

    # Download ZIP
    zip_bytes = build_zip(variants, stem)
    st.download_button(
        "⬇️  Download all as ZIP",
        data=zip_bytes,
        file_name=f"{stem}-responsive.zip",
        mime="application/zip",
    )

    # HTML snippet
    st.subheader("HTML snippet")
    st.code(html_snippet(stem), language="html")
