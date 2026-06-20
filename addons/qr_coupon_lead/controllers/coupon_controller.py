import re
from odoo import http, fields
from odoo.http import request
from odoo.exceptions import ValidationError


class QRCouponController(http.Controller):
    """
    Public QR Coupon Controller

    Handles all public-facing routes for QR coupon scanning and claiming.
    No authentication required - accessible to external customers.

    Security Model:
    - Routes use auth='public' for unauthenticated access
    - sudo() used only for reading public coupon data
    - Input validation on all form submissions
    - CSRF protection automatic via Odoo framework
    - Rate limiting NOT implemented (add at nginx level if needed)

    Routes:
    1. GET /coupon/<code> - Display coupon page
    2. POST /coupon/<code>/claim - Process form submission
    3. GET /coupon/success/<code> - Success page
    4. GET /coupon/error/<error_type> - Error pages
    """

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def _get_client_ip(self):
        """
        Extract client IP address from request.

        Checks in order:
        1. X-Forwarded-For header (if behind proxy)
        2. X-Real-IP header (nginx proxy)
        3. REMOTE_ADDR (direct connection)

        This ensures accurate IP even when behind reverse proxy.
        """
        x_forwarded_for = request.httprequest.headers.get('X-Forwarded-For')
        if x_forwarded_for:
            # May be multiple IPs; take first one
            return x_forwarded_for.split(',')[0].strip()

        x_real_ip = request.httprequest.headers.get('X-Real-IP')
        if x_real_ip:
            return x_real_ip.strip()

        return request.httprequest.remote_addr or '0.0.0.0'

    def _get_user_agent(self):
        """Extract User-Agent header for device tracking"""
        return request.httprequest.headers.get('User-Agent', '')

    def _validate_email(self, email):
        """
        Validate email format using regex.

        Pattern: name@domain.extension
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def _validate_phone(self, phone):
        """
        Validate phone number (basic check).

        Accepts any format with at least 7 digits.
        """
        digits = ''.join(filter(str.isdigit, phone))
        return len(digits) >= 7

    def _validate_name(self, name):
        """
        Validate customer name.

        Requirements:
        - At least 2 characters
        - At most 100 characters
        - Only letters, spaces, hyphens, apostrophes
        """
        name = name.strip()
        if len(name) < 2 or len(name) > 100:
            return False

        # Allow letters (including Unicode), spaces, hyphens, apostrophes
        pattern = r"^[a-zA-Z\s\-']+$"
        return bool(re.match(pattern, name))

    def _build_error_response(self, error_type, coupon_code=None):
        """
        Build error page response.

        Args:
            error_type (str): Type of error ('not_found', 'expired', 'inactive', 'used', 'invalid')
            coupon_code (str): Original coupon code (for context)

        Returns:
            Response: Rendered error template
        """
        error_messages = {
            'not_found': {
                'title': 'Coupon Not Found',
                'message': 'The QR code or coupon code you are looking for does not exist.',
                'type': 'warning',
            },
            'expired': {
                'title': 'Coupon Expired',
                'message': 'This coupon has expired and is no longer available.',
                'type': 'danger',
            },
            'inactive': {
                'title': 'Coupon Inactive',
                'message': 'This coupon is currently inactive.',
                'type': 'warning',
            },
            'used': {
                'title': 'Coupon Limit Reached',
                'message': 'This coupon has reached its maximum usage limit.',
                'type': 'danger',
            },
            'invalid': {
                'title': 'Invalid Coupon',
                'message': 'This coupon is not available for claiming at this time.',
                'type': 'warning',
            },
            'invalid_form': {
                'title': 'Invalid Information',
                'message': 'Please check the information you provided and try again.',
                'type': 'danger',
            },
            'error': {
                'title': 'Error',
                'message': 'An error occurred while processing your request. Please try again.',
                'type': 'danger',
            },
        }

        error_info = error_messages.get(error_type, error_messages['error'])

        return request.render('qr_coupon_lead.error_page', {
            'error_type': error_type,
            'error_title': error_info['title'],
            'error_message': error_info['message'],
            'error_class': error_info['type'],
            'coupon_code': coupon_code,
        })

    # ========================================================================
    # PUBLIC ROUTES
    # ========================================================================

    @http.route('/coupon/<coupon_code>', type='http', auth='public', website=True)
    def view_coupon(self, coupon_code, **kwargs):
        """
        Route: GET /coupon/<coupon_code>

        Display coupon details and claim form to customer.

        Process:
        1. Search for coupon by code (sudo - public access)
        2. Check if coupon exists
        3. Validate coupon status
        4. Render coupon page template
        5. Pass form action URL and coupon details

        Args:
            coupon_code (str): Coupon code from URL (e.g., 'QR00001')

        Returns:
            Response: Rendered coupon page or error page
        """
        # Search for coupon (using sudo for public access)
        coupon = request.env['qr.coupon'].sudo().search([
            ('code', '=', coupon_code.upper())
        ], limit=1)

        # Handle coupon not found
        if not coupon:
            return self._build_error_response('not_found', coupon_code)

        # Handle coupon not valid for claiming
        if not coupon.validate_coupon():
            return self._build_error_response(coupon.status, coupon_code)

        # Render coupon page with form
        return request.render('qr_coupon_lead.coupon_page', {
            'coupon': coupon,
            'form_action': f'/coupon/{coupon_code}/claim',
            'days_until_expiration': coupon.get_days_until_expiration(),
        })

    @http.route(
        '/coupon/<coupon_code>/claim',
        type='http',
        auth='public',
        website=True,
        methods=['POST'],
        csrf=True,
    )
    def claim_coupon(self, coupon_code, **post):
        """
        Route: POST /coupon/<coupon_code>/claim

        Process coupon claim form submission.

        Process:
        1. Extract and validate form data
        2. Search for coupon
        3. Validate coupon status
        4. Validate form inputs
        5. Create CRM Lead
        6. Create scan record
        7. Increment usage counter
        8. Redirect to success page

        Args:
            coupon_code (str): Coupon code from URL
            **post (dict): Form data {name, email, phone, message}

        Returns:
            Response: Redirect to success or error page

        Security:
        - csrf=True: Automatic CSRF token validation
        - sudo(): Used only for creating public lead/scan records
        - Input validation: Email, phone, name format checks
        - Error handling: Graceful error messages
        """
        try:
            # Step 1: Search for coupon
            coupon = request.env['qr.coupon'].sudo().search([
                ('code', '=', coupon_code.upper())
            ], limit=1)

            if not coupon:
                return request.redirect('/coupon/error/not_found')

            # Step 2: Validate coupon
            if not coupon.validate_coupon():
                return request.redirect(f'/coupon/error/{coupon.status}')

            # Step 3: Extract and validate form data
            name = post.get('name', '').strip()
            email = post.get('email', '').strip()
            phone = post.get('phone', '').strip()
            message = post.get('message', '').strip()

            # Validation: Required fields
            if not all([name, email, phone]):
                return request.redirect(f'/coupon/error/invalid_form')

            # Validation: Name format
            if not self._validate_name(name):
                return request.redirect(f'/coupon/error/invalid_form')

            # Validation: Email format
            if not self._validate_email(email):
                return request.redirect(f'/coupon/error/invalid_form')

            # Validation: Phone format
            if not self._validate_phone(phone):
                return request.redirect(f'/coupon/error/invalid_form')

            # Step 4: Prepare customer data
            customer_data = {
                'name': name,
                'email': email,
                'phone': phone,
                'message': message,
                'ip_address': self._get_client_ip(),
                'user_agent': self._get_user_agent(),
            }

            # Step 5: Call coupon model to create lead & scan
            # This method handles all creation logic atomically
            lead_id, scan_id = coupon.sudo().action_claim_coupon(customer_data)

            # Step 6: Redirect to success page
            return request.redirect(f'/coupon/success/{coupon_code}')

        except ValidationError as e:
            return request.redirect(f'/coupon/error/invalid')
        except Exception as e:
            # Log error but don't expose internals to user
            request.env.cr.rollback()
            return request.redirect(f'/coupon/error/error')

    @http.route('/coupon/success/<coupon_code>', type='http', auth='public', website=True)
    def coupon_success(self, coupon_code, **kwargs):
        """
        Route: GET /coupon/success/<coupon_code>

        Display success page after successful coupon claim.

        Shows:
        - Success message
        - Coupon details again (for reference)
        - Discount information
        - Expiration date
        - Thank you message
        - Optional: Next steps or CTAs

        Args:
            coupon_code (str): Coupon code

        Returns:
            Response: Rendered success page
        """
        # Fetch coupon for display (sudo for public access)
        coupon = request.env['qr.coupon'].sudo().search([
            ('code', '=', coupon_code.upper())
        ], limit=1)

        if not coupon:
            return request.redirect('/coupon/error/not_found')

        return request.render('qr_coupon_lead.success_page', {
            'coupon': coupon,
        })

    @http.route('/coupon/error/<error_type>', type='http', auth='public', website=True)
    def coupon_error(self, error_type, **kwargs):
        """
        Route: GET /coupon/error/<error_type>

        Display error page with appropriate error message.

        Args:
            error_type (str): Type of error from kwargs

        Returns:
            Response: Rendered error page
        """
        return self._build_error_response(error_type)
