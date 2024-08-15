from char_led import render_text_to_led_matrix, save
import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser, font, ttk
from PIL import Image, ImageTk
import requests
import os

def on_vertical(event):
    move_fraction = -event.delta / 180  # Adjust this divisor for sensitivity
    current_position = canvas.yview()[0]  # Get current position (fraction)
    new_position = current_position + move_fraction  # Calculate new position
    canvas.yview_moveto(new_position)  # Scroll to the new position

def on_horizontal(event):
    canvas.xview_scroll(-1 * event.delta, 'units')


def extract_rgb_values(image):
    image = image.convert("RGB")  # Ensure image is in RGB mode
    width, height = image.size
    pixels = list(image.getdata())
    
    rgb_values = []
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[y * width + x]
            rgb_values.append((r, g, b))
            #print(f"Pixel at ({x}, {y}): R={r}, G={g}, B={b}")
    g
    return rgb_values

def send_image(file_path):
    url = 'http://192.168.4.1/write'
    
    try:
        with Image.open(file_path) as img:
            # Extract RGB values
            rgb_values = extract_rgb_values(img)

            # Convert image to bytes for sending
            img_bytes = img.tobytes()

            # Send the image bytes to the server
            files = {'plain': img_bytes}
            response = requests.post(url, files=files)
            response_text = response.text
            response_code = response.status_code
            
            # Check if the request was successful
            if response_code != 200:
                raise Exception(f"Failed to send image: HTTP {response_code} - {response_text}")
                
    except Exception as e:
        response_text = f"Error: {str(e)}"
        response_code = None
    
    # Display the response in the GUI or console
    display_response(response_text, response_code)


def browse_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        with Image.open(file_path) as img:
            if img.size == (628, 372):  # Updated size
                display_image_preview(img, False)
                current_file.set(file_path)
            else:
                display_response("Error: Image size must be 628x372 pixels.", None)

def submit_image():
    file_path = current_file.get()
    if file_path:
        send_image(file_path)
    else:
        messagebox.showerror("Error", "No image selected.")

def clear_image():
    current_file.set("")
    image_canvas.delete("all")
    image_canvas.image = None
    file_name_label.config(text="")

def display_image_preview(img, preview):
    img = img.resize((628, 372), Image.LANCZOS)  # Updated size
    img_tk = ImageTk.PhotoImage(img)
    image_canvas.delete("all")
    image_canvas.create_image(0, 0, anchor='nw', image=img_tk)
    image_canvas.config(scrollregion=image_canvas.bbox('all'))
    image_canvas.image = img_tk
    file_name_label.config(text="Image selected")

def display_character_preview(img):
    img_tk = ImageTk.PhotoImage(img)
    character_canvas.delete("all")
    character_canvas.create_image(0, 0, anchor='nw', image=img_tk)
    character_canvas.config(scrollregion=character_canvas.bbox('all'))
    character_canvas.image = img_tk

def display_response(response_text, response_code):
    response_label.config(text=f"Response: {response_text}")
    if response_code == 200:
        input_text_box.delete(0, tk.END)
        messagebox.showinfo("Success", "Request submitted successfully!")
    else:
        messagebox.showerror("Failure", "Request submission failed.")

def submit_text():
    user_input = input_text_box.get()
    if user_input:
        response_code = 200
        if response_code == 200:
            input_text_box.delete(0, tk.END)
            messagebox.showinfo("Success", "Text submitted successfully!")
        else:
            messagebox.showerror("Failure", "Text submission failed.")
    else:
        messagebox.showerror("Failure", "Text submission failed.")

def change_font_size(size):
    try:
        size = int(size)
        display_color = "#FFFFFF"  # White for display in GUI
        input_text_box.config(fg=display_color)
        
        render_color = input_text_box.render_color  # Use the stored render color
        
        result = render_text_to_led_matrix(
            input_text_box.get(),
            "/Users/zhaoze/Desktop/2024/upsoft/xingkai.ttf",
            size,
            (628, 372),  # Updated size
            render_color  # Use render color for the generated image
        )
        directory_path = './char'
        file_path = os.path.join(directory_path, 'preview.png')
        save(result, file_path)

        images = []
        for filename in os.listdir(directory_path):
            if filename.endswith(".png"):
                img = Image.open(os.path.join(directory_path, filename))
                images.append(img)
        
        if images:
            total_height = sum(img.height for img in images)
            max_width = max(img.width for img in images)
            stacked_image = Image.new('RGB', (max_width, total_height), 'white')

            y_offset = 0
            for img in images:
                stacked_image.paste(img, (0, y_offset))
                y_offset += img.height

            display_character_preview(stacked_image)
            stacked_image.save(os.path.join(directory_path, 'stacked_preview.png'))

    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid number for font size.")

def change_font_color():
    color = colorchooser.askcolor()[1]
    if color:
        input_text_box.render_color = color  # Store the render color separately

root = tk.Tk()
root.title("ESP32 Image Uploader")
root.geometry('800x600')

# Create a canvas to hold the entire page
canvas = tk.Canvas(root)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Add a scrollbar for the canvas
scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

canvas.configure(yscrollcommand=scrollbar.set)

# Create a frame to hold all the widgets
scrollable_frame = tk.Frame(canvas)

# Add the frame to the canvas

def update_canvas_window_position(event=None):
    # Calculate new center position for the scrollable_frame
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    
    new_x = canvas_width // 2
    new_y = canvas_height // 2

    # Move the scrollable_frame to the new position
    canvas.coords(window_id, new_x, new_y)

    # Print the new anchoring point (optional)
    # print(f"New anchoring point is {new_x}, {new_y}")

