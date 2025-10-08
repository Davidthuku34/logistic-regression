// Navigation and Section Management
document.addEventListener('DOMContentLoaded', function() {
    // Initialize navigation
    initializeNavigation();
    
    // Initialize form handling
    initializeFormHandling();
    
    // Initialize animations
    initializeAnimations();
    
    // Initialize responsive menu
    initializeResponsiveMenu();
    
    // Check for URL hash and show appropriate section
    const hash = window.location.hash.replace('#', '');
    if (hash && ['home', 'about', 'services', 'contact'].includes(hash)) {
        showSection(hash);
    } else {
        showSection('home');
    }
});

// Navigation Functions
function initializeNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const href = this.getAttribute('href');
            if (href.startsWith('#')) {
                const section = href.replace('#', '');
                showSection(section);
                updateActiveNavLink(this);
                
                // Close mobile menu if open
                closeMobileMenu();
            }
        });
    });
}

function showSection(sectionName) {
    // Hide all sections
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => {
        section.classList.remove('active');
    });
    
    // Show target section
    const targetSection = document.getElementById(sectionName);
    if (targetSection) {
        targetSection.classList.add('active');
        
        // Update URL hash
        history.pushState(null, null, `#${sectionName}`);
        
        // Update active nav link
        updateActiveNavBySection(sectionName);
        
        // Scroll to top
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
        
        // Trigger section-specific animations
        triggerSectionAnimations(sectionName);
    }
}

function updateActiveNavLink(clickedLink) {
    // Remove active class from all nav links
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => link.classList.remove('active'));
    
    // Add active class to clicked link
    clickedLink.classList.add('active');
}

