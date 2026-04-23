/* ============================================
   HANI SHOPPING - COOKIE / JS (DJANGO VERSION)
   ============================================ */

let currentSlide = 0;
let sliderInterval = null;

document.addEventListener('DOMContentLoaded', () => {
    initSlider();
    // updateCartUI(); // Trộn lẫn với Django, sẽ load sau
});

// =================== SLIDER ===================
function initSlider() {
    const slides = document.querySelectorAll('.slide');
    const dotsContainer = document.getElementById('slider-dots');
    if (!dotsContainer) return;

    dotsContainer.innerHTML = '';
    slides.forEach((_, i) => {
        const dot = document.createElement('div');
        dot.className = 'slider-dot' + (i === 0 ? ' active' : '');
        dot.onclick = () => goToSlide(i);
        dotsContainer.appendChild(dot);
    });

    startSliderAutoplay();
}

function goToSlide(index) {
    const slides = document.querySelectorAll('.slide');
    const dots = document.querySelectorAll('.slider-dot');
    if (slides.length === 0) return;

    currentSlide = index;
    if (currentSlide >= slides.length) currentSlide = 0;
    if (currentSlide < 0) currentSlide = slides.length - 1;

    const track = document.getElementById('slider-track');
    if (track) track.style.transform = `translateX(-${currentSlide * 100}%)`;

    dots.forEach((d, i) => d.classList.toggle('active', i === currentSlide));
}

function nextSlide() { goToSlide(currentSlide + 1); startSliderAutoplay(); }
function prevSlide() { goToSlide(currentSlide - 1); startSliderAutoplay(); }
function startSliderAutoplay() {
    if (sliderInterval) clearInterval(sliderInterval);
    sliderInterval = setInterval(() => goToSlide(currentSlide + 1), 5000);
}

// =================== CART ===================
function openCart() {
    document.getElementById('cart-overlay').classList.add('open');
    document.getElementById('cart-sidebar').classList.add('open');
    document.body.style.overflow = 'hidden';
    updateCartUI();
}

function closeCart() {
    document.getElementById('cart-overlay').classList.remove('open');
    document.getElementById('cart-sidebar').classList.remove('open');
    document.body.style.overflow = '';
}

function handleCouponToggle() {
    // Ưu tiên dùng biến global, nếu chưa có thì cào DOM
    const count = (typeof window.currentCartCount !== 'undefined') ? window.currentCartCount : (function() {
        const badge = document.getElementById('cart-badge');
        const countText = badge ? badge.textContent.trim() : '0';
        const sidebarCount = document.getElementById('cart-count-sidebar');
        const countTextSidebar = sidebarCount ? sidebarCount.textContent.trim() : '0';
        return parseInt(countText) || parseInt(countTextSidebar) || 0;
    })();
    
    if (count > 0) {
        if (typeof toggleCouponList === 'function') {
            toggleCouponList();
        } else {
            console.error('toggleCouponList not defined');
        }
    } else {
        showToast('info', null, 'Vui lòng thêm sản phẩm vào giỏ hàng trước khi chọn mã!');
    }
}

let isCartEditMode = false;

function toggleCartEditMode() {
    isCartEditMode = !isCartEditMode;
    const btn = document.getElementById('btn-edit-cart');
    if(btn) {
        btn.textContent = isCartEditMode ? 'Xong' : 'Sửa';
    }
    updateCartUI(); // Re-render to show/hide trash bins
}

