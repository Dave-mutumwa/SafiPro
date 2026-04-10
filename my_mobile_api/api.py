import frappe
from frappe.utils import random_string

@frappe.whitelist(allow_guest=True)
def send_registration_otp(email):
    if frappe.db.exists("User", email):
        return {"status": "error", "message": "Email already registered"}

    otp = random_string(4, digits=True)
    frappe.cache().set_value(f"signup_otp:{email}", otp, expires_in_sec=600)

    frappe.sendmail(
        recipients=[email],
        subject="Safi Pro Verification Code",
        content=f"Your 4-digit verification code is: {otp}",
        now=True
    )
    return {"status": "success", "message": "OTP sent to your email"}

@frappe.whitelist(allow_guest=True)
def verify_otp_and_register(email, otp, full_name, password, phone):
    cached_otp = frappe.cache().get_value(f"signup_otp:{email}")

    if not cached_otp:
        return {"status": "error", "message": "OTP expired. Please request a new one."}
    
    if str(cached_otp) != str(otp):
        return {"status": "error", "message": "Invalid OTP code"}

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
        frappe.db.commit()
        
        frappe.cache().delete_value(f"signup_otp:{email}")
        return {"status": "success", "message": "Verification successful!"}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Safi Pro OTP Register Error")
        return {"status": "error", "message": "Registration failed"}
