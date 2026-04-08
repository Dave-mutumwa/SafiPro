import frappe

@frappe.whitelist(allow_guest=True)
def register_user(**kwargs):
    # This captures whatever Flutter sends and maps it correctly
    email = kwargs.get('email')
    # It will look for 'full_name', then 'name' if full_name is missing
    full_name = kwargs.get('full_name') or kwargs.get('name')
    phone = kwargs.get('phone') or kwargs.get('mobile_no')
    password = kwargs.get('password')

    if not all([email, full_name, phone, password]):
        # This will tell us exactly what the server actually received
        frappe.throw(f"Missing fields. Received: {list(kwargs.keys())}")

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
