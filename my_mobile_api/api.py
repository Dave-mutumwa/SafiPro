import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def verify_and_signup(mobile_no, otp, full_name, email=None):
    """
    Verifies the OTP and creates a new User in Frappe.
    """
    # 1. Verify the OTP (Assuming you have a verification logic)
    # This is a placeholder for your OTP verification service
    is_valid = True # Replace with: your_otp_verification_function(mobile_no, otp)
    
    if not is_valid:
        frappe.throw(_("Invalid or expired OTP"), frappe.PermissionError)

    # 2. Check if user already exists
    if frappe.db.exists("User", mobile_no):
        return {
            "status": "failed",
            "message": _("User already exists with this mobile number.")
        }

    # 3. Create the User
    user = frappe.get_doc({
        "doctype": "User",
        "email": email or f"{mobile_no}@example.com",
        "first_name": full_name,
        "enabled": 1,
        "send_welcome_email": 0,
        "user_type": "System User" # Or 'Website User' depending on your needs
    })
    
    user.insert(ignore_permissions=True)
    
    # 4. Set a password or add roles if necessary
    user.add_roles("Customer") 
    
    return {
        "status": "success",
        "message": _("User created successfully"),
        "api_key": user.api_key,
        "api_secret": user.get_password() # Note: Only works if you've set them
    }
