import frappe

# 1. PROFILE UPDATE (Only works for Logged-in Users)
@frappe.whitelist()
def update_profile_safe(full_name=None, phone=None):
    current_user = frappe.session.user
    
    if current_user == "Guest":
        frappe.throw("Session expired, please login again")

    try:
        doc = frappe.get_doc("User", current_user)
        if full_name: doc.first_name = full_name
        if phone: 
            doc.mobile_no = phone
            doc.phone = phone

        doc.save(ignore_permissions=True)
        frappe.db.commit()
        return {"status": "success", "message": "Profile Updated"}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Mobile Profile Update Failed")
        return {"status": "error", "message": str(e)}

# 2. SIGNUP & VERIFY (Works for Guests/New Users)
@frappe.whitelist(allow_guest=True)
def verify_and_signup(email=None, otp=None, full_name=None, password=None):
    if not all([email, otp, full_name, password]):
        frappe.throw("Missing required information (Email, OTP, Name, or Password).")

    # Check OTP from Cache
    saved_otp = frappe.cache().get_value(f"otp_{email}")
    if not saved_otp or str(saved_otp) != str(otp):
        frappe.throw("Invalid or expired OTP")

    if frappe.db.exists("User", email):
        frappe.throw("An account with this email already exists")

    try:
        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": full_name,
            "new_password": password,
            "enabled": 1,
            "user_type": "Website User", # Changed to Website User for your Customers
            "send_welcome_email": 0
        })
        user.insert(ignore_permissions=True)
        
        # Assign the Customer role (Make sure 'Customer' role exists in Frappe Desk)
        user.add_roles("Customer")
        
        frappe.db.commit()
        frappe.cache().delete_value(f"otp_{email}") # Clean up OTP
        return {"status": "success", "message": "Account created successfully"}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Signup Error")
        return {"status": "error", "message": str(e)}