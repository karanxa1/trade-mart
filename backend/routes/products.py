# Products Routes
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List
import os
import os
import shutil

from ..models.product import ProductModel, CategoryModel, ConditionModel
from ..models.user import UserModel
from ..models.verification import ReviewModel
import logging

router = APIRouter(prefix="/api/products", tags=["products"])
logger = logging.getLogger(__name__)

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'frontend', 'public', 'images', 'products')

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    negotiable: bool = False
    condition_id: str
    category_id: str
    image: Optional[str] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    negotiable: Optional[bool] = None
    condition_id: Optional[str] = None
    category_id: Optional[str] = None
    status: Optional[str] = None
    image: Optional[str] = None

@router.get("")
async def get_products(
    category: Optional[str] = None,
    condition: Optional[str] = None,
    seller: Optional[str] = None,
    min_price: Optional[str] = None,
    max_price: Optional[str] = None,
    q: Optional[str] = None,
    sort: str = "newest",
    page: int = 1,
    per_page: int = 12
):
    # Sanitize inputs
    if category == "": category = None
    if condition == "": condition = None
    if seller == "": seller = None
    if q == "": q = None

    # Parse numeric params safely
    min_p_val = None
    if min_price and min_price.strip():
        try:
            min_p_val = float(min_price)
        except ValueError:
            pass
            
    max_p_val = None
    if max_price and max_price.strip():
        try:
            max_p_val = float(max_price)
        except ValueError:
            pass

    products = ProductModel.get_available_products(
        category_id=category,
        condition_id=condition,
        seller_id=seller,
        min_price=min_p_val,
        max_price=max_p_val,
        search_query=q,
        sort_by=sort
    )
    
    if not seller:
        enriched_products = []
        
        # Collect all seller IDs
        seller_ids = list(set([p.get('seller_id') for p in products if p.get('seller_id')]))
        
        # Batch fetch sellers
        sellers = UserModel.get_by_ids(seller_ids)
        sellers_map = {s['id']: s for s in sellers}
        
        for product in products:
            seller_data = sellers_map.get(product.get('seller_id'))
            product['seller'] = {
                'id': seller_data['id'] if seller_data else None,
                'username': seller_data.get('username') if seller_data else 'Unknown',
                'avg_rating': seller_data.get('avg_rating', 0) if seller_data else 0
            }
            enriched_products.append(product)
        products = enriched_products
    
    total = len(products)
    start = (page - 1) * per_page
    end = start + per_page
    products_page = products[start:end]
    
    # Optimize Category and Condition fetching (Fetch all once since they are small collections)
    # Caching these in memory would be even better for production
    categories = CategoryModel.get_all()
    conditions = ConditionModel.get_all()
    cat_map = {c['id']: c for c in categories}
    cond_map = {c['id']: c for c in conditions}
    
    for p in products_page:
        category_data = cat_map.get(p.get('category_id'))
        condition_data = cond_map.get(p.get('condition_id'))
        p['category_name'] = category_data.get('name') if category_data else ''
        p['condition_name'] = condition_data.get('name') if condition_data else ''
    
    return {
        "products": products_page,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page
    }

@router.get("/featured")
async def get_featured_products(limit: int = 8):
    products = ProductModel.get_available_products(limit=limit)
    
    # Batch fetch sellers
    seller_ids = list(set([p.get('seller_id') for p in products if p.get('seller_id')]))
    sellers = UserModel.get_by_ids(seller_ids)
    sellers_map = {s['id']: s for s in sellers}
    
    # Get all conditions at once (cached)
    conditions = ConditionModel.get_all()
    cond_map = {c['id']: c for c in conditions}
    
    for product in products:
        seller = sellers_map.get(product.get('seller_id'))
        condition = cond_map.get(product.get('condition_id'))
        product['condition_name'] = condition.get('name') if condition else ''
        product['seller'] = {
            'id': seller['id'] if seller else None,
            'username': seller.get('username') if seller else 'Unknown',
            'avg_rating': seller.get('avg_rating', 0) if seller else 0
        }
    
    return products[:limit]

