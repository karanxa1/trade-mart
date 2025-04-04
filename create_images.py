from PIL import Image, ImageDraw
import os

print("Script starting...")

# Create products directory if it doesn't exist
products_dir = 'trade_mart/static/images/products'
if not os.path.exists(products_dir):
    os.makedirs(products_dir)
    print(f"Created directory {products_dir}")
else:
    print(f"Directory {products_dir} already exists")

# List of products with their colors
products = [
    ('bike', (200, 100, 100)),
    ('blender', (100, 200, 100)),
    ('board_games', (100, 100, 200)),
    ('desk', (200, 200, 100)),
    ('drill', (100, 200, 200)),
    ('gaming_pc', (200, 100, 200)),
    ('handbag', (150, 150, 200)),
    ('harrypotter', (150, 200, 150)),
    ('iphone13', (200, 150, 150)),
    ('lawn_mower', (180, 180, 180)),
    ('macbook', (220, 220, 220)),
    ('records', (120, 120, 180)),
    ('ring', (200, 180, 120))
]

print(f"Attempting to create {len(products)} images...")

# Generate an image for each product
for name, color in products:
    try:
        # Create a new image with a white background
        img = Image.new('RGB', (400, 300), color=color)
        draw = ImageDraw.Draw(img)
        
        # Add product name as text
        display_name = name.replace('_', ' ').title()
        draw.text((150, 150), display_name, fill=(0, 0, 0))
        
        # Save the image
        img_path = os.path.join(products_dir, f"{name}.jpg")
        img.save(img_path)
        print(f"Created {name}.jpg")
    except Exception as e:
        print(f"Error creating {name}.jpg: {e}")

print("Script completed!")