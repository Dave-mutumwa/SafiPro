import frappe

@frappe.whitelist(allow_guest=True)
def register_user(email=None, full_name=None, phone=None, password=None):
    # We use .strip() to handle any accidental spaces from the mobile keyboard
    email = email.strip() if email else None
    full_name = full_name.strip() if full_name else None
    phone = phone.strip() if phone else None

    if not all([email, full_name, phone, password]):
        frappe.throw("All fields are required: Email, Name, Phone, and Password.")

    if frappe.db.exists("User", email):
        frappe.throw("This email is already registered.")

    try:
        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": full_name,
            "mobile_no": phone,
            "new_password": password,
            "enabled": 1,
            "user_type": "Website User",
            "send_welcome_email": 0
        })
        user.insert(ignore_permissions=True)
        user.add_roles("Customer")
        frappe.db.commit()
        return {"status": "success", "message": "Account created!"}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Signup Error")
        return {"status": "error", "message": str(e)}