@router.get("/categories")
async def get_categories():
    return CategoryModel.get_all()

@router.get("/conditions")
async def get_conditions():
    return ConditionModel.get_all()

@router.get("/{product_id}")
async def get_product(product_id: str):
    product = ProductModel.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Use cached lookups
    seller = UserModel.get_by_id(product.get('seller_id'))
    condition = ConditionModel.get_by_id(product.get('condition_id'))
    category = CategoryModel.get_by_id(product.get('category_id'))
    
    seller_stats = ReviewModel.get_seller_stats(seller.get('id')) if seller else {'avg_rating': 0, 'count': 0}
    
    # Get similar products (limit to 5, filter out current)
    similar = ProductModel.get_available_products(category_id=product.get('category_id'), limit=5)
    similar = [p for p in similar if p.get('id') != product_id][:4]
    
    # Enrich similar products with condition names (cached)
    conditions = ConditionModel.get_all()
    cond_map = {c['id']: c for c in conditions}
    for p in similar:
        cond = cond_map.get(p.get('condition_id'))
        p['condition_name'] = cond.get('name') if cond else ''
    
    return {
        **product,
        "seller": {
            "id": seller['id'] if seller else None,
            "username": seller.get('username') if seller else None,
            "avg_rating": seller_stats.get('avg_rating', 0),
            "review_count": seller_stats.get('count', 0)
        } if seller else None,
        "condition_name": condition.get('name') if condition else '',
        "category_name": category.get('name') if category else '',
        "similar_products": similar
    }

@router.post("")
async def create_product(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    negotiable: bool = Form(False),
    condition_id: str = Form(...),
    category_id: str = Form(...),
    seller_id: str = Form(...),
    image: Optional[UploadFile] = File(None)
):
    image_path = None
    if image:
        # ImgBB Upload
        import requests
        import base64
        
        IMGBB_API_KEY = "a1e67563c8efec2b94d9b605b0aa1db9" # Should be in env vars
        
        # Read file content
        file_content = await image.read()
        
        # Prepare payload
        payload = {
            "key": IMGBB_API_KEY,
            "image": base64.b64encode(file_content).decode('utf-8')
        }
        
        try:
            response = requests.post("https://api.imgbb.com/1/upload", data=payload)
            response.raise_for_status()
            result = response.json()
            if result.get("success"):
                image_path = result["data"]["url"]
            else:
                print(f"ImgBB Error: {result}")
        except Exception as e:
            print(f"Image upload failed: {str(e)}")
            # Fallback or error handling? For now, we continue without image if fail
            pass
    
    product_id = ProductModel.create_product(
        name=name,
        description=description,
        price=price,
        negotiable=negotiable,
        condition_id=condition_id,
        image=image_path,
        category_id=category_id,
        seller_id=seller_id
    )
    
    logger.info(f"Product created: {name} (ID: {product_id}) by Seller: {seller_id}")
    return {"success": True, "product_id": product_id}

@router.put("/{product_id}")
async def update_product(product_id: str, data: ProductUpdate):
    product = ProductModel.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    ProductModel.update(product_id, update_data)
    
    return {"success": True}

@router.delete("/{product_id}")
async def delete_product(product_id: str):
    product = ProductModel.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    ProductModel.delete(product_id)
    return {"success": True}

@router.get("/seller/{seller_id}")
async def get_seller_products(seller_id: str):
    products = ProductModel.get_by_seller(seller_id)
    
    # Get all categories and conditions at once (cached)
    categories = CategoryModel.get_all()
    conditions = ConditionModel.get_all()
    cat_map = {c['id']: c for c in categories}
    cond_map = {c['id']: c for c in conditions}
    
    for p in products:
        category = cat_map.get(p.get('category_id'))
        condition = cond_map.get(p.get('condition_id'))
        p['category_name'] = category.get('name') if category else ''
        p['condition_name'] = condition.get('name') if condition else ''
    
    return products
