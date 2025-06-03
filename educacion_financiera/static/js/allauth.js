/**
 * ALLAUTH ENHANCED FUNCTIONALITY
 * Platzi-inspired interactive features for authentication forms
 */

document.addEventListener('DOMContentLoaded', function() {

    // Password strength indicator
    initPasswordStrength();

    // Form validation enhancements
    initFormValidation();

    // Loading states for buttons
    initLoadingStates();

    // Auto-focus first input
    initAutoFocus();

    // Social login animations
    initSocialLoginAnimations();

    // Form field animations
    initFieldAnimations();
});

/**
 * Password strength indicator
 */
function initPasswordStrength() {
    const passwordFields = document.querySelectorAll('input[type="password"]');

    passwordFields.forEach(field => {
        if (field.name.includes('password1') || field.name.includes('new_password1')) {
            createPasswordStrengthIndicator(field);
        }
    });
}

function createPasswordStrengthIndicator(passwordField) {
    const container = passwordField.closest('.allauth-form-group');
    if (!container) return;

    const strengthContainer = document.createElement('div');
    strengthContainer.className = 'allauth-password-strength';

    const strengthBar = document.createElement('div');
    strengthBar.className = 'allauth-password-strength-bar';

    strengthContainer.appendChild(strengthBar);
    container.appendChild(strengthContainer);

    passwordField.addEventListener('input', function() {
        const strength = calculatePasswordStrength(this.value);
        updatePasswordStrengthIndicator(strengthBar, strength);
    });
}

function calculatePasswordStrength(password) {
    let score = 0;

    if (password.length >= 8) score += 25;
    if (password.length >= 12) score += 25;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score += 25;
    if (/\d/.test(password)) score += 15;
    if (/[^A-Za-z0-9]/.test(password)) score += 10;

    return Math.min(score, 100);
}

function updatePasswordStrengthIndicator(strengthBar, score) {
    strengthBar.style.width = score + '%';

    // Remove existing strength classes
    strengthBar.classList.remove(
        'allauth-password-strength-weak',
        'allauth-password-strength-medium',
        'allauth-password-strength-strong',
        'allauth-password-strength-very-strong'
    );

    // Add appropriate strength class
    if (score < 30) {
        strengthBar.classList.add('allauth-password-strength-weak');
    } else if (score < 60) {
        strengthBar.classList.add('allauth-password-strength-medium');
    } else if (score < 90) {
        strengthBar.classList.add('allauth-password-strength-strong');
    } else {
        strengthBar.classList.add('allauth-password-strength-very-strong');
    }
}

/**
 * Enhanced form validation
 */
function initFormValidation() {
    const forms = document.querySelectorAll('.allauth-form form');

    forms.forEach(form => {
        const inputs = form.querySelectorAll('input[required]');

        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });

            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    validateField(this);
                }
            });
        });

        form.addEventListener('submit', function(e) {
            let isValid = true;

            inputs.forEach(input => {
                if (!validateField(input)) {
                    isValid = false;
                }
            });

            if (!isValid) {
                e.preventDefault();
                showValidationError();
            }
        });
    });
}

function validateField(field) {
    const value = field.value.trim();
    const isValid = field.checkValidity() && value !== '';

    field.classList.toggle('is-invalid', !isValid);

    // Email specific validation
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        const isValidEmail = emailRegex.test(value);
        field.classList.toggle('is-invalid', !isValidEmail);
        return isValidEmail;
    }

    // Password confirmation validation
    if (field.name.includes('password2')) {
        const password1 = document.querySelector('input[name*="password1"]');
        if (password1) {
            const passwordsMatch = field.value === password1.value;
            field.classList.toggle('is-invalid', !passwordsMatch);
            return passwordsMatch;
        }
    }

    return isValid;
}

function showValidationError() {
    const firstInvalidField = document.querySelector('.form-control.is-invalid');
    if (firstInvalidField) {
        firstInvalidField.focus();
        firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

/**
 * Loading states for buttons
 */
function initLoadingStates() {
    const forms = document.querySelectorAll('.allauth-form form');

    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.classList.add('allauth-btn-loading');
                submitButton.disabled = true;

                // Re-enable after 5 seconds as fallback
                setTimeout(() => {
                    submitButton.classList.remove('allauth-btn-loading');
                    submitButton.disabled = false;
                }, 5000);
            }
        });
    });
}

/**
 * Auto-focus first input
 */
function initAutoFocus() {
    const firstInput = document.querySelector('.allauth-form input:not([type="hidden"]):not([type="checkbox"])');
    if (firstInput) {
        setTimeout(() => {
            firstInput.focus();
        }, 100);
    }
}

/**
 * Social login animations
 */
function initSocialLoginAnimations() {
    const socialButtons = document.querySelectorAll('.allauth-social-btn');

    socialButtons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px) scale(1.02)';
        });

        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
}

/**
 * Field animations and interactions
 */
function initFieldAnimations() {
    const formControls = document.querySelectorAll('.form-control');

    formControls.forEach(control => {
        control.addEventListener('focus', function() {
            this.closest('.allauth-form-group')?.classList.add('focused');
        });

        control.addEventListener('blur', function() {
            this.closest('.allauth-form-group')?.classList.remove('focused');
        });

        // Add filled class for styling
        control.addEventListener('input', function() {
            this.classList.toggle('filled', this.value.trim() !== '');
        });

        // Initial check for pre-filled fields
        if (control.value.trim() !== '') {
            control.classList.add('filled');
        }
    });
}

/**
 * Utility functions
 */

// Show toast notifications
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `allauth-toast allauth-toast-${type}`;
    toast.textContent = message;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('show');
    }, 100);

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 3000);
}

// Smooth scroll to element
function smoothScrollTo(element) {
    element.scrollIntoView({
        behavior: 'smooth',
        block: 'center'
    });
}

// Copy to clipboard functionality
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showToast('Copiado al portapapeles', 'success');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showToast('Copiado al portapapeles', 'success');
    }
}
