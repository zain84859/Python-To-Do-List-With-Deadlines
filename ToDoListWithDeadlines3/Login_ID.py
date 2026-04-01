state = {"Login_ID": None}


def set_current_user_id(id):
    state["Login_ID"] = id

def get_current_user_id():
    return state["Login_ID"]

