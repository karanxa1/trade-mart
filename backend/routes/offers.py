# Offers Routes
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from firebase_admin import firestore

from ..models.offer import OfferModel
from ..models.product import ProductModel
from ..models.user import UserModel
import logging

router = APIRouter(prefix="/api/offers", tags=["offers"])
logger = logging.getLogger(__name__)

class CreateOfferRequest(BaseModel):
    product_id: str
    buyer_id: str
    offer_price: float

class RespondOfferRequest(BaseModel):
    action: str  # 'accept' or 'reject'

@router.get("/buyer/{buyer_id}")
async def get_buyer_offers(buyer_id: str):
    offers = OfferModel.get_by_buyer(buyer_id)
    offers_with_details = []
    
    # Pre-fetch products
    product_ids = list(set([o.get('product_id') for o in offers]))
    # Note: ProductModel doesn't have batch fetch yet, so we still loop for products or add batch there too. 
    # For now, let's just optimize sellers since users are the main cross-collection join.
    # Actually, getting products one by one is also slow. But let's assume ProductModel.get_by_id checks memory/cache? No it doesn't.
    # Prioritizing User batching as it's the requested fix pattern.
    
    # We need product to get seller_id. So we must fetch products first.
    # Optimization: Add get_by_ids to ProductModel too? 
    # For now, let's keep product fetch as is (maybe optimize later) but batch fetch sellers after we have products.
    
    products_map = {}
    seller_ids = set()
    
    for offer in offers:
        pid = offer.get('product_id')
        if pid not in products_map:
            p = ProductModel.get_by_id(pid)
            products_map[pid] = p
            if p and p.get('seller_id'):
                seller_ids.add(p.get('seller_id'))
                
    sellers = UserModel.get_by_ids(list(seller_ids))
    sellers_map = {s['id']: s for s in sellers}
    
    for offer in offers:
        product = products_map.get(offer.get('product_id'))
        seller = sellers_map.get(product.get('seller_id')) if product else None
        
        offers_with_details.append({
            **offer,
            "product": product,
            "seller": {
                "id": seller['id'] if seller else None,
                "username": seller.get('username') if seller else None
            } if seller else None
        })
    
    return offers_with_details

@router.get("/seller/{seller_id}")
async def get_seller_offers(seller_id: str):
    offers = OfferModel.get_by_seller(seller_id)
    offers_with_details = []
    
    buyer_ids = list(set([o.get('buyer_id') for o in offers]))
    buyers = UserModel.get_by_ids(buyer_ids)
    buyers_map = {b['id']: b for b in buyers}
    
    for offer in offers:
        product = ProductModel.get_by_id(offer.get('product_id')) # Potential optimization point
        buyer = buyers_map.get(offer.get('buyer_id'))
        
        offers_with_details.append({
            **offer,
            "product": product,
            "buyer": {
                "id": buyer['id'] if buyer else None,
                "username": buyer.get('username') if buyer else None
            } if buyer else None
        })
    
    return offers_with_details

@router.get("/seller/{seller_id}/pending-count")
async def get_pending_offers_count(seller_id: str):
    count = OfferModel.get_pending_count_for_seller(seller_id)
    return {"count": count}

@router.post("/")
async def create_offer(request: CreateOfferRequest):
    product = ProductModel.get_by_id(request.product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.get('status') != 'available':
        raise HTTPException(status_code=400, detail="Product is not available")
    
    if product.get('seller_id') == request.buyer_id:
        raise HTTPException(status_code=400, detail="You cannot make an offer on your own product")
    
    if not product.get('negotiable', False):
        raise HTTPException(status_code=400, detail="This product does not accept offers")
    
    if request.offer_price <= 0:
        raise HTTPException(status_code=400, detail="Offer price must be greater than 0")
    
    if request.offer_price >= product.get('price', 0):
        raise HTTPException(status_code=400, detail="Offer must be lower than listing price")
    
    existing_offer = OfferModel.get_pending_by_buyer_product(request.buyer_id, request.product_id)
    
    if existing_offer:
        OfferModel.update(existing_offer['id'], {
            'offer_price': request.offer_price,
            'created_at': firestore.SERVER_TIMESTAMP
        })
        return {"success": True, "message": "Offer updated", "offer_id": existing_offer['id']}
    else:
        offer_id = OfferModel.create_offer(
            product_id=request.product_id,
            buyer_id=request.buyer_id,
            seller_id=product.get('seller_id'),
            offer_price=request.offer_price
        )
        logger.info(f"Offer created: {offer_id} for Product {request.product_id} by Buyer {request.buyer_id}")
        return {"success": True, "offer_id": offer_id}

@router.post("/{offer_id}/respond")
async def respond_to_offer(offer_id: str, request: RespondOfferRequest):
    offer = OfferModel.get_by_id(offer_id)
    
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    
    if offer.get('status') != 'pending':
        raise HTTPException(status_code=400, detail="Offer has already been responded to")
    
    if request.action == 'accept':
        OfferModel.update(offer_id, {'status': 'accepted'})
        ProductModel.update(offer.get('product_id'), {'price': offer.get('offer_price')})
        return {"success": True, "message": "Offer accepted. Product price updated."}
    elif request.action == 'reject':
        OfferModel.update(offer_id, {'status': 'rejected'})
        return {"success": True, "message": "Offer rejected."}
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'accept' or 'reject'.")
