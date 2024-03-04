from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import string
import os
import numpy as np

# random.seed(12)

class Sampler:
    def __init__(
        self, 
        root_dir="mnist_chars/"
    ):
        self.root_dir = root_dir
    
    def get_stroke_bounding_box(self, image):
        """
        Finds the bounding box for the stroke in the image where pixels are less than 255.

        :param image: A PIL Image object in mode 'L'.
        :return: A tuple (left, upper, right, lower) defining the bounding box.
        """
        # Convert the image to a NumPy array
        image_array = np.array(image)

        # Find rows and columns where the image has pixels with values less than 255
        rows = np.any(image_array < 255, axis=1)
        cols = np.any(image_array < 255, axis=0)
        left, right = np.where(cols)[0][[0, -1]]
        top, bottom = np.where(rows)[0][[0, -1]]

        # Return the bounding box: left, upper, right, lower
        return (left, top, right + 1, bottom + 1)
    
    def sample_images_from_characters(self, characters, k=1):
        """
        Samples k images for each specified character from subdirectories.

        :param root_dir: Root directory containing character subfolders.
        :param characters: A list of characters to sample images from.
        :param k: Number of images to sample per character.
        :return: A list of PIL Image objects.
        """
        sampled_images = []

        for character in characters:
            char_dir = os.path.join(self.root_dir, character.upper())  # Ensure character is uppercase
            if not os.path.exists(char_dir):
                print(f"Directory for {character} does not exist. Skipping...")
                continue

            # List all PNG images in the directory
            images = [file for file in os.listdir(char_dir) if file.endswith('.png')]
            if not images:
                print(f"No images found for {character}. Skipping...")
                continue

            # Sample k images from the list
            sampled_filenames = random.sample(images, k=min(k, len(images)))

            # Load and add the sampled images to the list
            for filename in sampled_filenames:
                image_path = os.path.join(char_dir, filename)
                image = Image.open(image_path)

                # Find the bounding box for the stroke
                bbox = self.get_stroke_bounding_box(image)

                # Crop the image to the bounding box to focus on the stroke
                cropped_image = image.crop(bbox)

                sampled_images.append(cropped_image)

        return sampled_images
    
    def sample_color(self, num_colors=1):
        """
        This method samples random colors from the RGB space.
        --------------------------------------------------------------
        :param: None
        :output: colors
        """

        # if is white, resample
        colors = []
        for _ in range(num_colors):
            color = tuple(random.randint(0, 255) for _ in range(3))
            while color == (255, 255, 255):
                color = tuple(random.randint(0, 255) for _ in range(3))
            colors.append(color)

        return colors
    
    def sample_chars(
        self, 
        num_chars=5,
        exclude_chars=["J", "S", "Q"]
    ):
        """
        This method selects random characters from the alphabet.
        --------------------------------------------------------------
        :param: None
        :output: characters
        """
        char_set = [char for char in string.ascii_uppercase if char not in exclude_chars]
        characters = random.choices(char_set, k=num_chars)
        return characters

