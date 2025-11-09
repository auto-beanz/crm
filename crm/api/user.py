import frappe

@frappe.whitelist()
def add_existing_users(users, role="Sales User"):
    """
    Add existing users to the CRM by assigning them a role (Sales User or Sales Manager).
    :param users: List of user names to be added
    """
    frappe.only_for(["System Manager", "Sales Manager"])
    users = frappe.parse_json(users)
    for user in users:
        add_user(user, role)


@frappe.whitelist()
def update_user_role(user, new_role):
    """
    Update the role of the user to Sales Manager, Sales User, or System Manager.
    :param user: The name of the user
    :param new_role: The new role to assign (Sales Manager or Sales User)
    """

    frappe.only_for(["System Manager", "Sales Manager"])

    if new_role not in ["System Manager", "Sales Manager", "Sales User","Aftersales Executive","Customer Support Executive","Business Development Executive"]:
        frappe.throw("Cannot assign this role")

    try:
        user_doc = frappe.get_doc("User", user)

        if new_role == "System Manager":
            user_doc.append_roles("System Manager", "Sales Manager", "Sales User")
            user_doc.set("block_modules", [])
        if new_role == "Sales Manager":
            user_doc.append_roles("Sales Manager", "Sales User")
            user_doc.remove_roles("System Manager")
        if new_role == "Sales User":
            user_doc.append_roles("Sales User")
            user_doc.remove_roles("Sales Manager", "System Manager","Aftersales Executive","Customer Support Executive","Business Development Executive")
            update_module_in_user(user_doc, "FCRM")
        if new_role == "Aftersales Executive":
            user_doc.append_roles("Aftersales Executive")
            user_doc.remove_roles("Sales Manager", "System Manager","Sales User","Business Development Executive","Customer Support Executive")
        if new_role == "Customer Support Executive":
            user_doc.append_roles("Customer Support Executive")
            user_doc.remove_roles("Sales Manager", "System Manager","Sales User","Aftersales Executive","Business Development Executive")
        if new_role == "Business Development Executive":
            user_doc.append_roles("Business Development Executive")
            user_doc.remove_roles("Sales Manager", "System Manager","Sales User""Aftersales Executive","Customer Support Executive")
            update_module_in_user(user_doc, "FCRM")

        user_doc.save(ignore_permissions=True)

    except Exception as e:
        frappe.throw(f"Failed to update user {user}")


@frappe.whitelist()
def add_user(user, role):
	"""
	Add a user means adding role (Sales User or/and Sales Manager) to the user.
	:param user: The name of the user to be added
	:param role: The role to be assigned (Sales User or Sales Manager)
	"""
	update_user_role(user, role)


@frappe.whitelist()
def remove_user(user):
	"""
	Remove a user means removing Sales User & Sales Manager roles from the user.
	:param user: The name of the user to be removed
	"""
	frappe.only_for(["System Manager", "Sales Manager"])

	user_doc = frappe.get_doc("User", user)
	roles = [d.role for d in user_doc.roles]

	if "Sales User" in roles:
		user_doc.remove_roles("Sales User")
	if "Sales Manager" in roles:
		user_doc.remove_roles("Sales Manager")

	user_doc.save(ignore_permissions=True)
	frappe.msgprint(f"User {user} has been removed from CRM roles.")


def update_module_in_user(user, module):
	block_modules = frappe.get_all(
		"Module Def",
		fields=["name as module"],
		filters={"name": ["!=", module]},
	)

	if block_modules:
		user.set("block_modules", block_modules)



import frappe
import logging

# ... (Keep your add_existing_users, update_user_role, etc. functions) ...
# ... They are all still needed to add the user. ...


@frappe.whitelist()
def get_selectable_companies():
    """
    Gets all 'Company' records that are NOT groups.
    These are the selectable, operational companies.
    """
    try:
        companies = frappe.get_all("Company",
                                 filters={
                                     "is_group": 0,
                                 },
                                 fields=["name"])
        
        return [{"label": c.name, "value": c.name} for c in companies]
    
    except Exception as e:
        frappe.log_error(f"Error in get_selectable_companies: {e}")
        return []


@frappe.whitelist()
def get_departments_for_company(company=None):
    """
    Given a Company name, finds all Departments associated with it.
    """
    if not company:
        return []

    try:
        departments = frappe.get_all("Department",
                                     filters={"company": company},
                                     fields=["name"])
        
        return [{"label": d.name, "value": d.name} for d in departments]

    except Exception as e:
        frappe.log_error(f"Error in get_departments_for_company: {e}")
        return []


@frappe.whitelist()
def get_users_for_department(department=None):
    """
    Given a Department name, finds all Employees in that department
    and returns their linked user_id (email).
    (This function is unchanged)
    """
    if not department:
        return []

    try:
        employees = frappe.get_all("Employee",
                                 filters={
                                     "department": department,
                                     "user_id": ("is", "set")
                                 },
                                 fields=["user_id"])
        
        employee_ids = [e.get("user_id") for e in employees]
        frappe.log_error(
            title="Step 3 SUCCESS: Query Results",
            message=f"Query for {department} found {len(employee_ids)} users: {employee_ids}"
        )
        
        return [{"label": e.user_id, "value": e.user_id} for e in employees]
    
    except Exception as e:
        frappe.log_error(f"Error in get_users_for_department: {e}")
        return []