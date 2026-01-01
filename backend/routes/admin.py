# Admin Routes (Government Portal)
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from ..models.user import UserModel
from ..models.verification import BusinessVerificationModel, ReviewModel
from ..models.product import ProductModel, CategoryModel, ConditionModel
from ..models.order import OrderItemModel
from ..config import db

router = APIRouter(prefix="/api/admin", tags=["admin"])

class VerificationResponse(BaseModel):
    action: str  # 'approve' or 'reject'
    reason: Optional[str] = None

class SuspendSellerRequest(BaseModel):
    reason: str

class ProductApprovalRequest(BaseModel):
    gov_employee_id: str

class ProductRejectionRequest(BaseModel):
    gov_employee_id: str
    reason: str

class ProductDeletionRequest(BaseModel):
    gov_employee_id: str
    reason: str

@router.get("/pending-verifications")
async def get_pending_verifications():
    verifications = BusinessVerificationModel.get_pending()
    
    for v in verifications:
        user = UserModel.get_by_id(v.get('user_id'))
        v['user'] = {
            'id': user['id'] if user else None,
            'username': user.get('username') if user else None,
            'email': user.get('email') if user else None
        }
    
    return verifications

@router.get("/oversight-items")
async def get_oversight_items():
    # 1. Get Pending Verifications
    verifications = BusinessVerificationModel.get_pending()
    items = []
    
    for v in verifications:
        user = UserModel.get_by_id(v.get('user_id'))
        items.append({
            'id': v.get('id'),
            'type': 'Seller Verification',
            'status': 'Pending',
            'date': v.get('created_at', '').isoformat() if hasattr(v.get('created_at'), 'isoformat') else str(v.get('created_at')),
            'details': f"New seller registration: {user.get('username', 'Unknown') if user else 'Unknown'}",
            'action_link': f"/govt/sellers", # or specific verification page
            'raw_data': v
        })

    # 2. Get High Value Orders (> 50000) - Assuming we add this method to OrderModel or query here
    # For now, let's fetch recent orders and filter (inefficient for prod but works for this scale)
    from ..models.order import OrderModel
    # We need to expose a method in OrderModel to get all orders or high value ones
    # Let's add a quick helper method in OrderModel or just hack it here if OrderModel exposes stream
    # OrderModel.get_all() doesn't exist yet, let's assume we can add it or use firestore directly here
    
    # Direct Firestore Query for High Value Orders
    try:
        high_val_docs = db.collection('orders').where('total_amount', '>', 50000).limit(10).stream()
        for doc in high_val_docs:
            data = doc.to_dict()
            if data.get('status') not in ['completed', 'cancelled']: # Only flag active high value orders
                items.append({
                    'id': doc.id,
                    'type': 'High Value Transaction',
                    'status': data.get('status', 'Pending'),
                    'date': data.get('created_at', '').isoformat() if hasattr(data.get('created_at'), 'isoformat') else str(data.get('created_at')),
                    'details': f"Order Value: ₹{data.get('total_amount', 0):,}",
                    'action_link': f"/orders/{doc.id}", # Link to view order
                    'raw_data': {'id': doc.id, **data}
                })
    except Exception as e:
        print(f"Error fetching high value orders: {e}")

    return items

@router.get("/sellers")
async def get_all_sellers():
    sellers = UserModel.get_all_sellers()
    
    for seller in sellers:
        stats = ReviewModel.get_seller_stats(seller['id'])
        products = ProductModel.get_by_seller(seller['id'])
        
        total_sales = 0
        for product in products:
            order_items = OrderItemModel.get_by_product(product['id'])
            for item in order_items:
                total_sales += item.get('price', 0) * item.get('quantity', 0)
        
        seller['stats'] = {
            'avg_rating': stats.get('avg_rating', 0),
            'review_count': stats.get('count', 0),
            'product_count': len(products),
            'total_sales': total_sales
        }
    
    return sellers

@router.get("/seller/{seller_id}")
async def get_seller_details(seller_id: str):
    seller = UserModel.get_by_id(seller_id)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    
    if seller.get('user_type') != 'seller':
        raise HTTPException(status_code=400, detail="User is not a seller")
    
    stats = ReviewModel.get_seller_stats(seller_id)
    products = ProductModel.get_by_seller(seller_id)
    reviews = ReviewModel.get_by_seller(seller_id)
    
    for review in reviews:
        reviewer = UserModel.get_by_id(review.get('reviewer_id'))
        review['reviewer_username'] = reviewer.get('username') if reviewer else None
    
    return {
        **seller,
        'stats': {
            'avg_rating': stats.get('avg_rating', 0),
            'review_count': stats.get('count', 0),
            'product_count': len(products)
        },
        'products': products,
        'reviews': reviews
    }