class CanvasSynthesis:
    def __init__(
        self,
        canvas: Image=None
    ):
        """
        This is the constructor method for the CanvasSynthesis class.
        This class is used to synthesize a canvas for captcha generation.
        Note: the canvas is not transformed in place, but rather a new canvas is returned.
        --------------------------------------------------------------
        :param canvas: A PIL Image object representing the canvas.
        :output: None
        """

        self.canvas = canvas
        if self.canvas is not None:
            self.canvas_size = (self.canvas.width, self.canvas.height)
    
    def __call__(
        self,
        canvas: Image
    ):
        """
        This method is used to update the canvas.
        --------------------------------------------------------------
        :param canvas: A PIL Image object representing the canvas.
        :output: None
        """

        self.canvas = canvas
        self.canvas_size = (self.canvas.width, self.canvas.height)
    
    def _add_pixel_noise_to_canvas(
        self, 
        noise_density=0.05,
    ):
        """
        Adds random pixel noise to the canvas.
        --------------------------------------------------------------
        :param noise_density: The density of noise to add.
        :return: A PIL Image object representing the final canvas.
        """

        # Ensure the canvas is in RGBA mode
        if self.canvas.mode != 'RGBA':
            self.canvas = self.canvas.convert('RGBA')

        # Convert the canvas to a NumPy array
        canvas_array = np.array(self.canvas)

        # Calculate the number of pixels to apply noise to
        total_pixels = canvas_array.shape[0] * canvas_array.shape[1]
        noise_pixels = int(total_pixels * noise_density)

        # Apply noise to a random selection of pixels
        for _ in range(noise_pixels):
            # Randomly choose a pixel
            x = random.randint(0, canvas_array.shape[0] - 1)
            y = random.randint(0, canvas_array.shape[1] - 1)

            # Generate random RGB values for noise
            noise_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 255)

            # Apply the noise
            canvas_array[x, y] = noise_color

        # Convert the NumPy array back to a PIL Image
        self.canvas = Image.fromarray(canvas_array, 'RGBA')

        return self.canvas
    
    def _add_line_noise_to_canvas(
        self,
        num_line_range=(3, 8),
        width=1
    ):
        """
        Adds random lines to the canvas using PIL.
        --------------------------------------------------------------
        :param num_line_range: A tuple specifying the range of the number of lines to add.
        :return: A PIL Image object representing the final canvas with line noise.
        """
        # Ensure the canvas is in RGBA mode
        if self.canvas.mode != 'RGBA':
            self.canvas = self.canvas.convert('RGBA')

        # Prepare to draw on the image
        draw = ImageDraw.Draw(self.canvas)
        num_lines = random.randint(*num_line_range)

        for _ in range(num_lines):
            # Randomly choose line coordinates
            x1, y1 = random.randint(0, self.canvas.width - 1), random.randint(0, self.canvas.height - 1)
            x2, y2 = random.randint(0, self.canvas.width - 1), random.randint(0, self.canvas.height - 1)

            # Generate a random RGB color for the line
            line_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

            # Draw the line
            draw.line([x1, y1, x2, y2], fill=line_color, width=width)
        
        return self.canvas
    
    def _add_circle_noise_to_canvas(
        self,
        num_circle_range=(3, 8), 
        circle_diameter_range=(5, 20),
        width=1
    ):
        """
        Adds random circles to the canvas using PIL.
        --------------------------------------------------------------
        :param num_circle_range: A tuple specifying the range of the number of circles to add.
        :param circle_diameter_range: A tuple specifying the range of diameters for the circles.
        :return: A PIL Image object representing the final canvas with circle noise.
        """

        draw = ImageDraw.Draw(self.canvas)
        num_circles = random.randint(*num_circle_range)

        for _ in range(num_circles):
            # Randomly choose the center and diameter for each circle
            center_x = random.randint(0, self.canvas.width)
            center_y = random.randint(0, self.canvas.height)
            diameter = random.randint(*circle_diameter_range)

            # Calculate the bounding box for the circle
            left = center_x - diameter // 2
            top = center_y - diameter // 2
            right = center_x + diameter // 2
            bottom = center_y + diameter // 2

            # Generate a random RGB color for the circle
            circle_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

            # Draw the circle
            draw.ellipse([left, top, right, bottom], outline=circle_color, width=width)
        
        return self.canvas
    
    def add_noise_to_canvas(
        self,
        noise_density=0.05,
        num_line_range=(3, 8),
        num_circle_range=(3, 8),
        circle_diameter_range=(5, 20),
        width=1
    ):
        """
        Adds random noise to the canvas in the form of random pixels, 
        lines, circles, blurring, etc.
        --------------------------------------------------------------
        :param noise_density: The density of noise to add.
        :param num_line_range: A tuple specifying the range of the number of lines to add.
        :param num_circle_range: A tuple specifying the range of the number of circles to add.
        :param circle_diameter_range: A tuple specifying the range of diameters for the circles.
        :return: A PIL Image object representing the final canvas.
        """

        # Apply noise to the canvas
        self.canvas = self._add_pixel_noise_to_canvas(noise_density=noise_density)
        self.canvas = self._add_line_noise_to_canvas(num_line_range=num_line_range, width=width)
        self.canvas = self._add_circle_noise_to_canvas(
                            num_circle_range=num_circle_range, 
                            circle_diameter_range=circle_diameter_range,
                            width=width
                        )

        return self.canvas
    
    def add_characters_to_canvas(
        self, 
        characters: list,
        rotate_range=(-15, 15),
        scale_range=(0.8, 1.2),
        x_offset_range=(-20,0),
    ):
        """
        Places characters on a canvas with variations.
        --------------------------------------------------------------
        :param characters: List of PIL Image objects of the characters.
        :param rotate_angle: Tuple of the range of rotation angles in degrees.
        :param scale_range: Tuple of the range of scale factors.
        :param x_offset_range: Tuple of the range of x-axis offsets.
        :return: A PIL Image object representing the final canvas.
        """

        # Initial X position (will be updated after placing each character)
        x_offset = random.randint(x_offset_range[1]//2, x_offset_range[1]*2)

        for i, char_img in enumerate(characters):
            # Randomly adjust the scale
            scale_factor = random.uniform(*scale_range)
            new_size = (int(char_img.width * scale_factor), int(char_img.height * scale_factor))
            char_img_resized = char_img.resize(new_size, Image.LANCZOS)

            # Randomly adjust the rotation angle
            angle = random.uniform(*rotate_range)
            char_img_rotated = char_img_resized.rotate(angle, expand=1, fillcolor=(255,255,255,0))

            # Randomly adjust the Y position for vertical variation, within canvas limits
            max_y_variation = self.canvas_size[1] - char_img_rotated.height
            y_offset = random.randint(0, max(max_y_variation, 1))

            # Composite the character onto the canvas
            self.canvas.paste(char_img_rotated, (x_offset, y_offset), char_img_rotated)

            # Update x_offset for the next character, allowing for some overlap
            x_offset += char_img_rotated.width - random.randint(*x_offset_range)  # Adjust overlap

            # Break if we run out of space on the canvas
            if i != len(characters)-1 and x_offset >= self.canvas_size[0] - char_img_rotated.width:
                # pop the characters that were not placed on the canvas
                for _ in range(i+1, len(characters)):
                    characters.pop() 

                # print("Characters did not fit on the canvas. Returning...")
                break

        return self.canvas

class CaptchaSynthesis:
    def __init__(
        self, 
        root_dir="mnist_chars/"
    ):
        self.sampler = Sampler(root_dir)
        self.cas = CanvasSynthesis()
    
    def colorize_image(
        self, 
        grayscale_img, 
        color,
        alpha_percent=0.65
    ):
        """
        This method converts an mnist gray-scale character image to 
        a colored character image.
        --------------------------------------------------------------
        :param: grayscale_img
        :param: color
        :param: alpha_percent
        :output: colored_image
        """
        
        # Ensure the image is in grayscale mode
        if grayscale_img.mode != 'L':
            raise ValueError("Image must be in grayscale mode ('L').")

        # Convert grayscale image to numpy array
        gray_data = np.array(grayscale_img)

        # Prepare an empty RGBA image with the same dimensions
        rgba_data = np.zeros((gray_data.shape[0], gray_data.shape[1], 4), dtype=np.uint8)

        # Set the RGB values to the specified color
        rgba_data[..., 0] = color[0]
        rgba_data[..., 1] = color[1]
        rgba_data[..., 2] = color[2]

        # Use the grayscale values directly as the alpha channel to preserve stroke intensity
        # Subtracting from 255 to invert the grayscale for proper visibility
        rgba_data[..., 3] = (255 - gray_data)*alpha_percent  

        # Convert back to an RGBA image
        new_img = Image.fromarray(rgba_data, 'RGBA')

        return new_img
    
    def create_canvas(
        self, 
        canvas_size=(160, 50),
        color=(255, 255, 255),
        alpha=200
    ):
        """
        Places characters on a canvas with variations.

        :param canvas_size: Tuple of the canvas size (width, height).
        :param color: Tuple of the RGB color values.
        :param alpha: The alpha value for the canvas.
        :return: A PIL Image object representing the canvas.
        """
        # Create a blank canvas
        canvas = Image.new('RGBA', canvas_size, (*color, alpha))
        return canvas

    def synthesize_captcha(
        self, 
        num_char_range=(4, 5),
        noise_density=0.05,
        num_line_range=(3, 8),
        num_circle_range=(3, 8),
        circle_diameter_range=(5, 60),
        rotate_range=(-20, 20),
        scale_range=(0.9, 1.1),
        x_offset_range=(-15, 15),
        canvas_size=(160, 50),
        background_alpha=255,
        background_color=(255, 255, 255),
        brush_width=1
    ):
        """
        This method synthesizes a captcha image with the specified number of characters.
        --------------------------------------------------------------
        :param num_chars: The number of characters to synthesize.
        :param noise_density: The density of noise to add to the canvas.
        :param rotate_range: Tuple of the range of rotation angles in degrees.
        :param scale_range: Tuple of the range of scale factors.
        :param x_offset_range: Tuple of the range of x-axis offsets.
        :return: A PIL Image object representing the final captcha.
        """

        # Sample characters and images
        num_chars = random.randint(*num_char_range)
        characters = self.sampler.sample_chars(num_chars=num_chars)
        sampled_images = self.sampler.sample_images_from_characters(characters, k=1)

        # Sample colors
        colors = self.sampler.sample_color(num_colors=num_chars)

        # Colorize the images
        colored_images = [self.colorize_image(img, color) for img, color in zip(sampled_images, colors)]

        # Create a blank canvas
        canvas = self.create_canvas(canvas_size=canvas_size, color=background_color, alpha=background_alpha)
        self.cas(canvas) # Update the canvas

        # Add characters to the canvas
        self.cas.add_characters_to_canvas(
                    colored_images,
                    rotate_range=rotate_range,
                    scale_range=scale_range,
                    x_offset_range=x_offset_range
                )

        # Add noise to the canvas
        canvas = self.cas.add_noise_to_canvas(
                        noise_density=noise_density,
                        num_line_range=num_line_range,
                        num_circle_range=num_circle_range,
                        circle_diameter_range=circle_diameter_range,
                        width=brush_width
                    )

        # Ensure the number of characters matches the number of images in the captcha
        characters = characters[:len(colored_images)] 
        
        # print(f"labels: {''.join(characters)}")
        return canvas, characters
    

if __name__ == "__main__":
    cg = CaptchaSynthesis()
    captcha, labels = cg.synthesize_captcha()
    # captcha.show()
    captcha.save("captcha.png")