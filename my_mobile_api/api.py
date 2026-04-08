import frappe

@frappe.whitelist(allow_guest=True)
def register_user(email=None, full_name=None, phone=None, password=None):
    # Match the 4 fields from your Flutter UI
    if not all([email, full_name, phone, password]):
        frappe.throw("Please provide all required fields (Email, Name, Phone, and Password)")

    if frappe.db.exists("User", email):
        frappe.throw("An account with this email already exists.")

    try:
        user = frappe.get_doc({
            "doctype": "User",
            "email": email.strip(),
            "first_name": full_name.strip(),
            "mobile_no": phone.strip(),
            "new_password": password,
            "enabled": 1,
            "user_type": "Website User", 
            "send_welcome_email": 0
        })

        # ignore_permissions=True bypasses the Desk Permission check
        user.insert(ignore_permissions=True)
        user.add_roles("Customer")
        frappe.db.commit()
        
        return {
            "status": "success",
            "message": f"Account created successfully for {full_name}"
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Mobile Signup Error")
        return {
            "status": "error",
            "message": str(e)
        }
