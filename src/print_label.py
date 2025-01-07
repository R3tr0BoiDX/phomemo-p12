import binascii
import io
import logging

from PIL import Image, ImageOps
import serial

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class DummySerial:
    def __init__(self, w):
        self.width = int(w / 8)

    def write(self, x):
        with io.BytesIO(x) as bstrm:
            while bstrm.readable():
                data = bytearray(self.width)
                blen = bstrm.readinto(data)
                if blen == 0:
                    break
                logger.debug(binascii.hexlify(data[0:blen]))
        return 0

    def flush(self):
        return 0

    def read(self):
        return bytearray(0)


def header(port):
    # printer initialization sniffed from Android app "Print Master"
    packets = [
        "1f1138",
        "1f11111f11121f11091f1113",
        "1f1109",
        "1f11191f1111",
        "1f1119",
        "1f1107",
    ]

    for packet in packets:
        port.write(bytes.fromhex(packet))
        port.flush()
        resp = port.read()
        logger.debug(binascii.hexlify(resp))


def preprocess_image(filepath, width):
    with Image.open(filepath) as src:
        src_w, src_h = src.size
        if src_w > width:
            resized = src.crop((0, 0, width, src_h))
        elif src_w < width:
            resized = Image.new("1", (width, src_h), 1)
            resized.paste(src, (width - src_w, 0))
        else:
            resized = src

        return ImageOps.invert(resized.convert("RGB")).convert("1")


def image_to_bytes(image):
    width, height = image.size

    output = bytearray(0)
    for y in range(height):
        byte = 0
        for x in range(width):
            pixel = 1 if image.getpixel((x, y)) != 0 else 0
            byte |= (pixel & 0x1) << (7 - (x % 8))

            if (x % 8) == 7:
                output.append(byte)
                byte = 0

    return output


def print_image(port, image):
    width, height = image.size

    output = bytearray.fromhex("1b401d763000")
    output.extend(int(width / 8).to_bytes(2, byteorder="little"))
    output.extend(height.to_bytes(2, byteorder="little"))

    port.write(output)
    port.flush()
    resp = port.read()
    logger.debug(binascii.hexlify(resp))

    output = image_to_bytes(image)
    port.write(output)
    port.flush()
    resp = port.read()
    logger.debug(binascii.hexlify(resp))


def tape_feed(port):
    output = bytearray.fromhex("1b640d1b640d")

    port.write(output)
    port.flush()
    resp = port.read()
    logger.debug(binascii.hexlify(resp))


def print_label(filename, port_id, dots=96):
    image = preprocess_image(filename, dots)
    if port_id == "dummy":
        port = DummySerial(dots)
    else:
        port = serial.Serial(port, timeout=10)

    header(port)
    print_image(port, image)
    tape_feed(port)

    if port_id != "dummy":
        port.close()