def on_resize(event):
    # Print window dimensions
    # print("Window width and height:", root.winfo_width(), root.winfo_height())
    # Print canvas dimensions
    # print("Canvas width and height:", canvas.winfo_width(), canvas.winfo_height())

    # Update the position of the window inside the canvas
    update_canvas_window_position()

root.bind("<Configure>", on_resize)

window_id = canvas.create_window((canvas.winfo_width()//2, 0), window=scrollable_frame, anchor="center")
# Update the scrollregion of the canvas whenever the frame is resized
scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

# Bind scrolling events for touchpad and mouse wheel
canvas.bind_all('<MouseWheel>', on_vertical)
# canvas.bind_all('<Shift-MouseWheel>', on_horizontal)

current_file = tk.StringVar()

# Configure grid weights to center the content
scrollable_frame.grid_columnconfigure(0, weight=1)
scrollable_frame.grid_columnconfigure(2, weight=1)

# Create the central frame content within the scrollable_frame
central_frame = tk.Frame(scrollable_frame)
central_frame.grid(row=0, column=1, padx=20, pady=10, sticky="n")

# Image Upload Header
upload_header = tk.Label(central_frame, text="Image Upload", font=('Helvetica', 16, 'bold'))
upload_header.grid(row=0, column=0, columnspan=3, pady=5)

# Select, Submit, and Clear Image Buttons
button_frame = tk.Frame(central_frame)
button_frame.grid(row=1, column=0, columnspan=3, pady=5)

select_button = tk.Button(button_frame, text="Select Image", command=browse_file)
select_button.grid(row=0, column=0, padx=5)

submit_image_button = tk.Button(button_frame, text="Submit Image", command=submit_image)
submit_image_button.grid(row=0, column=1, padx=5)

clear_image_button = tk.Button(button_frame, text="Clear Image", command=clear_image)
clear_image_button.grid(row=0, column=2, padx=5)

# Scrollable Image Preview with Canvas
image_canvas_frame = tk.Frame(central_frame)
image_canvas_frame.grid(row=2, column=0, columnspan=3, pady=5, sticky="nsew")
image_canvas = tk.Canvas(image_canvas_frame, width=628, height=372, bg='white')  # Updated size
image_canvas.grid(row=0, column=0, sticky="nsew", padx=(40, 0))
scrollbar = tk.Scrollbar(image_canvas_frame, orient="vertical", command=image_canvas.yview)
scrollbar.grid(row=0, column=1, sticky="ns")
image_canvas.configure(yscrollcommand=scrollbar.set)

# Character Preview Canvas
character_canvas_frame = tk.Frame(central_frame)
character_canvas_frame.grid(row=9, column=0, columnspan=3, pady=5, sticky="nsew")
character_canvas = tk.Canvas(character_canvas_frame, width=628, height=372, bg='white')  # Updated size
character_canvas.grid(row=0, column=0, sticky="nsew", padx=(40, 0), pady=(40, 0))
character_scrollbar = tk.Scrollbar(character_canvas_frame, orient="vertical", command=character_canvas.yview)
character_scrollbar.grid(row=0, column=1, sticky="ns", pady=(40, 0))
character_canvas.configure(yscrollcommand=character_scrollbar.set)

file_name_label = tk.Label(central_frame, text="")
file_name_label.grid(row=3, column=0, columnspan=3, pady=5)

response_label = tk.Label(central_frame, text="", font=('Helvetica', 10))
response_label.grid(row=4, column=0, columnspan=3, pady=5)

separator = tk.Frame(central_frame, height=2, bd=1, relief=tk.SUNKEN)
separator.grid(row=5, column=0, columnspan=3, pady=10, sticky="we")

input_header = tk.Label(central_frame, text="Uploading Characters", font=('Helvetica', 16, 'bold'))
input_header.grid(row=6, column=0, columnspan=3, pady=5)

input_text_box = tk.Entry(central_frame, width=50, fg="#FFFFFF")  # Set display color to white
input_text_box.render_color = "#000000"  # Default render color is black
input_text_box.grid(row=7, column=0, columnspan=3, pady=5)

button_frame2 = tk.Frame(central_frame)
button_frame2.grid(row=8, column=0, columnspan=3, pady=5)

submit_button = tk.Button(button_frame2, text="Submit", command=submit_text)
submit_button.grid(row=0, column=0, padx=5)

font_size_label = tk.Label(button_frame2, text="Font Size:")
font_size_label.grid(row=0, column=1, padx=5)

font_size_var = tk.StringVar()
font_size_combobox = ttk.Combobox(button_frame2, textvariable=font_size_var, values=[8, 10, 12, 14, 16, 18, 20, 22, 24], width=5)
font_size_combobox.grid(row=0, column=2, padx=5)

font_size_entry = tk.Entry(button_frame2, textvariable=font_size_var, width=5)
font_size_entry.grid(row=0, column=3, padx=5)

font_size_button = tk.Button(button_frame2, text="Preview", command=lambda: change_font_size(font_size_var.get()))
font_size_button.grid(row=0, column=4, padx=5)

font_color_button = tk.Button(button_frame2, text="Font Color", command=change_font_color)
font_color_button.grid(row=0, column=5, padx=5)

button_frame.columnconfigure(0, weight=1)
button_frame.columnconfigure(1, weight=1)
button_frame.columnconfigure(2, weight=1)

button_frame2.columnconfigure(0, weight=1)
button_frame2.columnconfigure(1, weight=1)
button_frame2.columnconfigure(2, weight=1)
button_frame2.columnconfigure(3, weight=1)
button_frame2.columnconfigure(4, weight=1)
button_frame2.columnconfigure(5, weight=1)

root.mainloop()
