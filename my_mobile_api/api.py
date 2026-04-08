import frappe

@frappe.whitelist(allow_guest=True)
def register_user(email=None, full_name=None, phone=None, password=None):
    if not all([email, full_name, phone, password]):
        frappe.throw("Please provide all fields: Email, Name, Phone, and Password")

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
        user.insert(ignore_permissions=True)
        user.add_roles("Customer")
        frappe.db.commit()
        return {"status": "success", "message": "User Created"}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Signup Error")
        return {"status": "error", "message": str(e)}
