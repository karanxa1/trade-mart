from trade_mart.app import app, db, User, Product, Order, Offer, Message, BusinessVerification, VerificationActivity, SuspensionActivity

def delete_sellers():
    with app.app_context():
        # Find the sellers
        sellers = User.query.filter(User.username.in_(['JHONDO', 'SELLER1'])).all()
        
        for seller in sellers:
            print(f"Deleting seller: {seller.username}")
            
            # Delete related records
            Product.query.filter_by(seller_id=seller.id).delete()
            Order.query.filter_by(seller_id=seller.id).delete()
            Offer.query.filter_by(seller_id=seller.id).delete()
            Message.query.filter_by(sender_id=seller.id).delete()
            Message.query.filter_by(receiver_id=seller.id).delete()
            
            # Delete business verification if exists
            if seller.business_verification:
                VerificationActivity.query.filter_by(verification_id=seller.business_verification.id).delete()
                db.session.delete(seller.business_verification)
            
            # Delete suspension activities
            SuspensionActivity.query.filter_by(seller_id=seller.id).delete()
            
            # Delete the seller
            db.session.delete(seller)
        
        # Commit the changes
        db.session.commit()
        print("Deletion completed successfully!")

if __name__ == '__main__':
    delete_sellers() 