import frappe

@frappe.whitelist()
def update_profile_safe(full_name=None, phone=None):
    # This identifies the user based on their active session/login
    current_user = frappe.session.user
    
    # Safety check to ensure the user is actually logged in
    if current_user == "Guest":
        frappe.throw("Session expired, please login again")

    try:
        # Load the User document for the logged-in person
        doc = frappe.get_doc("User", current_user)
        
        # Apply updates sent from the Flutter app
        if full_name:
            doc.first_name = full_name
        if phone:
            doc.mobile_no = phone
            doc.phone = phone

        # Save changes. 'ignore_permissions' allows the user to update
        # their own record even if the Role Manager is strict.
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        
        return {"status": "success", "message": "Profile Updated"}
    except Exception as e:
        # If something fails, this logs the error in the 'Error Log' list
        frappe.log_error(frappe.get_traceback(), "Mobile Profile Update Failed")
        return {"status": "error", "message": str(e)}

import frappe

@frappe.whitelist(allow_guest=True)  # allow_guest is required for new users to sign up
def verify_and_signup(email, otp, full_name, password):
    # 1. Verify OTP (This logic depends on how you store your OTPs)
    # Check if you have a DocType or Cache storing the OTP
    saved_otp = frappe.cache().get_value(f"otp_{email}")
    
    if not saved_otp or str(saved_otp) != str(otp):
        frappe.throw("Invalid or expired OTP")

    # 2. Check if user already exists
    if frappe.db.exists("User", email):
        frappe.throw("An account with this email already exists")

    try:
        # 3. Create the User Document
        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": full_name,
            "new_password": password,
            "enabled": 1,
            "user_type": "System User",
            "send_welcome_email": 0
        })
        
        # Use ignore_permissions=True to bypass the Red Error screens
        user.insert(ignore_permissions=True)
        
        # 4. Assign the Customer Role automatically
        user.add_roles("Customer")
        
        frappe.db.commit()
        return {"status": "success", "message": "Account created successfully"}
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Signup Error")
        return {"status": "error", "message": str(e)}

import frappe

@frappe.whitelist(allow_guest=True)
def verify_and_signup(email=None, otp=None, full_name=None, password=None):
    # Check if any required field is missing
    if not all([email, otp, full_name, password]):
        frappe.throw("Missing required information. Please ensure email, OTP, name, and password are provided.")

    # ... rest of your signup logic (inserting user, etc.)
