// Main JavaScript File for Trade Mart

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Product image zoom on hover
    const productImage = document.querySelector('.product-detail-image');
    if (productImage) {
        productImage.addEventListener('mousemove', function(e) {
            const { left, top, width, height } = this.getBoundingClientRect();
            const x = (e.clientX - left) / width * 100;
            const y = (e.clientY - top) / height * 100;
            this.style.transformOrigin = `${x}% ${y}%`;
        });
        
        productImage.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.5)';
        });
        
        productImage.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
            this.style.transformOrigin = 'center center';
        });
    }

    // Flash messages auto-close
    const flashMessages = document.querySelectorAll('.alert-dismissible');
    flashMessages.forEach(function(message) {
        setTimeout(function() {
            const closeButton = message.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });

    // Product filter price range
    const minPriceInput = document.getElementById('min-price');
    const maxPriceInput = document.getElementById('max-price');
    const applyPriceFilterBtn = document.getElementById('apply-price-filter');
    
    if (applyPriceFilterBtn) {
        applyPriceFilterBtn.addEventListener('click', function() {
            const minPrice = minPriceInput.value;
            const maxPrice = maxPriceInput.value;
            
            // Get current URL and parameters
            const url = new URL(window.location.href);
            const params = url.searchParams;
            
            // Update or add min_price and max_price parameters
            if (minPrice) {
                params.set('min_price', minPrice);
            } else {
                params.delete('min_price');
            }
            
            if (maxPrice) {
                params.set('max_price', maxPrice);
            } else {
                params.delete('max_price');
            }
            
            // Redirect to the new URL with updated parameters
            window.location.href = url.toString();
        });
    }

    // Star rating selection for reviews
    const ratingInputs = document.querySelectorAll('.rating-input');
    const ratingStars = document.querySelectorAll('.rating-star');
    
    if (ratingStars.length > 0) {
        ratingStars.forEach(function(star) {
            star.addEventListener('click', function() {
                const value = this.getAttribute('data-value');
                const ratingInput = document.querySelector('input[name="rating"]');
                if (ratingInput) {
                    ratingInput.value = value;
                }
                
                // Update the stars visual
                ratingStars.forEach(function(s) {
                    const starValue = s.getAttribute('data-value');
                    if (starValue <= value) {
                        s.classList.remove('far');
                        s.classList.add('fas');
                    } else {
                        s.classList.remove('fas');
                        s.classList.add('far');
                    }
                });
            });
            
            star.addEventListener('mouseover', function() {
                const value = this.getAttribute('data-value');
                
                // Update the stars visual on hover
                ratingStars.forEach(function(s) {
                    const starValue = s.getAttribute('data-value');
                    if (starValue <= value) {
                        s.classList.remove('far');
                        s.classList.add('fas');
                    } else {
                        s.classList.remove('fas');
                        s.classList.add('far');
                    }
                });
            });
            
            // Reset to the selected value when mouse leaves
            document.querySelector('.rating-stars').addEventListener('mouseleave', function() {
                const selectedValue = document.querySelector('input[name="rating"]').value;
                
                ratingStars.forEach(function(s) {
                    const starValue = s.getAttribute('data-value');
                    if (starValue <= selectedValue) {
                        s.classList.remove('far');
                        s.classList.add('fas');
                    } else {
                        s.classList.remove('fas');
                        s.classList.add('far');
                    }
                });
            });
        });
    }

    // Cart quantity controls
    const minusBtns = document.querySelectorAll('.input-group button:first-child');
    const plusBtns = document.querySelectorAll('.input-group button:last-child');
    const quantityInputs = document.querySelectorAll('.input-group input');

    minusBtns.forEach((btn, index) => {
        btn.addEventListener('click', function() {
            let value = parseInt(quantityInputs[index].value);
            if (value > 1) {
                quantityInputs[index].value = value - 1;
                updateCartItemSubtotal(index);
            }
        });
    });

    plusBtns.forEach((btn, index) => {
        btn.addEventListener('click', function() {
            let value = parseInt(quantityInputs[index].value);
            let max = parseInt(quantityInputs[index].getAttribute('max') || 99);
            if (value < max) {
                quantityInputs[index].value = value + 1;
                updateCartItemSubtotal(index);
            }
        });
    });

    // Update subtotal on quantity change
    function updateCartItemSubtotal(index) {
        const priceElement = document.querySelectorAll('.table-responsive tbody tr td:nth-child(2)')[index];
        const subtotalElement = document.querySelectorAll('.table-responsive tbody tr td:nth-child(4)')[index];
        
        if (priceElement && subtotalElement) {
            const price = parseFloat(priceElement.innerText.replace('$', ''));
            const quantity = parseInt(quantityInputs[index].value);
            const subtotal = price * quantity;
            
            subtotalElement.innerText = '$' + subtotal.toFixed(2);
        }
    }

    // Product image gallery on product detail page
    const thumbnails = document.querySelectorAll('.thumbnail-image');
    const mainImage = document.querySelector('.main-product-image');

    if (thumbnails.length > 0 && mainImage) {
        thumbnails.forEach(thumbnail => {
            thumbnail.addEventListener('click', function() {
                mainImage.src = this.src;
                
                // Remove active class from all thumbnails
                thumbnails.forEach(thumb => {
                    thumb.classList.remove('active');
                });
                
                // Add active class to clicked thumbnail
                this.classList.add('active');
            });
        });
    }

    // Form validation for checkout
    const checkoutForm = document.querySelector('form[action*="checkout"]');
    
    if (checkoutForm) {
        checkoutForm.addEventListener('submit', function(event) {
            if (!validateCheckoutForm()) {
                event.preventDefault();
            }
        });
    }

    function validateCheckoutForm() {
        let isValid = true;
        
        const paymentMethod = document.querySelector('input[name="payment_method"]:checked').value;
        
        // Only validate card fields if payment method is not cash on delivery
        if (paymentMethod !== 'cash_on_delivery') {
            // Card number validation (simple check for 16 digits)
            const cardNumber = document.getElementById('card_number');
            if (cardNumber) {
                const cardNumberValue = cardNumber.value.replace(/\s/g, '');
                if (!/^\d{16}$/.test(cardNumberValue)) {
                    isValid = false;
                    highlightInvalidField(cardNumber, 'Please enter a valid 16-digit card number');
                } else {
                    removeInvalidHighlight(cardNumber);
                }
            }
            
            // Expiration date validation (MM/YY format)
            const expiration = document.getElementById('expiration');
            if (expiration) {
                if (!/^(0[1-9]|1[0-2])\/\d{2}$/.test(expiration.value)) {
                    isValid = false;
                    highlightInvalidField(expiration, 'Please enter a valid expiration date (MM/YY)');
                } else {
                    removeInvalidHighlight(expiration);
                }
            }
            
            // CVV validation (3-4 digits)
            const cvv = document.getElementById('cvv');
            if (cvv) {
                if (!/^\d{3,4}$/.test(cvv.value)) {
                    isValid = false;
                    highlightInvalidField(cvv, 'Please enter a valid CVV (3-4 digits)');
                } else {
                    removeInvalidHighlight(cvv);
                }
            }
        }
        
        return isValid;
    }

    function highlightInvalidField(field, message) {
        field.classList.add('is-invalid');
        
        // Create or update error message
        let errorDiv = field.nextElementSibling;
        if (!errorDiv || !errorDiv.classList.contains('invalid-feedback')) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            field.parentNode.insertBefore(errorDiv, field.nextSibling);
        }
        
        errorDiv.textContent = message;
    }

    function removeInvalidHighlight(field) {
        field.classList.remove('is-invalid');
        
        // Remove error message if exists
        const errorDiv = field.nextElementSibling;
        if (errorDiv && errorDiv.classList.contains('invalid-feedback')) {
            errorDiv.textContent = '';
        }
    }

    // Add to wishlist functionality
    const wishlistBtns = document.querySelectorAll('.btn-outline-primary i.fa-heart');
    
    wishlistBtns.forEach(btn => {
        btn.parentElement.addEventListener('click', function(event) {
            event.preventDefault();
            
            // Toggle filled/outline heart icon
            if (btn.classList.contains('fas')) {
                btn.classList.remove('fas');
                btn.classList.add('far');
                showAlert('Item removed from wishlist', 'warning');
            } else {
                btn.classList.remove('far');
                btn.classList.add('fas');
                showAlert('Item added to wishlist', 'success');
            }
        });
    });

    // Toast notification for wishlist, add to cart, etc.
    function showAlert(message, type) {
        const alertContainer = document.createElement('div');
        alertContainer.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertContainer.style.top = '20px';
        alertContainer.style.right = '20px';
        alertContainer.style.zIndex = '1050';
        
        alertContainer.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        document.body.appendChild(alertContainer);
        
        // Auto-dismiss after 3 seconds
        setTimeout(() => {
            alertContainer.classList.remove('show');
            setTimeout(() => {
                alertContainer.remove();
            }, 300);
        }, 3000);
    }

    // Message Modal Handling
    const messageModal = document.getElementById('messageModal');
    if (messageModal) {
        messageModal.addEventListener('show.bs.modal', function () {
            const messageContent = document.getElementById('message-content');
            if (messageContent) {
                messageContent.focus();
            }
        });

        // Clear form when modal is hidden
        messageModal.addEventListener('hidden.bs.modal', function () {
            const messageForm = messageModal.querySelector('form');
            if (messageForm) {
                messageForm.reset();
            }
        });
    }

    // Handle message form submission
    const messageForm = document.querySelector('#messageModal form');
    if (messageForm) {
        messageForm.addEventListener('submit', function(e) {
            const messageContent = document.getElementById('message-content');
            if (messageContent && !messageContent.value.trim()) {
                e.preventDefault();
                alert('Please enter a message');
                return;
            }
        });
    }
}); 