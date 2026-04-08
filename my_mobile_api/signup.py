import frappe

@frappe.whitelist(allow_guest=True)
def create_account(email=None, full_name=None, phone=None, password=None):
    if not all([email, full_name, phone, password]):
        frappe.throw("Fill all fields: Email, Name, Phone, Password")

    if frappe.db.exists("User", email):
        frappe.throw("User already exists")

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
    return {"status": "success"}
