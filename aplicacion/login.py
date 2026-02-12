from flask import session

def login_user(Usuario):
    session["id"] = Usuario.id
    session["username"] = Usuario.username
    session["admin"] = getattr(Usuario, 'admin', False)

def logout_user():
    session.clear()

def is_login():
    if "id" in session:
        return True
    else:
        return False

def is_admin():
    return session.get("admin", False)