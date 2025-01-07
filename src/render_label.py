import math

import cairo
import PIL.Image
import PIL.ImageOps

SURFACE_WIDTH = 32767
SURFACE_HEIGHT = 88
ASCII_BITS = ["0", "1"]
STROKE_WIDTH = 3


def convert_to_png(img, filename):
    # Ensure the image is in grayscale
    img = img.convert("L")  # Convert to grayscale

    # Apply a basic threshold to convert to black and white
    threshold = 128
    img = img.point(lambda p: 255 if p > threshold else 0)

    img = PIL.ImageOps.invert(img)

    # Save the modified image as PNG
    img.save(filename, format="PNG")


def convert_to_pbm(img, filename):
    width, height = img.size

    # Convert image data to a list of ASCII bits.
    data = [ASCII_BITS[bool(val)] for val in img.getdata()]

    # Convert that to 2D list (list of character lists)
    data = [data[offset : offset + width] for offset in range(0, width * height, width)]

    with open(filename, "w", encoding="utf-8") as file:
        file.write("P1\n")
        file.write(f"{width} {height}\n")
        for row in data:
            file.write(" ".join(row) + "\n")


def create_cairo_context(image_size, settings: dict):
    surface_w, surface_h = image_size
    font_name = settings["font"]
    font_size = settings["size"]

    if settings["bold"]:
        weight = cairo.FONT_WEIGHT_BOLD
    else:
        weight = cairo.FONT_WEIGHT_NORMAL

    if settings["italic"]:
        slant = cairo.FONT_SLANT_ITALIC
    else:
        slant = cairo.FONT_SLANT_NORMAL

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, *image_size)
    cr = cairo.Context(surface)
    cr.set_antialias(cairo.Antialias.NONE)
    cr.set_source_rgb(0.0, 0.0, 0.0)
    cr.rectangle(0, 0, surface_w, surface_h)
    cr.fill()

    # setup font
    cr.set_source_rgb(1, 1, 1)
    cr.select_font_face(font_name, slant, weight)
    cr.set_font_size(font_size)

    return cr


def render_text(cr, settings: dict):
    text = settings["text"]
    t_ext = cr.text_extents(text)

    cr.move_to(int(t_ext.x_bearing + 1), -int(t_ext.y_bearing - 1))
    cr.show_text(text)
    cr.stroke()

    if settings["underline"]:
        original_line_width = cr.get_line_width()
        cr.set_line_width(STROKE_WIDTH)
        underline_y = -int(t_ext.y_bearing - 1) + 4
        cr.move_to(int(t_ext.x_bearing + 1), underline_y)
        cr.line_to(int(t_ext.x_bearing + 1 + t_ext.width), underline_y)
        cr.stroke()
        cr.set_line_width(original_line_width)

    if settings["strikethrough"]:
        original_line_width = cr.get_line_width()
        cr.set_line_width(STROKE_WIDTH)
        strikethrough_y = -int(t_ext.y_bearing - 1) - (t_ext.height / 2)
        cr.move_to(int(t_ext.x_bearing + 1), strikethrough_y)
        cr.line_to(int(t_ext.x_bearing + 1 + t_ext.width), strikethrough_y)
        cr.stroke()
        cr.set_line_width(original_line_width)


def crop_rendered_text(cr, text):
    t_ext = cr.text_extents(text)
    surface_w = cr.get_target().get_width()
    surface_h = cr.get_target().get_height()
    x_offset = math.ceil(t_ext.x_bearing)
    x_width = x_offset + math.ceil(t_ext.x_advance)
    y_height = surface_h

    src = PIL.Image.frombytes(
        "RGBA", (surface_w, surface_h), cr.get_target().get_data().tobytes(), "raw"
    )

    mono = src.convert("1")
    return mono.crop((x_offset, 0, x_width, y_height))


def calc_y_offset(cr, text):
    t_ext = cr.text_extents(text)
    return int((cr.get_target().get_height() - math.ceil(t_ext.height)) / 2)


def render_label(settings: dict):
    cairo_context = create_cairo_context((SURFACE_WIDTH, SURFACE_HEIGHT), settings)

    # Render text
    render_text(cairo_context, settings)

    # Crop and center text
    text = settings["text"]
    cropped = crop_rendered_text(cairo_context, text)
    resized = PIL.Image.new("1", cropped.size, 0)

    # Calculate the y offset to center the text
    y_offset = calc_y_offset(cairo_context, text)
    resized.paste(cropped, (0, y_offset))

    # Save the image as a PNG file
    convert_to_png(resized, "preview.png")

    # Rotate the image 90 degrees clockwise
    rot = resized.rotate(270, expand=True)
    convert_to_pbm(rot, "label.pbm")
