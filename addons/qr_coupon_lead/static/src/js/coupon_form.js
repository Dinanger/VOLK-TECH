/**
 * QR Coupon Lead - Form Validation & Enhancement
 *
 * Client-side validation for coupon claim form:
 * - Real-time field validation
 * - Format checking (email, phone)
 * - User feedback & error messages
 * - Submit button state management
 */

(function() {
    'use strict';

    // Wait for DOM to be ready
    document.addEventListener('DOMContentLoaded', function() {
        initializeCouponForm();
    });

    /**
     * Initialize form validation and event handlers
     */
    function initializeCouponForm() {
        var form = document.getElementById('coupon_claim_form');
        if (!form) return;

        // Add real-time validation listeners
        var nameInput = document.getElementById('input_name');
        var emailInput = document.getElementById('input_email');
        var phoneInput = document.getElementById('input_phone');
        var termsCheckbox = document.getElementById('agree_terms');

        if (nameInput) {
            nameInput.addEventListener('blur', validateName);
            nameInput.addEventListener('input', validateName);
        }

        if (emailInput) {
            emailInput.addEventListener('blur', validateEmail);
            emailInput.addEventListener('input', validateEmail);
        }

        if (phoneInput) {
            phoneInput.addEventListener('blur', validatePhone);
            phoneInput.addEventListener('input', validatePhone);
        }

        // Form submission handler
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });

        // Enable/disable submit button based on form state
        if (termsCheckbox) {
            termsCheckbox.addEventListener('change', updateSubmitButtonState);
        }

        // Update submit button state initially
        updateSubmitButtonState();
    }

    /**
     * Validate name field
     * - At least 2 characters
     * - Maximum 100 characters
     * - Only letters, spaces, hyphens, apostrophes
     */
    function validateName() {
        var input = document.getElementById('input_name');
        if (!input) return;

        var value = input.value.trim();
        var isValid = true;
        var message = '';

        if (value.length === 0) {
            isValid = false;
            message = 'Name is required';
        } else if (value.length < 2) {
            isValid = false;
            message = 'Name must be at least 2 characters';
        } else if (value.length > 100) {
            isValid = false;
            message = 'Name must be less than 100 characters';
        } else if (!/^[a-zA-Z\s\-']+$/.test(value)) {
            isValid = false;
            message = 'Name can only contain letters, spaces, hyphens, and apostrophes';
        }

        setFieldValidity(input, isValid, message);
        return isValid;
    }

    /**
     * Validate email field
     * - Valid email format (basic regex)
     */
    function validateEmail() {
        var input = document.getElementById('input_email');
        if (!input) return;

        var value = input.value.trim();
        var isValid = true;
        var message = '';

        if (value.length === 0) {
            isValid = false;
            message = 'Email is required';
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
            isValid = false;
            message = 'Please enter a valid email address';
        }

        setFieldValidity(input, isValid, message);
        return isValid;
    }

    /**
     * Validate phone field
     * - At least 7 digits
     * - Accepts various formats
     */
    function validatePhone() {
        var input = document.getElementById('input_phone');
        if (!input) return;

        var value = input.value.trim();
        var isValid = true;
        var message = '';

        // Extract only digits
        var digits = value.replace(/\D/g, '');

        if (value.length === 0) {
            isValid = false;
            message = 'Phone number is required';
        } else if (digits.length < 7) {
            isValid = false;
            message = 'Phone number must contain at least 7 digits';
        }

        setFieldValidity(input, isValid, message);
        return isValid;
    }

    /**
     * Update field validity state
     * - Add/remove Bootstrap validation classes
     * - Update error message
     */
    function setFieldValidity(field, isValid, message) {
        if (isValid) {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
            // Clear error message if exists
            var feedback = field.parentElement.querySelector('.invalid-feedback');
            if (feedback) {
                feedback.textContent = feedback.getAttribute('data-default') || 'Please check this field';
            }
        } else {
            field.classList.remove('is-valid');
            field.classList.add('is-invalid');
            // Update error message
            var feedback = field.parentElement.querySelector('.invalid-feedback');
            if (feedback) {
                feedback.textContent = message;
            }
        }
    }

    /**
     * Update submit button state based on form completeness
     */
    function updateSubmitButtonState() {
        var form = document.getElementById('coupon_claim_form');
        var submitBtn = document.getElementById('submit_claim');
        var termsCheckbox = document.getElementById('agree_terms');

        if (!form || !submitBtn) return;

        var nameInput = document.getElementById('input_name');
        var emailInput = document.getElementById('input_email');
        var phoneInput = document.getElementById('input_phone');

        var isFormComplete = (
            (nameInput && nameInput.value.trim().length > 0) &&
            (emailInput && emailInput.value.trim().length > 0) &&
            (phoneInput && phoneInput.value.trim().length > 0) &&
            (termsCheckbox && termsCheckbox.checked)
        );

        if (isFormComplete) {
            submitBtn.disabled = false;
            submitBtn.classList.remove('disabled');
        } else {
            submitBtn.disabled = true;
            submitBtn.classList.add('disabled');
        }
    }

    // Attach to window for debugging
    window.CouponForm = {
        validateName: validateName,
        validateEmail: validateEmail,
        validatePhone: validatePhone,
        updateSubmitButtonState: updateSubmitButtonState
    };

})();

/**
 * Format phone number as user types
 * Provides visual feedback for phone input
 */
document.addEventListener('DOMContentLoaded', function() {
    var phoneInput = document.getElementById('input_phone');
    if (!phoneInput) return;

    phoneInput.addEventListener('input', function(e) {
        var value = e.target.value.replace(/\D/g, '');

        if (value.length <= 3) {
            e.target.value = value;
        } else if (value.length <= 6) {
            e.target.value = '(' + value.substring(0, 3) + ') ' + value.substring(3);
        } else if (value.length <= 10) {
            e.target.value = '(' + value.substring(0, 3) + ') ' + value.substring(3, 6) + '-' + value.substring(6);
        } else {
            e.target.value = '(' + value.substring(0, 3) + ') ' + value.substring(3, 6) + '-' + value.substring(6, 10);
        }
    });
});
