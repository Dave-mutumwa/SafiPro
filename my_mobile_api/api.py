import frappe
from frappe.utils import random_string

@frappe.whitelist(allow_guest=True)
def register_user(email, full_name, password, phone):
    # Step A: Check if the email already exists to avoid the error you saw earlier
    if frappe.db.exists("User", email):
        # For testing, we can delete the old failed attempt
        frappe.delete_doc("User", email)

    try:
        # Step B: Create the User Document
        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": full_name,
            "mobile_no": phone,
            "new_password": password,
            "enabled": 1,
            "user_type": "Website User" # This makes them a customer, not an admin
        })
        
        # Step C: Insert into database memory
        user.insert(ignore_permissions=True)
        
        # Step D: Assign the "Customer" role so they can use Safi Pro
        user.add_roles("Customer") 
        
        # Step E: THE CRITICAL STEP - Save to disk permanently
        frappe.db.commit() 
        
        return {
            "status": "success", 
            "message": f"User {email} has been saved and reflected in the backend."
        }

    except Exception as e:
        # If something fails, log it in the Frappe Error Log
        frappe.log_error(frappe.get_traceback(), "Safi Pro Registration Failed")
        return {"status": "error", "message": str(e)}
