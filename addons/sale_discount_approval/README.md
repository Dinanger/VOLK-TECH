# Sale Discount Approval Module for Odoo 18

## Overview
This module prevents sales orders with discounts exceeding 5% from being confirmed without supervisor approval. It implements a complete approval workflow with role-based access control.

## Features

### 1. Discount Threshold Enforcement
- Automatically detects when any order line discount exceeds 5%
- Blocks order confirmation if discount is not approved
- Displays alerts on order forms

### 2. Approval Workflow
- Request Approval: Salesperson requests approval for high discounts
- Approve/Reject: Supervisor can approve or reject discount requests
- Reset: Allows re-submission of approval requests if rejected

### 3. Role-Based Access Control
- Discount Approval Supervisor: Can approve/reject discount requests
- Uses Odoo's built-in security groups system

### 4. User Interface Enhancements
- Form view alerts showing discount status
- Action buttons for approval workflow
- Tree and kanban views with color-coded decorations
- Advanced search filters
- Justification field for discount requests

### 5. Status Tracking
- None: No high discount
- Pending: Awaiting supervisor approval
- Approved: Discount approved by supervisor
- Rejected: Discount rejected

### 6. Notifications
- Mail activities created when approval is requested
- Assigned to supervisor for tracking

## Installation

1. Copy the sale_discount_approval module to your Odoo addons directory
2. Update the app list: Apps > Update Apps List
3. Install the module: Apps > Sale Discount Approval
4. Assign "Discount Approval Supervisor" role to authorized users

## Usage

### For Salespeople:
1. Create a sale order with one or more line items
2. If any line discount > 5%, the order will show a warning
3. Add justification in the "High Discount Reason" field
4. Click "Request Approval" button
5. Once approved, you can confirm the order

### For Supervisors:
1. Navigate to pending approval orders using the filter
2. Review the discount justification
3. Click "Approve Discount" or "Reject Discount"
4. The salesperson will be notified

## Module Structure

```
sale_discount_approval/
├── __init__.py                 # Module initialization
├── __manifest__.py             # Module manifest
├── models/
│   ├── __init__.py
│   └── sale_order.py          # Sale order model extension
├── security/
│   ├── groups.xml             # Security groups definition
│   └── ir.model.access.csv    # Access control list
└── views/
    └── sale_order_views.xml   # UI customizations
```

## Key Methods

In sale_order.py:

- _compute_requires_approval(): Checks if any line discount > 5%
- _check_discount_approval(): Enforces approval before confirmation
- action_request_discount_approval(): Initiates approval workflow
- action_approve_discount(): Supervisor approves discount
- action_reject_discount(): Supervisor rejects discount
- action_reset_discount_approval(): Reset approval status

## Technical Details

### Fields Added to sale.order:
- discount_approval_status: Selection field tracking approval state
- discount_approval_user_id: Many2one to res.users who approved/rejected
- requires_discount_approval: Computed boolean based on line discounts
- high_discount_reason: Text field for justification

### Validation:
- Overrides action_confirm() to check approval before confirmation
- Raises UserError if order has high discount without approval

### Activity/Notifications:
- Creates mail.activity when approval is requested
- Assigns to first available supervisor

## Dependencies
- sale_management (core Odoo module)
- mail (for activity notifications)

## Configuration

No additional configuration required. Simply:
1. Install the module
2. Add users to the "Discount Approval Supervisor" group in their user settings
3. Start using the approval workflow

## Troubleshooting

### "No supervisor found for discount approval"
- Ensure at least one user is assigned to the Discount Approval Supervisor group
- Go to Settings > Users & Companies > Users
- Open a user and add them to the group

### Cannot confirm order message
- Check if discount is > 5%
- Verify the order has pending approval status
- Request approval first, then have a supervisor approve it
