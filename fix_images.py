from trade_mart.app import app, db, Product

# Mapping of old image names to actual image files
image_mapping = {
    'laptop.jpg': 'macbook.jpg',
    'books.jpg': 'harrypotter.jpg',
    'sofa.jpg': 'desk.jpg',
    'drill.jpg': 'drill.jpg',
    'bike.jpg': 'bike.jpg',
    'lego.jpg': 'board_games.jpg',
    'iphone.jpg': 'iphone13.jpg',
    'dutch_oven.jpg': 'blender.jpg',
    'tent.jpg': 'ring.jpg',
    'guitar.jpg': 'records.jpg',
    'air_fryer.jpg': 'gaming_pc.jpg',
    'jacket.jpg': 'handbag.jpg',
    'board_games.jpg': 'board_games.jpg',
    'blender.jpg': 'blender.jpg',
    'ring.jpg': 'ring.jpg',
    'lawn_mower.jpg': 'lawn_mower.jpg',
    'desk.jpg': 'desk.jpg',
    'handbag.jpg': 'handbag.jpg',
    'gaming_pc.jpg': 'gaming_pc.jpg',
    'records.jpg': 'records.jpg'
}

with app.app_context():
    products = Product.query.all()
    print("Original product images:")
    for p in products:
        print(f"{p.id}: {p.name} - Image: {p.image}")
    
    # Update the image paths
    print("\nUpdating image paths...")
    for p in products:
        if p.image in image_mapping:
            p.image = image_mapping[p.image]
        elif p.image.startswith('data:image'):
            # Handle base64 encoded images
            p.image = 'placeholder.jpg'
    
    # Save changes to the database
    db.session.commit()
    
    # Verify the updates
    print("\nUpdated product images:")
    products = Product.query.all()
    for p in products:
        print(f"{p.id}: {p.name} - Image: {p.image}")
        
    print("\nUpdate complete!") 