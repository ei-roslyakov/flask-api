def read_user_attributes_from_request(json):
    if not json:
        return None

    required_fields = ["name", "last_name", "description", "employee"]
    for required_field in required_fields:
        if required_field not in json:
            return None

    user = {
        "name": json["name"],
        "last_name": json["last_name"],
        "description": json["description"],
        "employee": bool(json["employee"]),
    }

    return user