@router.post("/verification/{verification_id}/respond")
async def respond_to_verification(verification_id: str, request: VerificationResponse):
    verification = BusinessVerificationModel.get_by_id(verification_id)
    if not verification:
        raise HTTPException(status_code=404, detail="Verification not found")
    
    if request.action == 'approve':
        BusinessVerificationModel.update(verification_id, {'status': 'approved'})
        UserModel.update(verification.get('user_id'), {'identity_verified': True})
        return {"success": True, "message": "Seller verified successfully"}
    elif request.action == 'reject':
        BusinessVerificationModel.update(verification_id, {
            'status': 'rejected',
            'reject_reason': request.reason
        })
        return {"success": True, "message": "Verification rejected"}
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

@router.post("/seller/{seller_id}/suspend")
async def suspend_seller(seller_id: str, request: SuspendSellerRequest):
    seller = UserModel.get_by_id(seller_id)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    
    from datetime import datetime
    UserModel.update(seller_id, {
        'is_suspended': True,
        'suspend_reason': request.reason,
        'suspended_at': datetime.utcnow().isoformat()
    })
    
    return {"success": True, "message": "Seller suspended"}

@router.post("/seller/{seller_id}/unsuspend")
async def unsuspend_seller(seller_id: str):
    seller = UserModel.get_by_id(seller_id)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    
    UserModel.update(seller_id, {
        'is_suspended': False,
        'suspend_reason': None,
        'suspended_at': None
    })
    
    return {"success": True, "message": "Seller unsuspended"}

@router.post("/seller/{seller_id}/verify")
async def verify_seller(seller_id: str):
    seller = UserModel.get_by_id(seller_id)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    
    UserModel.update(seller_id, {'is_verified': True, 'identity_verified': True})
    
    return {"success": True, "message": "Seller verified"}

# Product Approval Routes
@router.get("/pending-products")
async def get_pending_products():
    """Get all active products for government review (pending + approved)"""
    products = ProductModel.get_all_products_with_approval_status()
    
    # Filter out deleted products  
    products = [p for p in products if p.get('status') != 'deleted']
    
    # Enrich with seller and category info
    seller_ids = list(set([p.get('seller_id') for p in products if p.get('seller_id')]))
    sellers = UserModel.get_by_ids(seller_ids)
    sellers_map = {s['id']: s for s in sellers}
    
    categories = CategoryModel.get_all()
    conditions = ConditionModel.get_all()
    cat_map = {c['id']: c for c in categories}
    cond_map = {c['id']: c for c in conditions}
    
    for product in products:
        seller = sellers_map.get(product.get('seller_id'))
        category = cat_map.get(product.get('category_id'))
        condition = cond_map.get(product.get('condition_id'))
        
        product['seller'] = {
            'id': seller['id'] if seller else None,
            'username': seller.get('username') if seller else 'Unknown',
            'email': seller.get('email') if seller else 'Unknown'
        } if seller else None
        product['category_name'] = category.get('name') if category else ''
        product['condition_name'] = condition.get('name') if condition else ''
    
    return products

@router.post("/product/{product_id}/approve")
async def approve_product(product_id: str, request: ProductApprovalRequest):
    """Approve a pending product"""
    product = ProductModel.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.get('approval_status') == 'approved':
        raise HTTPException(status_code=400, detail="Product already approved")
    
    ProductModel.approve_product(product_id, request.gov_employee_id)
    return {"success": True, "message": "Product approved successfully"}

@router.post("/product/{product_id}/reject")
async def reject_product(product_id: str, request: ProductRejectionRequest):
    """Reject a pending product"""
    product = ProductModel.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.get('approval_status') == 'approved':
        raise HTTPException(status_code=400, detail="Product already approved")
    
    ProductModel.reject_product(product_id, request.gov_employee_id, request.reason)
    return {"success": True, "message": "Product rejected"}

@router.post("/product/{product_id}/delete")
async def delete_product(product_id: str, request: ProductDeletionRequest):
    """Delete a product by government employee"""
    product = ProductModel.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    ProductModel.delete_by_government(product_id, request.gov_employee_id, request.reason)
    return {"success": True, "message": "Product deleted successfully"}

@router.get("/product-approval-stats")
async def get_product_approval_stats():
    """Get statistics about product approvals"""
    all_products = ProductModel.get_all_products_with_approval_status()
    
    pending_count = sum(1 for p in all_products if p.get('approval_status') == 'pending')
    approved_count = sum(1 for p in all_products if p.get('approval_status') == 'approved')
    rejected_count = sum(1 for p in all_products if p.get('approval_status') == 'rejected')
    
    return {
        "pending": pending_count,
        "approved": approved_count,
        "rejected": rejected_count,
        "total": len(all_products)
    }
