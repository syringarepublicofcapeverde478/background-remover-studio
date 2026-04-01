"""Local web API for Background Remover Studio."""

from __future__ import annotations

import io
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image

from background_remover import (
    descontaminar_bordas,
    erosao_alpha,
    estimate_background_color,
    is_artwork_like_image,
    limpar_bordas,
    prepare_export_image,
    processing_profile,
    proteger_fios_de_cabelo,
    refinar_alpha_com_fundo,
    reforcar_detalhes_de_arte,
    sanitizar_rgb_transparente,
    suavizar_borda_humana,
    suavizar_serrilhado_alpha,
)

try:
    from rembg import new_session, remove as rembg_remove
except ImportError as exc:  # pragma: no cover - environment issue
    raise RuntimeError("Install dependencies from requirements.txt before running the web app.") from exc


ROOT = Path(__file__).parent
WEB_DIR = ROOT / "webui"
_SESSION = None


def get_session():
    global _SESSION
    if _SESSION is None:
        _SESSION = new_session()
    return _SESSION


def run_pipeline(
    src: Image.Image,
    white_threshold: int = 225,
    edge_cleanup: int = 0,
    hair_protect: bool = True,
) -> Image.Image:
    src = src.convert("RGB")
    buffer = io.BytesIO()
    src.save(buffer, format="PNG")
    data = buffer.getvalue()

    bg_rgb = estimate_background_color(src)
    bg_brightness = float(bg_rgb.mean())
    artwork_mode = is_artwork_like_image(src, bg_rgb)
    erode_size, clean_threshold, edge_radius = processing_profile(src.width, src.height, white_threshold)

    try:
        if not artwork_mode:
            out = rembg_remove(
                data,
                session=get_session(),
                alpha_matting=True,
                alpha_matting_foreground_threshold=240,
                alpha_matting_background_threshold=10,
                alpha_matting_erode_size=erode_size,
            )
        else:
            out = rembg_remove(data, session=get_session())
    except Exception:
        out = rembg_remove(data, session=get_session())

    img = Image.open(io.BytesIO(out)).convert("RGBA")

    if artwork_mode:
        img = reforcar_detalhes_de_arte(src, img, bg_rgb, distance_threshold=26.0)
        img = sanitizar_rgb_transparente(img)
    else:
        img = refinar_alpha_com_fundo(
            src,
            img,
            bg_rgb,
            edge_radius=max(3, edge_radius + 1),
            low=18.0,
            high=92.0,
        )
        if hair_protect:
            img = proteger_fios_de_cabelo(src, img, bg_rgb, edge_radius=max(2, edge_radius))
        sim_thr = 46.0 if bg_brightness < 170.0 else 62.0
        img = descontaminar_bordas(img, bg_rgb, edge_radius=max(2, edge_radius), similarity_threshold=sim_thr)
        if clean_threshold < 255:
            cleanup_thr = clean_threshold if bg_brightness < 170.0 else min(clean_threshold, 212)
            img = limpar_bordas(img, cleanup_thr, edge_radius=edge_radius)
        img = suavizar_borda_humana(src, img, bg_rgb, edge_radius=max(1, edge_radius))
        img = suavizar_serrilhado_alpha(img, edge_radius=max(1, edge_radius), blur_radius=0.72)
        if edge_cleanup > 0:
            img = erosao_alpha(img, edge_cleanup)
        img = sanitizar_rgb_transparente(img)

    return img


app = FastAPI(title="Background Remover Studio API")
app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")


@app.get("/")
def root():
    return FileResponse(WEB_DIR / "index.html")


@app.get("/api/health")
def health():
    return JSONResponse({"ok": True, "app": "Background Remover Studio API"})


@app.post("/api/remove-background")
async def remove_background(
    file: UploadFile = File(...),
    white_threshold: int = Form(225),
    edge_cleanup: int = Form(0),
    hair_protect: bool = Form(True),
    output: str = Form("png"),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    try:
        raw = await file.read()
        src = Image.open(io.BytesIO(raw)).convert("RGB")
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid image file.") from exc

    result = run_pipeline(
        src,
        white_threshold=max(180, min(255, int(white_threshold))),
        edge_cleanup=max(0, min(8, int(edge_cleanup))),
        hair_protect=bool(hair_protect),
    )

    if output not in {"png", "webp", "jpg"}:
        output = "png"

    export_map = {
        "png": ("PNG", "image/png", True, ".png"),
        "webp": ("WEBP", "image/webp", True, ".webp"),
        "jpg": ("JPEG", "image/jpeg", False, ".jpg"),
    }
    pil_format, media_type, transparent, suffix = export_map[output]
    final_img = prepare_export_image(result, transparent)
    out = io.BytesIO()
    save_kwargs = {"quality": 95} if pil_format in {"WEBP", "JPEG"} else {}
    final_img.save(out, format=pil_format, **save_kwargs)
    out.seek(0)

    stem = Path(file.filename).stem or "result"
    headers = {
        "Content-Disposition": f'inline; filename="{stem}_transparent{suffix}"',
        "X-Image-Width": str(final_img.width),
        "X-Image-Height": str(final_img.height),
    }
    return StreamingResponse(out, media_type=media_type, headers=headers)
