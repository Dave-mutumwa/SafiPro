import frappe

@frappe.whitelist(allow_guest=True)
def register_user(email=None, full_name=None, phone=None, password=None):
    # This check ensures no empty data is saved
    if not all([email, full_name, phone, password]):
        frappe.throw("Required: Email, Full Name, Phone, and Password.")

    if frappe.db.exists("User", email):
        frappe.throw("This email is already registered.")

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
        
        user.insert(ignore_permissions=True)
        user.add_roles("Customer")
        
        frappe.db.commit()
        return {"status": "success", "message": "Account created successfully"}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Signup Error")
        return {"status": "error", "message": str(e)}
