# Cart Routes
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from ..models.cart import CartModel
from ..models.product import ProductModel, ConditionModel
import logging

router = APIRouter(prefix="/api/cart", tags=["cart"])
logger = logging.getLogger(__name__)

class AddToCartRequest(BaseModel):
    user_id: str
    product_id: str
    quantity: int = 1

class UpdateCartRequest(BaseModel):
    quantity: int

@router.get("/{user_id}")
async def get_cart(user_id: str):
    cart_items = CartModel.get_by_user(user_id)
    cart_with_details = []
    total = 0.0
    
    for item in cart_items:
        product = ProductModel.get_by_id(item.get('product_id'))
        if product:
            condition = ConditionModel.get_by_id(product.get('condition_id'))
            item_total = item.get('quantity', 0) * product.get('price', 0)
            total += item_total
            cart_with_details.append({
                **item,
                "product": product,
                "condition_name": condition.get('name') if condition else '',
                "item_total": item_total
            })
    
    return {
        "items": cart_with_details,
        "total": total,
        "count": len(cart_with_details)
    }

@router.post("/add")
async def add_to_cart(request: AddToCartRequest):
    product = ProductModel.get_by_id(request.product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.get('status') != 'available':
        raise HTTPException(status_code=400, detail="Product is not available")
    
    if product.get('seller_id') == request.user_id:
        raise HTTPException(status_code=400, detail="You cannot buy your own product")
    
    cart_id = CartModel.add_to_cart(request.user_id, request.product_id, request.quantity)
    
    logger.info(f"Item added to cart: Product {request.product_id} (Qty: {request.quantity}) for User {request.user_id}")
    return {"success": True, "cart_id": cart_id}

@router.put("/{cart_id}")
async def update_cart_item(cart_id: str, request: UpdateCartRequest):
    cart_item = CartModel.get_by_id(cart_id)
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    if request.quantity <= 0:
        CartModel.delete(cart_id)
        return {"success": True, "message": "Item removed from cart"}
    
    CartModel.update(cart_id, {'quantity': request.quantity})
    return {"success": True}

@router.delete("/{cart_id}")
async def remove_from_cart(cart_id: str):
    cart_item = CartModel.get_by_id(cart_id)
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    CartModel.delete(cart_id)
    return {"success": True}

@router.delete("/clear/{user_id}")
async def clear_cart(user_id: str):
    CartModel.clear_user_cart(user_id)
    return {"success": True}
