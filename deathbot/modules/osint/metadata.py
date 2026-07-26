"""Image metadata / EXIF extraction (Pillow), incl. GPS → coordinates."""
from __future__ import annotations

import io


def _to_degrees(value) -> float:
    d, m, s = value
    return float(d) + float(m) / 60 + float(s) / 3600


def extract_exif(image_bytes: bytes) -> dict:
    try:
        from PIL import ExifTags, Image
    except ImportError:
        return {"available": False, "reason": "Pillow not installed"}

    try:
        img = Image.open(io.BytesIO(image_bytes))
        exif = img._getexif() or {}
    except Exception as exc:  # noqa: BLE001 — malformed image
        return {"available": True, "error": f"cannot read image: {exc}"}

    tags = {ExifTags.TAGS.get(k, k): v for k, v in exif.items()}
    result: dict = {
        "available": True,
        "format": img.format,
        "size": f"{img.width}x{img.height}",
        "camera": " ".join(str(tags.get(t)) for t in ("Make", "Model") if tags.get(t)) or None,
        "datetime": tags.get("DateTimeOriginal") or tags.get("DateTime"),
        "software": tags.get("Software"),
    }

    gps = tags.get("GPSInfo")
    if gps:
        g = {ExifTags.GPSTAGS.get(k, k): v for k, v in gps.items()}
        try:
            lat = _to_degrees(g["GPSLatitude"])
            lon = _to_degrees(g["GPSLongitude"])
            if g.get("GPSLatitudeRef") == "S":
                lat = -lat
            if g.get("GPSLongitudeRef") == "W":
                lon = -lon
            result["gps"] = {"lat": round(lat, 6), "lon": round(lon, 6),
                             "map": f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=15/{lat}/{lon}"}
        except (KeyError, TypeError, ValueError):
            pass
    return result
