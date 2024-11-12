import customtkinter
from PIL import ImageGrab, Image, UnidentifiedImageError
import time
import google.generativeai as genai
from pynput import keyboard

# Configure the generative AI model
genai.configure(api_key='AIzaSyBMK1b_wZWqM2eiq11ln0i9uxGOuZ5uX5Q')
model = genai.GenerativeModel("gemini-1.5-flash")

class ScreenshotApp:
    def __init__(self):
        self.root = customtkinter.CTk()
        self.root.title("blingo")
        self.root.geometry("400x400")
        self.root.attributes("-topmost", True)

        # Set the appearance mode to dark
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("blue")

        # Instruction label
        self.label = customtkinter.CTkLabel(self.root, text="Press Shift+C to capture a region of the screen.", font=("Arial", 12))
        self.label.pack(pady=10)

        # Create a text box to show the AI response
        self.response_text = customtkinter.CTkTextbox(self.root, wrap="word", width=570, height=300, font=("Arial", 12))
        self.response_text.pack(pady=10, padx=10)

        # Variables to store coordinates
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0
        self.rect_id = None

        # Listen for the shortcut
        self.listener = keyboard.GlobalHotKeys({
            '<shift>+c': self.start_capture
        })
        self.listener.start()

    def start_capture(self):
        # Hide the main window before starting capture
        self.root.withdraw()

        # Wait a moment to ensure the window is hidden before capture
        time.sleep(0.2)

        # Create a transparent window for drawing the rectangle
        self.capture_window = customtkinter.CTkToplevel(self.root)
        self.capture_window.attributes("-fullscreen", True)
        self.capture_window.attributes("-alpha", 0.3)  # Transparent window
        self.capture_window.attributes("-topmost", True)
        self.capture_window.overrideredirect(True)  # Remove window borders
        self.capture_window.config(cursor="cross")  # Set cursor to cross

        # Create a canvas to draw the rectangle
        self.canvas = customtkinter.CTkCanvas(self.capture_window, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Bind mouse events
        self.capture_window.bind("<ButtonPress-1>", self.on_mouse_down)
        self.capture_window.bind("<B1-Motion>", self.on_mouse_drag)
        self.capture_window.bind("<ButtonRelease-1>", self.on_mouse_up)

    def on_mouse_down(self, event):
        # Record the starting coordinates
        self.start_x = event.x
        self.start_y = event.y
        # Initialize the rectangle
        self.rect_id = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red", width=2)

    def on_mouse_drag(self, event):
        # Update the rectangle while dragging the mouse
        self.end_x = event.x
        self.end_y = event.y

        # Modify the rectangle's size dynamically
        self.canvas.coords(self.rect_id, self.start_x, self.start_y, self.end_x, self.end_y)

    def on_mouse_up(self, event):
        try:
            # Record the end coordinates
            self.end_x = event.x
            self.end_y = event.y

            # Convert coordinates for ImageGrab
            x1 = min(self.start_x, self.end_x)
            y1 = min(self.start_y, self.end_y)
            x2 = max(self.start_x, self.end_x)
            y2 = max(self.start_y, self.end_y)

            # Close the capture window
            self.capture_window.destroy()

            # Wait briefly to ensure the window is closed before capture
            time.sleep(0.1)

            # Capture the screenshot
            self.capture_screenshot(x1, y1, x2, y2)

            # Show the main window again
            self.root.deiconify()

        except Exception as e:
            # If anything goes wrong, show an error message
            customtkinter.CTkMessagebox(title="Error", message=f"An error occurred while capturing: {e}")
            self.root.deiconify()

    def capture_screenshot(self, x1, y1, x2, y2):
        try:
            # Capture the screenshot of the selected area
            screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            filename = f"screenshot_{int(time.time())}.png"
            screenshot.save(filename)
            print(f"Screenshot saved as {filename}")

            # Process the image with the generative model
            self.generate_response(filename)

        except Exception as e:
            # Handle any error in capturing the screenshot
            customtkinter.CTkMessagebox(title="Error", message=f"An error occurred while saving the screenshot: {e}")

    def generate_response(self, filename):
        try:
            # Load the image
            sol = Image.open(filename)

            # Generate the content from the image
            response = model.generate_content(["Which option is correct or the what will be the  answer  in this image for this question?", sol])

            # Check if the response has a text attribute and display it in the Text widget
            if hasattr(response, 'text'):
                self.display_response(response.text)
            else:
                self.display_response("Unable to retrieve the response text from the model.")

        except UnidentifiedImageError:
            # Handle cases where the image cannot be opened
            self.display_response("Unable to open the screenshot image.")
        except Exception as e:
            # Handle any errors during the AI response generation
            customtkinter.CTkMessagebox(title="Error", message=f"An error occurred while generating the response: {e}")

    def display_response(self, response_text):
        try:
            # Clear the previous text
            self.response_text.delete("1.0", "end")

            # Insert the new response into the text box
            self.response_text.insert("1.0", response_text)
            print("AI Response displayed in the window.")

        except Exception as e:
            # Handle any errors in updating the Text widget
            customtkinter.CTkMessagebox(title="Error", message=f"An error occurred while displaying the response: {e}")

    def run(self):
        self.root.mainloop()

# Main application
if __name__ == "__main__":
    print("CustomTkinter is available.")
    print(f"Available attributes: {', '.join(dir(customtkinter))}")
    try:
        app = ScreenshotApp()
        app.run()
    except Exception as e:
        print(f"An error occurred while starting the app: {e}")