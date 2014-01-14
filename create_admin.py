#!bin/python2
from blog.models import User, ROLE_ADMIN
from blog import db


def test_admin(passwd, email):
    admin_db = User.query.filter_by(nickname='admin').first()
    if admin_db:
        if not admin_db.password_correct(passwd) or admin_db.email != email:
            return False
    return True


def main():
    if User.query.filter_by(nickname='admin').first():
        print "Check the admin user."
        passwd = raw_input("Insert admin password: ")
        email = raw_input("Insert email address: ")
        if test_admin(passwd, email):
            print "Admin user matches."
        else:
            print "Doesn't matches."
        return
    print "You want to create a new admin user."
    passwd = raw_input("Insert admin password: ")
    email = raw_input("Insert email address: ")
    admin = User(nickname="admin", password=User.hash_password(passwd), email=email, role=ROLE_ADMIN)
    db.session.add(admin)
    db.session.commit()
    if test_admin(passwd, email):
        print "Admin user created successfully"


if __name__ == "__main__":
    main()