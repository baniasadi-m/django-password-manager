import pyotp
import qrcode
from io import BytesIO
from django.core.files import File
from django.core.files.uploadedfile import InMemoryUploadedFile
import qrcode.image.svg

def generate_totp_secret():
    return pyotp.random_base32()

def get_totp_code(secret):
    totp = pyotp.TOTP(secret)
    return totp.now()

def verify_totp_code(secret, code):
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=2)

def generate_qr_code(username, secret):
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(username, issuer_name="AQRpwm")
    image_factory = qrcode.image.svg.SvgPathImage
    qr = qrcode.QRCode(        version=1,  # Controls the size of the QR Code
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # About 7% or so error correction
        box_size=10,  # Size of the box where the QR code is drawn
        border=4,)

    qr.add_data(totp_uri)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    binary_image = buffer.getvalue()
    # file_buffer = InMemoryUploadedFile(buffer, None, 'qrcode.png', 'image/png', buffer.tell, None)
    return binary_image

# secret = generate_totp_secret()
# totp = get_totp_code(secret)

# print(secret,totp)

# img = generate_qr_code('masoud',secret)

# img.