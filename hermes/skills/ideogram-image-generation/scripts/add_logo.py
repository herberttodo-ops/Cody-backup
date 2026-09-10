#!/usr/bin/env python3
from PIL import Image
import os

# Load the generated image
gen_path = "/home/herby/.hermes/generated_images/optirfp_ideogram____ID___.png"
logo_path = "/home/herby/.hermes/assets/optirfp_logo.jpg"

img = Image.open(gen_path)

# Load and process logo
logo = Image.open(logo_path).convert("RGBA")

# Make white background transparent
data = logo.getdata()
newData = []
for item in data:
    # If pixel is close to white, make it transparent
    if item[0] > 240 and item[1] > 240 and item[2] > 240:
        newData.append((255, 255, 255, 0))
    else:
        newData.append(item)
logo.putdata(newData)

# Resize logo (height = 55px)
aspect = logo.width / logo.height
new_height = 55
new_width = int(new_height * aspect)
logo = logo.resize((new_width, new_height), Image.Resampling.LANCZOS)

# Position at bottom center
padding = 40
logo_x = (img.width - new_width) // 2
logo_y = img.height - new_height - padding

# Paste logo
img.paste(logo, (logo_x, logo_y), logo)

# Save final
output_dir = "/home/herby/.hermes/generated_images"
final_path = f"{output_dir}/optirfp_final_linkedin.png"
img.save(final_path, "PNG", quality=95)

print(f"Final image saved: {final_path}")
print(f"Image size: {img.width}x{img.height}")
