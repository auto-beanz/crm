import frappe


@frappe.whitelist()
def get_users():
    users = frappe.qb.get_query(
        "User",
        fields=[
            "name",
            "email",
            "enabled",
            "user_image",
            "first_name",
            "last_name",
            "full_name",
            "user_type",
        ],
        order_by="full_name asc",
        distinct=True,
    ).run(as_dict=1)

    user_list = [user.name for user in users]

    employee_data = frappe.get_all("Employee",
                                    filters={"user_id": ("in", user_list)},
                                    fields=["user_id", "company"])
    
    company_map = {emp.user_id: emp.company for emp in employee_data}

    crm_roles = [
        "System Manager",
        "Sales Manager",
        "Sales User",
        "Aftersales Executive",
        "Customer Support Executive",
        "Business Development Executive",
    ]

    for user in users:
        if frappe.session.user == user.name:
            user.session_user = True

        user.roles = frappe.get_roles(user.name)
        user.role = ""

        if "System Manager" in user.roles:
            user.role = "System Manager"
        elif "Sales Manager" in user.roles:
            user.role = "Sales Manager"
        elif "Sales User" in user.roles:
            user.role = "Sales User"
        elif "Aftersales Executive" in user.roles:
            user.role = "Aftersales Executive"
        elif "Customer Support Executive" in user.roles:
            user.role = "Customer Support Executive"
        elif "Business Development Executive" in user.roles:
            user.role = "Business Development Executive"
        elif "Guest" in user.roles:
            user.role = "Guest"

        if frappe.session.user == user.name:
            user.session_user = True
            
        user.company = company_map.get(user.name)

        user.is_telephony_agent = frappe.db.exists("CRM Telephony Agent", {"user": user.name})

    crm_users = []

    for user in users:
        if any(role in crm_roles for role in user.roles):
            crm_users.append(user)

    return users, crm_users

@frappe.whitelist()
def get_organizations():
	organizations = frappe.qb.get_query(
		"CRM Organization",
		fields=["*"],
		order_by="name asc",
		distinct=True,
	).run(as_dict=1)

	return organizations
