/**
 * Enhanced Navbar Interactivity
 * Handles smooth scrolling, active link detection, and animations
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize navbar enhancements
    initNavbarEnhancements();
    updateActiveNavLink();
});

/**
 * Initialize navbar enhancement features
 */
function initNavbarEnhancements() {
    const navLinks = document.querySelectorAll('.nav-link-enhanced');
    
    navLinks.forEach(link => {
        link.addEventListener('click', handleNavLinkClick);
        link.addEventListener('mouseover', handleNavLinkHover);
        link.addEventListener('mouseout', handleNavLinkOut);
    });

    // Handle scroll for active link detection
    window.addEventListener('scroll', updateActiveNavLink);
    
    // Close navbar on mobile after link click
    const navbarCollapse = document.querySelector('.navbar-collapse');
    const navbarToggler = document.querySelector('.navbar-toggler');
    
    if (navbarCollapse && navbarToggler) {
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                // Close navbar on mobile after clicking a link
                if (window.innerWidth < 992) {
                    navbarToggler.click();
                }
            });
        });
    }

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#' && document.querySelector(href)) {
                e.preventDefault();
                document.querySelector(href).scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Dropdown animation
    const dropdownToggles = document.querySelectorAll('[data-bs-toggle="dropdown"]');
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('shown.bs.dropdown', function() {
            this.classList.add('active');
        });
        toggle.addEventListener('hidden.bs.dropdown', function() {
            this.classList.remove('active');
        });
    });
}

/**
 * Update active navigation link based on current page
 */
function updateActiveNavLink() {
    const navLinks = document.querySelectorAll('.nav-link-enhanced');
    const currentPath = window.location.pathname;

    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        
        // Remove active class from all links
        link.classList.remove('active');

        // Add active class to current page link
        if (href && (href === currentPath || href === window.location.href)) {
            link.classList.add('active');
        }

        // Check data-link attribute for home page
        const dataLink = link.getAttribute('data-link');
        if (dataLink === 'home' && (currentPath === '/' || currentPath.includes('accueil'))) {
            link.classList.add('active');
        }
    });
}

/**
 * Handle navigation link click
 */
function handleNavLinkClick(event) {
    // Let Bootstrap handle the navigation
    // Just ensure smooth transition
    this.style.transition = 'all 0.2s ease';
}

/**
 * Handle hover effect on nav links
 */
function handleNavLinkHover(event) {
    this.style.transform = 'translateY(-2px)';
}

/**
 * Handle mouse out from nav links
 */
function handleNavLinkOut(event) {
    if (!this.classList.contains('active')) {
        this.style.transform = 'translateY(0)';
    }
}

/**
 * Animate notification badge
 */
function initNotificationBadge() {
    const badge = document.querySelector('.badge');
    if (badge) {
        setInterval(() => {
            badge.style.animation = 'none';
            setTimeout(() => {
                badge.style.animation = 'pulse 2s infinite';
            }, 10);
        }, 5000);
    }
}

/**
 * Enhance dropdown items with icons
 */
function enhanceDropdownItems() {
    const dropdownItems = document.querySelectorAll('.dropdown-item');
    
    dropdownItems.forEach(item => {
        const icon = item.querySelector('i');
        if (icon) {
            icon.style.marginRight = '0.5rem';
            icon.style.minWidth = '20px';
            icon.style.textAlign = 'center';
        }
    });
}

/**
 * Handle navbar scroll behavior
 */
function initNavbarScrollBehavior() {
    const navbar = document.querySelector('.nav-enhanced');
    let lastScrollTop = 0;

    window.addEventListener('scroll', () => {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

        if (scrollTop > 100) {
            navbar.style.boxShadow = '0 8px 24px rgba(46, 74, 47, 0.12)';
        } else {
            navbar.style.boxShadow = '0 4px 16px rgba(46, 74, 47, 0.06)';
        }

        lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
    });
}

// Initialize additional features
window.addEventListener('load', () => {
    initNotificationBadge();
    enhanceDropdownItems();
    initNavbarScrollBehavior();
});

// Export functions for external use if needed
window.NavbarEnhanced = {
    updateActiveNavLink,
    initNavbarEnhancements,
    handleNavLinkClick
};
