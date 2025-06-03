/**
 * USER JAVASCRIPT - PLATZI INSPIRED DESIGN
 * ========================================
 *
 * This file contains all JavaScript functionality for user-related pages
 * including user forms and user detail pages.
 */

document.addEventListener('DOMContentLoaded', function() {

    // ========================================
    // USER FORM FUNCTIONALITY
    // ========================================

    /**
     * Initialize form validation
     */
    function initFormValidation() {
        const form = document.querySelector('form');
        if (!form) return;

        const inputs = form.querySelectorAll('input, textarea, select');

        inputs.forEach(input => {
            // Validate on blur
            input.addEventListener('blur', function() {
                if (this.value.trim() === '' && this.hasAttribute('required')) {
                    this.classList.add('is-invalid');
                } else {
                    this.classList.remove('is-invalid');
                }
            });

            // Remove invalid class on input
            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid') && this.value.trim() !== '') {
                    this.classList.remove('is-invalid');
                }
            });
        });
    }

    /**
     * Handle file upload preview
     */
    function initFileUploadPreview() {
        const photoInput = document.querySelector('input[type="file"]');
        if (!photoInput) return;

        photoInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = function(e) {
                const avatar = document.querySelector('.profile-avatar, .avatar-placeholder');
                if (avatar) {
                    if (avatar.classList.contains('avatar-placeholder')) {
                        avatar.outerHTML = `<img src="${e.target.result}" class="profile-avatar" alt="Preview">`;
                    } else {
                        avatar.src = e.target.result;
                    }
                }
            };
            reader.readAsDataURL(file);
        });

        // Hide the actual file input
        photoInput.style.display = 'none';
    }

    /**
     * Auto-dismiss alerts
     */
    function initAlertAutoDismiss() {
        setTimeout(function() {
            const alerts = document.querySelectorAll('.alert');
            alerts.forEach(alert => {
                if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
                    const bsAlert = new bootstrap.Alert(alert);
                    bsAlert.close();
                }
            });
        }, 5000);
    }

    // ========================================
    // USER DETAIL FUNCTIONALITY
    // ========================================

    /**
     * Animate progress bars
     */
    function initProgressBarAnimations() {
        const progressBars = document.querySelectorAll('.course-progress-bar, .progress-bar-custom');
        progressBars.forEach(bar => {
            const width = bar.style.width;
            bar.style.width = '0%';
            setTimeout(() => {
                bar.style.width = width;
            }, 500);
        });
    }

    /**
     * Add hover effects to course cards
     */
    function initCourseCardHoverEffects() {
        const courseCards = document.querySelectorAll('.course-card');
        courseCards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-8px)';
            });

            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
            });
        });
    }

    /**
     * Animate statistics on scroll
     */
    function initStatsAnimation() {
        const observerOptions = {
            threshold: 0.5,
            rootMargin: '0px 0px -100px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const statNumbers = entry.target.querySelectorAll('.stat-number');
                    statNumbers.forEach(stat => {
                        const finalValue = parseInt(stat.textContent);
                        if (isNaN(finalValue)) return;

                        let currentValue = 0;
                        const increment = finalValue / 30;

                        const timer = setInterval(() => {
                            currentValue += increment;
                            if (currentValue >= finalValue) {
                                stat.textContent = finalValue;
                                clearInterval(timer);
                            } else {
                                stat.textContent = Math.floor(currentValue);
                            }
                        }, 50);
                    });
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        const profileStats = document.querySelector('.profile-stats');
        if (profileStats) {
            observer.observe(profileStats);
        }
    }

    /**
     * Initialize sidebar navigation effects
     */
    function initSidebarEffects() {
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.addEventListener('mouseenter', function() {
                const icon = this.querySelector('i');
                if (icon) {
                    icon.style.transform = 'scale(1.2) rotate(5deg)';
                }
            });

            item.addEventListener('mouseleave', function() {
                const icon = this.querySelector('i');
                if (icon) {
                    icon.style.transform = 'scale(1) rotate(0deg)';
                }
            });
        });
    }

    /**
     * Initialize action button effects
     */
    function initActionButtonEffects() {
        const actionBtns = document.querySelectorAll('.action-btn');
        actionBtns.forEach(btn => {
            btn.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-3px) scale(1.05)';
            });

            btn.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0) scale(1)';
            });
        });
    }

    /**
     * Initialize subscription card effects
     */
    function initSubscriptionCardEffects() {
        const subscriptionCard = document.querySelector('.subscription-card');
        if (subscriptionCard) {
            subscriptionCard.addEventListener('mouseenter', function() {
                this.style.transform = 'scale(1.02)';
            });

            subscriptionCard.addEventListener('mouseleave', function() {
                this.style.transform = 'scale(1)';
            });
        }
    }

    /**
     * Initialize table row hover effects
     */
    function initTableHoverEffects() {
        const tableRows = document.querySelectorAll('.instructor-table tbody tr');
        tableRows.forEach(row => {
            row.addEventListener('mouseenter', function() {
                this.style.transform = 'translateX(5px)';
            });

            row.addEventListener('mouseleave', function() {
                this.style.transform = 'translateX(0)';
            });
        });
    }

    /**
     * Initialize smooth scrolling for anchor links
     */
    function initSmoothScrolling() {
        const anchorLinks = document.querySelectorAll('a[href^="#"]');
        anchorLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                const targetId = this.getAttribute('href');
                if (targetId === '#') return;

                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    e.preventDefault();
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    /**
     * Initialize loading states for buttons
     */
    function initButtonLoadingStates() {
        const submitButtons = document.querySelectorAll('button[type="submit"]');
        submitButtons.forEach(button => {
            button.addEventListener('click', function() {
                const originalText = this.innerHTML;
                this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
                this.disabled = true;

                // Re-enable after form submission (fallback)
                setTimeout(() => {
                    this.innerHTML = originalText;
                    this.disabled = false;
                }, 3000);
            });
        });
    }

    /**
     * Initialize tooltips for action buttons
     */
    function initTooltips() {
        const tooltipElements = document.querySelectorAll('[title]');
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            tooltipElements.forEach(element => {
                new bootstrap.Tooltip(element);
            });
        }
    }

    /**
     * Initialize copy to clipboard functionality
     */
    function initCopyToClipboard() {
        const copyButtons = document.querySelectorAll('[data-copy]');
        copyButtons.forEach(button => {
            button.addEventListener('click', function() {
                const textToCopy = this.getAttribute('data-copy');
                navigator.clipboard.writeText(textToCopy).then(() => {
                    // Show success feedback
                    const originalText = this.innerHTML;
                    this.innerHTML = '<i class="fas fa-check me-2"></i>Copied!';
                    setTimeout(() => {
                        this.innerHTML = originalText;
                    }, 2000);
                });
            });
        });
    }

    /**
     * Initialize search functionality
     */
    function initSearchFunctionality() {
        const searchInput = document.querySelector('#courseSearch');
        if (searchInput) {
            searchInput.addEventListener('input', function() {
                const searchTerm = this.value.toLowerCase();
                const courseCards = document.querySelectorAll('.course-card');

                courseCards.forEach(card => {
                    const title = card.querySelector('.course-title').textContent.toLowerCase();
                    const instructor = card.querySelector('.course-instructor').textContent.toLowerCase();

                    if (title.includes(searchTerm) || instructor.includes(searchTerm)) {
                        card.closest('.col').style.display = 'block';
                    } else {
                        card.closest('.col').style.display = 'none';
                    }
                });
            });
        }
    }

    /**
     * Initialize keyboard navigation
     */
    function initKeyboardNavigation() {
        document.addEventListener('keydown', function(e) {
            // ESC key to close modals or go back
            if (e.key === 'Escape') {
                const modals = document.querySelectorAll('.modal.show');
                if (modals.length > 0) {
                    modals.forEach(modal => {
                        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
                            const bsModal = bootstrap.Modal.getInstance(modal);
                            if (bsModal) bsModal.hide();
                        }
                    });
                }
            }

            // Ctrl+S to save form
            if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                const submitButton = document.querySelector('button[type="submit"]');
                if (submitButton) {
                    submitButton.click();
                }
            }
        });
    }

    // ========================================
    // INITIALIZATION
    // ========================================

    // Initialize all functionality
    initFormValidation();
    initFileUploadPreview();
    initAlertAutoDismiss();
    initProgressBarAnimations();
    initCourseCardHoverEffects();
    initStatsAnimation();
    initSidebarEffects();
    initActionButtonEffects();
    initSubscriptionCardEffects();
    initTableHoverEffects();
    initSmoothScrolling();
    initButtonLoadingStates();
    initTooltips();
    initCopyToClipboard();
    initSearchFunctionality();
    initKeyboardNavigation();

    // Add a subtle entrance animation to the main container
    const mainContainer = document.querySelector('.profile-container, .profile-form-container');
    if (mainContainer) {
        mainContainer.style.opacity = '0';
        mainContainer.style.transform = 'translateY(20px)';

        setTimeout(() => {
            mainContainer.style.transition = 'all 0.6s ease';
            mainContainer.style.opacity = '1';
            mainContainer.style.transform = 'translateY(0)';
        }, 100);
    }

    // Console log for debugging
    console.log('User page JavaScript initialized successfully');
});
