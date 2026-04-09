import frappe
from frappe.utils import random_string

@frappe.whitelist(allow_guest=True)
def send_registration_otp(email):
    # 1. Check if user exists first
    if frappe.db.exists("User", email):
        frappe.throw("An account with this email already exists.")

    # 2. Generate OTP
    otp = random_string(4, digits=True)
    
    # 3. Store in Cache (Reliable for Frappe Cloud)
    frappe.cache().set_value(f"signup_otp:{email}", otp, expires_in_sec=600)
    
    # 4. Force Send Email
    frappe.sendmail(
        recipients=[email],
        subject="Safi Pro Verification",
        content=f"Your Safi Pro OTP is {otp}",
        now=True  # <--- CRITICAL: Sends immediately
    )
    
    return {"status": "success", "message": "OTP sent successfully"}

@frappe.whitelist(allow_guest=True)
def verify_otp_and_create_user(email, otp, full_name, password):
    # 1. Validate OTP from cache
    cached_otp = frappe.cache().get_value(f"signup_otp:{email}")
    
    if not cached_otp or str(cached_otp) != str(otp):
        return {"status": "error", "message": "Invalid or expired OTP"}

    try:
        # 2. Create the User
        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": full_name,
            "new_password": password,
            "enabled": 1,
            "user_type": "Website User" # Use Website User for customers
        })
        user.insert(ignore_permissions=True)
        
        # 3. Commit to Database
        frappe.db.commit() # <--- CRITICAL: Makes the user permanent
        
        # 4. Clear Cache
        frappe.cache().delete_value(f"signup_otp:{email}")
        
        return {"status": "success", "message": "User created and reflected in backend"}
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Safi Pro Registration Failed")
        return {"status": "error", "message": str(e)}