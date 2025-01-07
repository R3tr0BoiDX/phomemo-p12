import os
import tkinter as tk
from tkinter import PhotoImage, ttk

import matplotlib.font_manager as fm

import src.render_label as renderer
import src.print_label as printer

# List of font sizes to populate the dropdown menu
FONT_SIZES = list(range(10, 13)) + list(range(14, 31, 2)) + [36, 48, 64, 72, "MAX"]
DEFAULT_FONT = ("default", 16)
WINDOW_NAME = "P12 Label Printer text renderer"


def get_available_fonts():
    available_fonts = []
    fonts = fm.findSystemFonts()
    for font in fonts:
        try:
            name = fm.FontProperties(fname=font).get_name()
            available_fonts.append(name)
        except Exception:  # pylint: disable=broad-except
            file_name = os.path.basename(font).split(".")[0]
            print(f'Cant read font "{file_name}"')
            continue

    return sorted(set(available_fonts), key=lambda x: x.lower())


def render():

    if dropdown_var_size.get() == "MAX":
        dropdown_var_size.set(88)

    settings = {
        "text": text_box.get("1.0", "end").strip(),
        "font": dropdown_var_font.get(),
        "size": int(dropdown_var_size.get()),
        "bold": bold_var.get(),
        "italic": italic_var.get(),
        "underline": underline_var.get(),
        "strikethrough": strikethrough_var.get(),
    }
    print(f"Rendering with settings: {settings}")
    renderer.render_label(settings)

    update_preview()


def print_label():
    printer.print_label("preview.png", "dummy")


def on_font_select(_):
    selected_font = dropdown_var_font.get()
    if selected_font:
        text_box.config(font=(selected_font, 16))

    update_font_style()


def update_font_style():
    selected_font = dropdown_var_font.get()
    font_size = 16  # Default font size
    font_styles = []

    # Add styles based on checkbox values
    if bold_var.get():
        font_styles.append("bold")
    if italic_var.get():
        font_styles.append("italic")
    if underline_var.get():
        font_styles.append("underline")

    # Apply selected font and combined styles
    text_box.config(font=(selected_font, font_size) + tuple(font_styles))

    # Handle strikethrough separately
    if strikethrough_var.get():
        text_box.tag_configure("strikethrough", overstrike=True)
        text_box.tag_add("strikethrough", "1.0", "end")  # Apply to all text
    else:
        text_box.tag_remove("strikethrough", "1.0", "end")  # Remove strikethrough


def update_preview():
    new_image = PhotoImage(file="preview.png")
    image_label.config(image=new_image)
    image_label.image = new_image


# region GUI
# region setup
# Create root window
root = tk.Tk()
root.title(WINDOW_NAME)

# Set theme
s = ttk.Style()
s.theme_use("clam")
# endregion

# region text box
# Frame for text box and label to make them in one line
frame = ttk.Frame(root)
frame.pack(pady=10)

# Label for text box
label = ttk.Label(frame, text="Label text:")
label.pack(side="left", padx=5)

# Text Box (increased size and font)
text_box = tk.Text(
    frame,
    height=1,
    width=50,
    font=DEFAULT_FONT,
)
text_box.insert("1.0", "Test text")
text_box.pack(side="left", padx=5)
# endregion

# region checkboxes
# Frame for the checkboxes (Bold, Italic, Underline, Strikethrough)
checkbox_frame = ttk.Frame(root)
checkbox_frame.pack(pady=10)

# Bold style
bold_var = tk.BooleanVar()
bold_checkbox = ttk.Checkbutton(checkbox_frame, text="Bold", variable=bold_var)
bold_checkbox.grid(row=0, column=0, padx=5)
bold_var.trace_add("write", lambda *args: update_font_style())

# Italic style
italic_var = tk.BooleanVar()
italic_checkbox = ttk.Checkbutton(checkbox_frame, text="Italic", variable=italic_var)
italic_checkbox.grid(row=0, column=1, padx=5)
italic_var.trace_add("write", lambda *args: update_font_style())

# Underline style
underline_var = tk.BooleanVar()
underline_checkbox = ttk.Checkbutton(
    checkbox_frame, text="Underline", variable=underline_var
)
underline_checkbox.grid(row=0, column=2, padx=5)
underline_var.trace_add("write", lambda *args: update_font_style())

# Strikethrough style
strikethrough_var = tk.BooleanVar()
strikethrough_checkbox = ttk.Checkbutton(
    checkbox_frame, text="Strikethrough", variable=strikethrough_var
)
strikethrough_checkbox.grid(row=0, column=3, padx=5)
strikethrough_var.trace_add("write", lambda *args: update_font_style())
# endregion

# region dropdowns
# Dropdown Menu for fonts
dropdown_var_font = tk.StringVar()
dropdown_font = ttk.Combobox(
    root,
    textvariable=dropdown_var_font,
    values=get_available_fonts(),
    state="readonly",
)
dropdown_font.bind("<<ComboboxSelected>>", on_font_select)
dropdown_font.pack(pady=10, padx=10)

# Dropdown Menu for font sizes
dropdown_var_size = tk.StringVar()
dropdown_size = ttk.Combobox(
    root, textvariable=dropdown_var_size, values=FONT_SIZES, state="normal"
)
dropdown_size.set("MAX")
dropdown_size.pack(pady=10, padx=10)
# endregion

# region other

# Rendered label preview
image = PhotoImage(file="preview.png")
image_label = ttk.Label(root, image=image)
image_label.pack(pady=10)

# Frame for buttons
button_frame = ttk.Frame(root)
button_frame.pack(pady=10)

# Render Button
submit_btn = ttk.Button(button_frame, text="Render", command=render)
submit_btn.grid(row=0, column=0, padx=5)

# Print Button
submit_btn = ttk.Button(button_frame, text="Print", command=print_label)
submit_btn.grid(row=0, column=1, padx=5)
# endregion
# endregion

root.mainloop()