function updateCartUI() {
    fetch('/cart/data/')
    .then(res => res.json())
    .then(data => {
        const badge = document.getElementById('cart-badge');
        if(badge) {
            badge.textContent = data.count;
            badge.classList.toggle('show', data.count > 0);
        }
        
        const countSidebar = document.getElementById('cart-count-sidebar');
        if(countSidebar) countSidebar.textContent = data.count;

        const totalPrice = document.getElementById('cart-total-price');
        if(totalPrice) totalPrice.textContent = data.total_formatted;

        const container = document.getElementById('cart-items');
        if (!container) return;

        if (data.items.length === 0) {
            container.innerHTML = `<div style="padding:40px;text-align:center;color:#a0a0a0;"><p>Giỏ hàng trống</p></div>`;
            document.getElementById('cart-selected-info').textContent = 'Bạn đã chọn 0 sản phẩm';
            isCartEditMode = false; // Turn off edit mode if cart is empty
            const btn = document.getElementById('btn-edit-cart');
            if(btn) btn.textContent = 'Sửa';
        } else {
            const selectedCount = data.items.filter(i => i.selected).length;
            document.getElementById('cart-selected-info').textContent = `Bạn đã chọn ${selectedCount} sản phẩm`;
            
            container.innerHTML = data.items.map((item, index) => `
                <div class="cart-item">
                    <div class="cart-item-check" style="${isCartEditMode ? 'display:none;' : ''}">
                        <label class="custom-checkbox">
                            <input type="checkbox" ${item.selected ? 'checked' : ''} 
                                   onchange="updateCartItemqty(${index}, 'toggle', ${item.product_id}, '${item.color}', '${item.size}')">
                            <span class="checkmark"></span>
                        </label>
                    </div>
                    <div class="cart-item-image" onclick="location.href='/product/${item.product_id}/'" style="cursor:pointer;"><img src="/static/images/${item.image}"></div>
                    <div class="cart-item-info">
                        <div class="cart-item-name" onclick="location.href='/product/${item.product_id}/'" style="cursor:pointer;">${item.name}</div>
                        <div class="cart-item-variant" style="margin-top: 8px;">
                            <div class="cart-custom-select" id="variant-select-${index}">
                                <div class="custom-select-trigger" onclick="toggleCustomSelect(${index})">
                                    ${item.color} | ${item.size}
                                </div>
                                <div class="custom-select-options">
                                    <div class="custom-optgroup-label">MÀU SẮC</div>
                                    ${item.available_colors.map(c => `
                                        <div class="custom-option ${c.name === item.color ? 'selected' : ''}" 
                                             onclick="changeCartVariant(${item.product_id}, '${item.color}', '${item.size}', '${c.name}', '${item.size}')">
                                            ${c.name}
                                        </div>
                                    `).join('')}
                                    <div class="custom-optgroup-label">KÍCH THƯỚC</div>
                                    ${item.available_sizes.map(s => `
                                        <div class="custom-option ${s === item.size ? 'selected' : ''}" 
                                             onclick="changeCartVariant(${item.product_id}, '${item.color}', '${item.size}', '${item.color}', '${s}')">
                                            ${s}
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        </div>
                        <div class="cart-item-price-row">
                            <span class="cart-item-price">${item.price_formatted}</span>
                            <div class="cart-item-qty">
                                <button class="qty-btn" onclick="updateCartItemqty(${index}, 'decrease', ${item.product_id}, '${item.color}', '${item.size}')">−</button>
                                <span class="qty-value">${item.qty}</span>
                                <button class="qty-btn" onclick="updateCartItemqty(${index}, 'increase', ${item.product_id}, '${item.color}', '${item.size}')">+</button>
                            </div>
                        </div>
                    </div>
                    <div class="cart-item-del" style="display: ${isCartEditMode ? 'flex' : 'none'}; align-items: center; justify-content: center; width: 40px;">
                        <button onclick="updateCartItemqty(${index}, 'delete', ${item.product_id}, '${item.color}', '${item.size}')" style="background:none; border:none; color:var(--red); font-size:18px; cursor:pointer;" title="Xóa">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    </div>
                </div>
            `).join('');
        }
        
        // Lưu số lượng vào window để dùng ở bất cứ đâu
        window.currentCartCount = data.count;
        window.currentSelectedCount = data.selected_count;

        // Cập nhật trạng thái dòng mã ưu đãi
        const couponRow = document.getElementById('coupon-toggle-row');
        const couponLabel = document.getElementById('selected-coupon-label');
        if (couponRow) {
            // CẬP NHẬT TRẠNG THÁI MÃ ƯU ĐÃI THEO VIỆC CHỌN SẢN PHẨM
            const isDisabled = (data.selected_count === 0);
            couponRow.style.opacity = isDisabled ? '0.6' : '1';
            couponRow.style.cursor = isDisabled ? 'not-allowed' : 'pointer';
            
            // Bắt buộc về mặc định khi không có SP được chọn hoặc giỏ hàng trống
            if (isDisabled && couponLabel) {
                const currentLabel = couponLabel.textContent.trim();
                // Chỉ gọi fetch nếu thực sự có mã đang áp dụng
                if (currentLabel !== 'Chọn hoặc nhập mã') {
                    couponLabel.textContent = 'Chọn hoặc nhập mã';
                    fetch('/apply-coupon/', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
                        body: JSON.stringify({ code: '' })
                    });
                }
                couponLabel.style.color = 'var(--gray-500)';
                couponLabel.style.fontWeight = '400';
            }
        }
    });
}

function updateCartItemqty(index, action, product_id, color, size) {
    fetch('/cart/update/', {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ product_id, color, size, action })
    })
    .then(res => res.json())
    .then(data => { if (data.success) updateCartUI(); });
}

function toggleCustomSelect(index) {
    const el = document.getElementById(`variant-select-${index}`);
    const isActive = el.classList.contains('active');
    
    // Close all other custom selects first
    document.querySelectorAll('.cart-custom-select').forEach(s => s.classList.remove('active'));
    
    if (!isActive) {
        el.classList.add('active');
    }
}

// Global click handler to close custom selects when clicking outside
document.addEventListener('click', (e) => {
    if (!e.target.closest('.cart-custom-select')) {
        document.querySelectorAll('.cart-custom-select').forEach(s => s.classList.remove('active'));
    }
});

function changeCartVariant(product_id, old_color, old_size, new_color, new_size) {
    if (old_color === new_color && old_size === new_size) return;
    
    fetch('/cart/update/', {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ 
            product_id, 
            color: old_color, 
            size: old_size, 
            new_color, 
            new_size, 
            action: 'change_variant' 
        })
    })
    .then(res => res.json())
    .then(data => { 
        if (data.success) {
            updateCartUI();
            showToast('info', null, 'Đã cập nhật phân loại sản phẩm');
        }
    });
}

function toggleSelectAll() {
    const checked = document.getElementById('select-all-cart').checked;
    fetch('/cart/update/', {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ action: 'toggle_all', checked: checked })
    })
    .then(res => res.json())
    .then(data => { if (data.success) updateCartUI(); });
}

function showToast(type, product = null, message = '') {
    const container = document.getElementById('toast-container');
    if(!container) return;
    
    let toastHTML = '';
    
    if (type === 'add-to-cart' && product) {
        toastHTML = `
            <div class="toast">
                <div class="toast-content">
                    <div class="toast-image">
                        <img src="${product.image}">
                    </div>
                    <div class="toast-message">
                        Đã thêm sản phẩm vào giỏ hàng!
                    </div>
                    <button class="toast-btn-view" onclick="openCart(); this.closest('.toast').remove();">
                        Xem giỏ hàng
                    </button>
                </div>
            </div>
        `;
    } else {
        toastHTML = `
            <div class="toast">
                <div class="toast-content" style="padding: 15px 25px; min-width: 300px; display: flex; align-items: center; gap: 10px;">
                    <i class="fas fa-info-circle" style="color: #4a90e2;"></i>
                    <div class="toast-message" style="font-size: 15px;">${message || 'Thành công!'}</div>
                </div>
            </div>
        `;
    }

    const div = document.createElement('div');
    div.innerHTML = toastHTML;
    const toastElement = div.firstElementChild;
    container.appendChild(toastElement);
    
    // Auto remove after 4.5s
    setTimeout(() => { 
        if(container.contains(toastElement)) toastElement.remove(); 
    }, 4500);
}



// =================== MOBILE MENU ===================
document.addEventListener('DOMContentLoaded', () => {
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const closeMobileMenu = document.getElementById('closeMobileMenu');
    const navBar = document.getElementById('navBar');
    const navOverlay = document.getElementById('navOverlay');

    if (mobileMenuToggle && navBar && navOverlay) {
        mobileMenuToggle.addEventListener('click', () => {
            navBar.classList.add('open');
            navOverlay.classList.add('open');
            document.body.style.overflow = 'hidden';
        });

        const closeMenu = () => {
            navBar.classList.remove('open');
            navOverlay.classList.remove('open');
            document.body.style.overflow = '';
        };

        if (closeMobileMenu) {
            closeMobileMenu.addEventListener('click', closeMenu);
        }
        navOverlay.addEventListener('click', closeMenu);
        
        // ��ng menu khi nh?n v�o link (d?i v?i single page apps ho?c anchors)
        navBar.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', closeMenu);
        });
    }
});

