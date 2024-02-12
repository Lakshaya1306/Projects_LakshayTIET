from qrcode import QRCode, constants
from PIL import Image
qr = QRCode(version=1, error_correction=constants.ERROR_CORRECT_H, box_size=15, border=4)
qr.add_data("https://www.youtube.com/channel/UCSUegRgX-lQRMU81nuVzDQw")
qr.make(fit=True)
img = qr.make_image(fill_color='red', back_color='white')
img.save("hehe.png")

