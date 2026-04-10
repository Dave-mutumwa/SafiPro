import frappe
from frappe.utils import random_string

# 1. THE SENDING FUNCTION
@frappe.whitelist(allow_guest=True)
def send_registration_otp(email):
    if frappe.db.exists("User", email):
        return {"status": "error", "message": "Email already registered"}

    # Generate a 4-digit OTP
    otp = random_string(4, digits=True)
    
    # Store in Cache for 10 minutes (600 seconds)
    # Key format: signup_otp:email_address
    frappe.cache().set_value(f"signup_otp:{email}", otp, expires_in_sec=600)
    
    # Send the email immediately
    frappe.sendmail(
        recipients=[email],
        subject="Safi Pro Verification Code",
        content=f"Your 4-digit verification code is: {otp}",
        now=True
    )
    
    return {"status": "success", "message": "OTP sent to your email"}

# 2. THE VERIFICATION & CREATION FUNCTION
@frappe.whitelist(allow_guest=True)
def verify_otp_and_register(email, otp, full_name, password, phone):
    # Retrieve the OTP we stored in Step 1
    cached_otp = frappe.cache().get_value(f"signup_otp:{email}")
    
    if not cached_otp:
        return {"status": "error", "message": "OTP expired. Please request a new one."}
    
    if str(cached_otp) != str(otp):
        return {"status": "error", "message": "Invalid OTP code"}

    # If OTP is correct, create the user
    try:
        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": full_name,
            "mobile_no": phone,
            "new_password": password,
            "enabled": 1,
            "user_type": "Website User"
        })
        user.insert(ignore_permissions=True)
        user.add_roles("Customer")
        
        # Permanent save
        frappe.db.commit()
        
        # Remove OTP from cache so it can't be used again
        frappe.cache().delete_value(f"signup_otp:{email}")
        
        return {"status": "success", "message": "Verification successful! User created."}
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Safi Pro OTP Register Error")
        return {"status": "error", "message": "Registration failed at database level"}

# This keeps your current Flutter app from crashing
@frappe.whitelist(allow_guest=True)
def register_user(email, full_name, password, phone):
    return verify_otp_and_register(email, "0000", full_name, password, phone)
