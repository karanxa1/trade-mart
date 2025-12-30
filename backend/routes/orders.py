# Orders Routes
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from ..models.order import OrderModel, OrderItemModel
from ..models.cart import CartModel
from ..models.product import ProductModel
from ..models.user import UserModel
import logging

router = APIRouter(prefix="/api/orders", tags=["orders"])
logger = logging.getLogger(__name__)

class CheckoutRequest(BaseModel):
    user_id: str
    first_name: str
    last_name: str
    address: str
    address2: Optional[str] = ""
    city: str
    state: str
    zip_code: str
    payment_method: str = "cash_on_delivery"

class UpdateOrderStatusRequest(BaseModel):
    status: str
    tracking_status: Optional[str] = None

@router.get("/user/{user_id}")
async def get_user_orders(user_id: str):
    orders = OrderModel.get_by_user(user_id)
    
    for order in orders:
        items = OrderItemModel.get_by_order(order['id'])
        for item in items:
            product = ProductModel.get_by_id(item.get('product_id'))
            item['product'] = product
        order['items'] = items
    
    return orders

@router.get("/{order_id}")
async def get_order(order_id: str):
    order = OrderModel.get_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    items = OrderItemModel.get_by_order(order_id)
    for item in items:
        product = ProductModel.get_by_id(item.get('product_id'))
        item['product'] = product
    order['items'] = items
    
    return order

@router.get("/track/{tracking_id}")
async def track_order(tracking_id: str):
    order = OrderModel.get_by_tracking_id(tracking_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    items = OrderItemModel.get_by_order(order['id'])
    for item in items:
        product = ProductModel.get_by_id(item.get('product_id'))
        item['product'] = product
    order['items'] = items
    
    return order

@router.post("/checkout")
async def checkout(request: CheckoutRequest):
    cart_items = CartModel.get_by_user(request.user_id)
    
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    total = 0.0
    items_to_order = []
    
    for item in cart_items:
        product = ProductModel.get_by_id(item.get('product_id'))
        if product and product.get('status') == 'available':
            item_total = item.get('quantity', 0) * product.get('price', 0)
            total += item_total
            items_to_order.append((item, product))
    
    if not items_to_order:
        raise HTTPException(status_code=400, detail="No available products in cart")
    
    delivery_address = f"{request.first_name} {request.last_name}, {request.address}"
    if request.address2:
        delivery_address += f", {request.address2}"
    delivery_address += f", {request.city}, {request.state} {request.zip_code}"
    
    order_id = OrderModel.create_order(
        user_id=request.user_id,
        total_amount=total,
        delivery_address=delivery_address,
        payment_method=request.payment_method
    )
    
    for item, product in items_to_order:
        OrderItemModel.create_item(
            order_id=order_id,
            product_id=product['id'],
            quantity=item.get('quantity', 1),
            price=product.get('price', 0)
        )
        ProductModel.update(product['id'], {'status': 'reserved'})
    
    CartModel.clear_user_cart(request.user_id)
    
    order = OrderModel.get_by_id(order_id)
    
    logger.info(f"Order created: {order_id} by User: {request.user_id} Amount: {total}")
    return {
        "success": True,
        "order_id": order_id,
        "tracking_id": order.get('tracking_id'),
        "total": total
    }

@router.put("/{order_id}/status")
async def update_order_status(order_id: str, request: UpdateOrderStatusRequest):
    order = OrderModel.get_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    update_data = {'status': request.status}
    if request.tracking_status:
        update_data['tracking_status'] = request.tracking_status
    
    OrderModel.update(order_id, update_data)
    return {"success": True}

@router.get("/seller/{seller_id}")
async def get_seller_orders(seller_id: str):
    products = ProductModel.get_by_seller(seller_id)
    product_ids = [p['id'] for p in products]
    
    orders_data = {}
    for product_id in product_ids:
        order_items = OrderItemModel.get_by_product(product_id)
        for item in order_items:
            order_id = item.get('order_id')
            if order_id not in orders_data:
                order = OrderModel.get_by_id(order_id)
                if order:
                    order['items'] = []
                    orders_data[order_id] = order
            if order_id in orders_data:
                product = ProductModel.get_by_id(item.get('product_id'))
                item['product'] = product
                orders_data[order_id]['items'].append(item)
    
    orders = list(orders_data.values())
    
    # Batch fetch buyers
    buyer_ids = list(set([o.get('user_id') for o in orders if o.get('user_id')]))
    buyers = UserModel.get_by_ids(buyer_ids)
    buyers_map = {b['id']: b for b in buyers}
    
    for order in orders:
        buyer = buyers_map.get(order.get('user_id'))
        order['buyer'] = {
            'id': buyer['id'] if buyer else None,
            'username': buyer.get('username') if buyer else None
        }
             
    return orders
