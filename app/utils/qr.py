import base64
import io

import qrcode


def generate_qr_base64(data : str):
    qr = qrcode.make(data)

    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")

    img_base64 = base64.b64encode(buffer.read()).decode("utf-8")

    return img_base64
