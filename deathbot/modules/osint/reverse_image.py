"""Reverse image search — builds engine query URLs for a given image URL.

There is no free reverse-image API; the practical OSINT workflow is to hand the
image URL to the major engines. This returns ready-to-open search links.
"""
from __future__ import annotations

from urllib.parse import quote


async def reverse_image(image_url: str) -> dict:
    u = image_url.strip()
    enc = quote(u, safe="")
    return {
        "image_url": u,
        "engines": {
            "Google Lens": f"https://lens.google.com/uploadbyurl?url={enc}",
            "Yandex": f"https://yandex.com/images/search?rpt=imageview&url={enc}",
            "Bing": f"https://www.bing.com/images/search?q=imgurl:{enc}&view=detailv2&iss=sbi",
            "TinEye": f"https://tineye.com/search?url={enc}",
        },
    }