function updateActiveNavBySection(sectionName) {
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${sectionName}`) {
            link.classList.add('active');
        }
    });
}

// Form Handling
function initializeFormHandling() {
    const predictionForm = document.getElementById('predictionForm');
    if (predictionForm) {
        // Add input validation and formatting
        const inputs = predictionForm.querySelectorAll('input[type="number"]');
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                validateGeneInput(this);
                updateInputState(this);
            });
            
            input.addEventListener('blur', function() {
                formatGeneInput(this);
            });
            
            input.addEventListener('focus', function() {
                this.parentElement.classList.add('focused');
            });
            
            input.addEventListener('blur', function() {
                this.parentElement.classList.remove('focused');
            });
        });
        
        // Form submission handling
        predictionForm.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                showFormError('Please fill in all gene expression values with valid numbers.');
                return;
            }
            
            // Show loading state
            showLoadingState();
        });
    }
    
    // Contact form handling
    const contactForm = document.querySelector('.contact-form form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleContactFormSubmission(this);
        });
    }
}

function validateGeneInput(input) {
    const value = parseFloat(input.value);
    const inputGroup = input.parentElement;
    
    // Remove previous validation classes
    inputGroup.classList.remove('error', 'warning');
    
    if (input.value !== '' && (isNaN(value) || value < 0)) {
        inputGroup.classList.add('error');
        return false;
    }
    
    if (value > 1000) {
        inputGroup.classList.add('warning');
    }
    
    return true;
}

function updateInputState(input) {
    const inputGroup = input.parentElement;
    if (input.value !== '') {
        inputGroup.classList.add('filled');
    } else {
        inputGroup.classList.remove('filled');
    }
}

function formatGeneInput(input) {
    if (input.value !== '') {
        const value = parseFloat(input.value);
        if (!isNaN(value)) {
            input.value = value.toFixed(2);
        }
    }
}

function validateForm(form) {
    const inputs = form.querySelectorAll('input[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.parentElement.classList.add('error');
            isValid = false;
        } else if (input.type === 'number') {
            const value = parseFloat(input.value);
            if (isNaN(value) || value < 0) {
                input.parentElement.classList.add('error');
                isValid = false;
            }
        }
    });
    
    return isValid;
}

function showFormError(message) {
    // Create or update error message
    let errorDiv = document.querySelector('.form-error');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'form-error';
        errorDiv.style.cssText = `
            background: linear-gradient(135deg, #e74c3c, #c0392b);
            color: white;
            padding: 15px 20px;
            margin: 20px 0;
            border-radius: 10px;
            text-align: center;
            font-weight: 500;
            box-shadow: 0 5px 15px rgba(231, 76, 60, 0.3);
        `;
        
        const form = document.getElementById('predictionForm');
        form.parentNode.insertBefore(errorDiv, form);
    }
    
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        if (errorDiv) {
            errorDiv.style.display = 'none';
        }
    }, 5000);
}

function showLoadingState() {
    const submitBtn = document.querySelector('.predict-btn');
    if (submitBtn) {
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
        submitBtn.disabled = true;
        submitBtn.style.opacity = '0.7';
    }
}

function handleContactFormSubmission(form) {
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    // Show success message (in a real app, you'd send to server)
    showContactSuccess();
    
    // Reset form
    form.reset();
}

function showContactSuccess() {
    const contactForm = document.querySelector('.contact-form');
    const successDiv = document.createElement('div');
    successDiv.className = 'contact-success';
    successDiv.style.cssText = `
        background: linear-gradient(135deg, #27ae60, #2ecc71);
        color: white;
        padding: 20px;
        margin: 20px 0;
        border-radius: 15px;
        text-align: center;
        font-weight: 500;
        box-shadow: 0 8px 25px rgba(39, 174, 96, 0.3);
    `;
    successDiv.innerHTML = `
        <i class="fas fa-check-circle" style="font-size: 1.5rem; margin-bottom: 10px;"></i>
        <p style="margin: 0;">Thank you for your message! We'll get back to you soon.</p>
    `;
    
    contactForm.appendChild(successDiv);
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        if (successDiv) {
            successDiv.remove();
        }
    }, 5000);
}

// Animation Functions
function initializeAnimations() {
    // Scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(handleIntersection, observerOptions);
    
    // Observe animated elements
    const animatedElements = document.querySelectorAll('.service-card, .gene-value-item, .contact-item, .stat-item');
    animatedElements.forEach(el => observer.observe(el));
}

function handleIntersection(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}

function triggerSectionAnimations(sectionName) {
    const section = document.getElementById(sectionName);
    if (!section) return;
    
    switch (sectionName) {
        case 'home':
            animateGeneInputs();
            break;
        case 'about':
            animateAboutStats();
            break;
        case 'services':
            animateServiceCards();
            break;
        case 'contact':
            animateContactItems();
            break;
    }
}

function animateGeneInputs() {
    const inputs = document.querySelectorAll('.input-group');
    inputs.forEach((input, index) => {
        input.style.opacity = '0';
        input.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            input.style.transition = 'all 0.6s ease';
            input.style.opacity = '1';
            input.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

function animateAboutStats() {
    const stats = document.querySelectorAll('.about-stats .stat-item');
    stats.forEach((stat, index) => {
        stat.style.opacity = '0';
        stat.style.transform = 'translateX(-20px)';
        
        setTimeout(() => {
            stat.style.transition = 'all 0.5s ease';
            stat.style.opacity = '1';
            stat.style.transform = 'translateX(0)';
        }, index * 150);
    });
}

function animateServiceCards() {
    const cards = document.querySelectorAll('.service-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.6s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

function animateContactItems() {
    const items = document.querySelectorAll('.contact-item');
    items.forEach((item, index) => {
        item.style.opacity = '0';
        item.style.transform = 'translateX(-30px)';
        
        setTimeout(() => {
            item.style.transition = 'all 0.5s ease';
            item.style.opacity = '1';
            item.style.transform = 'translateX(0)';
        }, index * 100);
    });
}

// Responsive Menu
function initializeResponsiveMenu() {
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    
    if (hamburger && navMenu) {
        hamburger.addEventListener('click', function() {
            toggleMobileMenu();
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!hamburger.contains(e.target) && !navMenu.contains(e.target)) {
                closeMobileMenu();
            }
        });
        
        // Close menu on window resize
        window.addEventListener('resize', function() {
            if (window.innerWidth > 1024) {
                closeMobileMenu();
            }
        });
    }
}

function toggleMobileMenu() {
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    
    hamburger.classList.toggle('active');
    navMenu.classList.toggle('active');
    
    // Add mobile menu styles if not already present
    if (!document.querySelector('#mobile-menu-styles')) {
        const style = document.createElement('style');
        style.id = 'mobile-menu-styles';
        style.textContent = `
            .hamburger.active .bar:nth-child(2) {
                opacity: 0;
            }
            .hamburger.active .bar:nth-child(1) {
                transform: translateY(8px) rotate(45deg);
            }
            .hamburger.active .bar:nth-child(3) {
                transform: translateY(-8px) rotate(-45deg);
            }
            @media (max-width: 1024px) {
                .nav-menu {
                    position: fixed;
                    left: -100%;
                    top: 70px;
                    flex-direction: column;
                    background: rgba(44, 62, 80, 0.98);
                    width: 100%;
                    text-align: center;
                    transition: 0.3s;
                    box-shadow: 0 10px 27px rgba(0, 0, 0, 0.05);
                    backdrop-filter: blur(10px);
                    padding: 20px 0;
                }
                .nav-menu.active {
                    left: 0;
                }
                .nav-item {
                    margin: 10px 0;
                }
                .nav-link {
                    padding: 15px 20px;
                    display: flex;
                    justify-content: center;
                }
            }
        `;
        document.head.appendChild(style);
    }
}

function closeMobileMenu() {
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    
    if (hamburger && navMenu) {
        hamburger.classList.remove('active');
        navMenu.classList.remove('active');
    }
}

// Utility Functions
function smoothScrollTo(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Handle form validation styles
function addValidationStyles() {
    if (!document.querySelector('#validation-styles')) {
        const style = document.createElement('style');
        style.id = 'validation-styles';
        style.textContent = `
            .input-group.error {
                border-color: #e74c3c !important;
                box-shadow: 0 0 0 3px rgba(231, 76, 60, 0.2) !important;
            }
            .input-group.warning {
                border-color: #f39c12 !important;
                box-shadow: 0 0 0 3px rgba(243, 156, 18, 0.2) !important;
            }
            .input-group.filled {
                border-color: #27ae60 !important;
            }
            .input-group.focused {
                border-color: #3498db !important;
                box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2) !important;
            }
        `;
        document.head.appendChild(style);
    }
}

// Initialize validation styles
addValidationStyles();

// Handle page navigation
window.addEventListener('popstate', function() {
    const hash = window.location.hash.replace('#', '');
    if (hash && ['home', 'about', 'services', 'contact'].includes(hash)) {
        showSection(hash);
    } else {
        showSection('home');
    }
});

// Add loading state for external links
document.addEventListener('click', function(e) {
    if (e.target.matches('a[href^="http"]')) {
        const link = e.target;
        const originalText = link.innerHTML;
        link.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
        
        setTimeout(() => {
            link.innerHTML = originalText;
        }, 2000);
    }
});

// Add copy functionality for gene IDs
document.addEventListener('click', function(e) {
    if (e.target.matches('.gene-id')) {
        const geneId = e.target.textContent;
        if (navigator.clipboard) {
            navigator.clipboard.writeText(geneId).then(() => {
                showTooltip(e.target, 'Copied!');
            });
        }
    }
});

function showTooltip(element, message) {
    const tooltip = document.createElement('div');
    tooltip.textContent = message;
    tooltip.style.cssText = `
        position: absolute;
        background: #2c3e50;
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        font-size: 0.8rem;
        z-index: 1000;
        pointer-events: none;
        opacity: 0;
        transition: opacity 0.3s ease;
    `;
    
    document.body.appendChild(tooltip);
    
    const rect = element.getBoundingClientRect();
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
    tooltip.style.top = rect.bottom + 10 + 'px';
    
    setTimeout(() => tooltip.style.opacity = '1', 10);
    
    setTimeout(() => {
        tooltip.style.opacity = '0';
        setTimeout(() => document.body.removeChild(tooltip), 300);
    }, 2000);
}

// Global function for external access
window.showSection = showSection;