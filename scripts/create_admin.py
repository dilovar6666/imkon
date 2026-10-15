import argparse
import getpass

from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models import User, UserRole


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an IMKON administrator")
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", help="Use only in secure automation; otherwise input is hidden")
    args = parser.parse_args()
    password = args.password or getpass.getpass("Password: ")
    if len(password) < 12:
        raise SystemExit("Password must contain at least 12 characters")
    with SessionLocal() as db:
        if db.scalar(select(User).where(User.email == args.email.lower())):
            raise SystemExit("Email already exists")
        db.add(User(email=args.email.lower(), password_hash=hash_password(password), role=UserRole.admin, is_email_verified=True))
        db.commit()
    print("Administrator created")


if __name__ == "__main__":
    main()
