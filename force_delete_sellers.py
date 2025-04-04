from trade_mart.app import app, db, User, Product, Order, OrderItem, Offer, Message, BusinessVerification, VerificationActivity, SuspensionActivity
from sqlalchemy import text

def force_delete_sellers():
    with app.app_context():
        # First, get the seller IDs
        sellers = User.query.filter(User.username.in_(['JHONDO', 'SELLER1'])).all()
        
        for seller in sellers:
            print(f"Force deleting seller: {seller.username}")
            
            # Delete all related records using raw SQL to bypass foreign key constraints
            db.session.execute(text(f"DELETE FROM order_item WHERE product_id IN (SELECT id FROM product WHERE seller_id = {seller.id})"))
            db.session.execute(text(f"DELETE FROM product WHERE seller_id = {seller.id}"))
            db.session.execute(text(f"DELETE FROM order WHERE seller_id = {seller.id}"))
            db.session.execute(text(f"DELETE FROM offer WHERE seller_id = {seller.id}"))
            db.session.execute(text(f"DELETE FROM message WHERE sender_id = {seller.id} OR receiver_id = {seller.id}"))
            
            # Delete business verification and related records
            if seller.business_verification:
                db.session.execute(text(f"DELETE FROM verification_activity WHERE verification_id = {seller.business_verification.id}"))
                db.session.execute(text(f"DELETE FROM business_verification WHERE id = {seller.business_verification.id}"))
            
            # Delete suspension activities
            db.session.execute(text(f"DELETE FROM suspension_activity WHERE seller_id = {seller.id}"))
            
            # Finally, delete the seller
            db.session.execute(text(f"DELETE FROM user WHERE id = {seller.id}"))
        
        # Commit all changes
        db.session.commit()
        print("Force deletion completed successfully!")

if __name__ == '__main__':
    force_delete_sellers() 