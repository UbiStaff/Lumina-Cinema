// 导航栏功能
function initNavbar() {
    // 移动端汉堡菜单
    const burger = document.querySelector('.burger');
    const navLinks = document.querySelector('.nav-links');
    
    if (burger && navLinks) {
        burger.addEventListener('click', () => {
            navLinks.classList.toggle('nav-active');
            
            // 添加动画效果
            const links = navLinks.querySelectorAll('li');
            links.forEach((link, index) => {
                if (link.style.animation) {
                    link.style.animation = '';
                } else {
                    link.style.animation = `navLinkFade 0.5s ease forwards ${index / 7 + 0.3}s`;
                }
            });
            
            // 汉堡菜单动画
            burger.classList.toggle('toggle');
        });
    }
    
    // 点击导航链接后关闭菜单
    const navItems = document.querySelectorAll('.nav-links a');
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            if (navLinks.classList.contains('nav-active')) {
                navLinks.classList.remove('nav-active');
                burger.classList.remove('toggle');
                
                // 清除动画
                const links = navLinks.querySelectorAll('li');
                links.forEach(link => {
                    link.style.animation = '';
                });
            }
        });
    });
}

// 选座功能
function initSeatSelection() {
    const seats = document.querySelectorAll('.seat:not(.occupied)');
    const selectedSeats = document.getElementById('selected-seats');
    const totalPrice = document.getElementById('total-price');
    const seatIdsInput = document.getElementById('seat_ids'); // 修改id从seat-ids为seat_ids
    const submitBtn = document.getElementById('submit-btn');
    
    if (seats.length > 0) {
        // 获取票价，添加空值检查以避免TypeError
        const ticketPriceElement = document.getElementById('ticket-price');
        const ticketPrice = ticketPriceElement ? parseFloat(ticketPriceElement.textContent) || 0 : 0;
        let selectedSeatIds = [];
        
        function updateSelectedCount() {
            const selectedSeatCount = selectedSeatIds.length;
            
            // 添加空值检查，避免TypeError
            if (selectedSeats) {
                selectedSeats.textContent = selectedSeatCount;
            }
            
            if (totalPrice) {
                totalPrice.textContent = (selectedSeatCount * ticketPrice).toFixed(2);
            }
            
            if (selectedSeatCount > 0) {
                if (submitBtn) {
                    submitBtn.disabled = false;
                }
                if (seatIdsInput) {
                    seatIdsInput.value = selectedSeatIds.join(',');
                }
            } else {
                if (submitBtn) {
                    submitBtn.disabled = true;
                }
                if (seatIdsInput) {
                    seatIdsInput.value = '';
                }
            }
        }
        
        seats.forEach(seat => {
            seat.addEventListener('click', () => {
                const seatId = parseInt(seat.dataset.seatId);
                
                if (seat.classList.contains('selected')) {
                    // 取消选择
                    seat.classList.remove('selected');
                    selectedSeatIds = selectedSeatIds.filter(id => id !== seatId);
                } else {
                    // 选择座位
                    seat.classList.add('selected');
                    selectedSeatIds.push(seatId);
                }
                
                updateSelectedCount();
            });
        });
    }
}

// 影评点赞功能
function initReviewLikes() {
    const likeButtons = document.querySelectorAll('.like-btn');
    
    likeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const reviewId = this.dataset.reviewId;
            
            fetch(`/review/${reviewId}/like`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                const likeCount = this.querySelector('span:last-child');
                likeCount.textContent = data.likes;
                
                if (data.status === 'liked') {
                    this.classList.add('liked');
                } else {
                    this.classList.remove('liked');
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });
}

// 表单验证功能
function initFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            // 简单的表单验证
            const inputs = form.querySelectorAll('input[required], textarea[required]');
            let isValid = true;
            
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.classList.add('invalid');
                } else {
                    input.classList.remove('invalid');
                }
            });
            
            // 密码确认验证
            const password = form.querySelector('input[name="password"]');
            const confirmPassword = form.querySelector('input[name="confirm_password"]');
            
            if (password && confirmPassword) {
                if (password.value !== confirmPassword.value) {
                    isValid = false;
                    password.classList.add('invalid');
                    confirmPassword.classList.add('invalid');
                    alert('两次输入的密码不一致');
                    e.preventDefault();
                }
            }
            
            if (!isValid) {
                e.preventDefault();
                alert('请填写所有必填字段');
            }
        });
        
        // 输入时移除错误状态
        const inputs = form.querySelectorAll('input, textarea');
        inputs.forEach(input => {
            input.addEventListener('input', () => {
                input.classList.remove('invalid');
            });
        });
    });
}

// 获取CSRF令牌
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// 页面加载完成后初始化所有功能
document.addEventListener('DOMContentLoaded', () => {
    initNavbar();
    initReviewLikes();
    initFormValidation();
    
    // 根据页面路径初始化特定功能
    const path = window.location.pathname;
    
    if (path.includes('select_seats')) {
        initSeatSelection();
    }
    
    if (path.includes('movie_detail')) {
        initReviewLikes();
    }
});

// 添加滚动监听事件
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('nav');
    
    if (navbar) {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    }
});

// 添加平滑滚动效果
function smoothScroll(target, duration) {
    const targetElement = document.querySelector(target);
    const targetPosition = targetElement.offsetTop;
    const startPosition = window.pageYOffset;
    const distance = targetPosition - startPosition;
    let startTime = null;
    
    function animation(currentTime) {
        if (startTime === null) startTime = currentTime;
        const timeElapsed = currentTime - startTime;
        const run = ease(timeElapsed, startPosition, distance, duration);
        window.scrollTo(0, run);
        if (timeElapsed < duration) requestAnimationFrame(animation);
    }
    
    function ease(t, b, c, d) {
        t /= d / 2;
        if (t < 1) return c / 2 * t * t + b;
        t--;
        return -c / 2 * (t * (t - 2) - 1) + b;
    }
    
    requestAnimationFrame(animation);
}

// 添加动画效果到页面元素
function animateOnScroll() {
    const elements = document.querySelectorAll('.card, .movie-detail, .screenings, .seat-selection, .order-confirmation, .reviews');
    
    elements.forEach(element => {
        const elementPosition = element.getBoundingClientRect().top;
        const screenPosition = window.innerHeight / 1.3;
        
        if (elementPosition < screenPosition) {
            element.classList.add('slide-in-up');
        }
    });
}

// 页面滚动时触发动画
window.addEventListener('scroll', animateOnScroll);

// 页面加载时触发动画
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(animateOnScroll, 300);
});