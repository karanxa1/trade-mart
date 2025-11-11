# Trade Mart Database ER Diagram

## Overview

This document describes the Entity-Relationship Diagram (ERD) for the Trade Mart e-commerce platform database. Trade Mart is a comprehensive marketplace that connects buyers and sellers with government oversight for business verification and seller management.

## Database Schema Summary

The database consists of 12 main entities that handle user management, product listings, transactions, communication, and government oversight functions.

### Core Entities

#### 1. User
- **Purpose**: Stores all user accounts (buyers, sellers, government employees)
- **Key Fields**:
  - `id` (Primary Key)
  - `username`, `email`, `password` - Authentication
  - `user_type` - 'buyer', 'seller', or 'govt_employee'
  - `is_verified` - Email verification status
  - `identity_verified` - Business verification status
  - Suspension fields for government control

#### 2. Product
- **Purpose**: Product listings by sellers
- **Key Fields**:
  - `id` (Primary Key)
  - Foreign keys to `Category`, `Condition`, `User` (seller)
  - `price`, `negotiable`, `status` (available/sold/reserved)
  - `image` - Product image path

#### 3. Category & Condition
- **Purpose**: Classification systems for products
- **Category**: Electronics, Books, Furniture, Tools, Vehicles, Toys, Clothing, Home & Garden
- **Condition**: New, Like New, Good, Fair, Poor

### Transaction Entities

#### 4. Order & OrderItem
- **Purpose**: Handle customer purchases
- **Order**: Order header with customer, date, status, tracking
- **OrderItem**: Individual products within orders

#### 5. Cart
- **Purpose**: Shopping cart functionality
- **Key Fields**: User, Product, Quantity

### Communication & Negotiation

#### 6. Message
- **Purpose**: Communication between users about products
- **Key Fields**: Sender, Receiver, Product (optional), content, read status

#### 7. Offer
- **Purpose**: Price negotiation system
- **Key Fields**: Product, Buyer, Seller, offer_price, status (pending/accepted/rejected)

### Review System

#### 8. Review
- **Purpose**: Seller rating and feedback system
- **Key Fields**: Reviewer, Seller, rating (1-5), comment

### Government Oversight

#### 9. BusinessVerification
- **Purpose**: Business verification process for sellers
- **Key Fields**: User, business details, documents, status, government approval

#### 10. VerificationActivity
- **Purpose**: Audit log of verification decisions
- **Key Fields**: Verification request, government employee, action, reason

#### 11. SuspensionActivity
- **Purpose**: Audit log of seller suspensions
- **Key Fields**: Seller, government employee, action, reason

## Key Relationships

### User Relationships
- **1:N** with Product (sellers list products)
- **1:N** with Order (buyers place orders)
- **1:N** with Cart (buyers have cart items)
- **1:N** with Message (users send/receive messages)
- **1:N** with Offer (buyers make offers, sellers receive offers)
- **1:N** with Review (buyers write reviews, sellers receive reviews)
- **1:1** with BusinessVerification (sellers request verification)
- **1:N** with VerificationActivity/SuspensionActivity (government actions)

### Product Relationships
- **N:1** with Category, Condition, User (seller)
- **1:N** with OrderItem, Cart, Message, Offer

### Transaction Flow
```
User (Buyer) → Cart → Order → OrderItem → Product
```

### Verification Flow
```
User (Seller) → BusinessVerification → VerificationActivity
```

## Business Logic Features

### 1. Multi-User Types
- **Buyers**: Can browse, add to cart, checkout, make offers, leave reviews, send messages
- **Sellers**: Can list products, manage orders, respond to offers, communicate with buyers
- **Government Employees**: Can verify businesses, suspend sellers, view analytics

### 2. Product Negotiation
- Sellers can mark products as negotiable
- Buyers can make offers on negotiable products
- Sellers can accept/reject offers

### 3. Government Oversight
- Mandatory business verification for sellers
- Document upload and review process
- Seller suspension capabilities
- Complete audit trail

### 4. Order Management
- Order tracking with status updates
- Multiple payment methods (cash on delivery, etc.)
- Order history and tracking

### 5. Communication System
- In-app messaging between buyers and sellers
- Message threading by product
- Read/unread status tracking

## Database Constraints & Rules

### Data Integrity
- All foreign keys properly defined
- User types restricted to 'buyer', 'seller', 'govt_employee'
- Product status restricted to 'available', 'sold', 'reserved'
- Order status: 'pending', 'completed', 'cancelled'
- Offer status: 'pending', 'accepted', 'rejected'

### Business Rules
- Users cannot buy their own products
- Only verified sellers can have products shown by default
- Reviews can only be left by buyers who have purchased from the seller
- Identity verification required for sellers
- Government employees have special permissions

## File Structure

The ERD is available in two formats:
- `erd_diagram.puml` - PlantUML source file for generating visual diagrams
- Text-based representation in terminal output

## Usage

To generate a visual diagram from the PlantUML file:
1. Install PlantUML (https://plantuml.com/)
2. Run: `plantuml erd_diagram.puml`
3. This generates `erd_diagram.png`

## Notes

- All timestamps use UTC
- Currency is Indian Rupees (₹)
- Images are stored as file paths
- JSON fields used for complex data like tracking updates
- SQLite database (can be changed to PostgreSQL/MySQL in production)
