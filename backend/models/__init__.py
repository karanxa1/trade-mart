# Firestore Data Models
from .user import UserModel
from .product import ProductModel, CategoryModel, ConditionModel
from .order import OrderModel, OrderItemModel
from .cart import CartModel
from .message import MessageModel
from .offer import OfferModel
from .verification import BusinessVerificationModel

def init_firestore_data():
    CategoryModel.initialize_categories()
    ConditionModel.initialize_conditions()
    print("Firestore initialized with default categories and conditions")
