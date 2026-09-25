from sqlmodel import SQLModel, Session, select
from database.connection import engine
from database.models import User, RoleEnum
from services.security import hash_password


def init():
    with Session(engine) as session:

        admin = session.exec(select(User).where(
            User.username == "admin")).first()
        if not admin:
            admin = User(
            username="admin",
            password_hash=hash_password("admin123"),
            role=RoleEnum.ADMIN
        )
            session.add(admin)
            session.commit()
            print("✅ Created Admin user (username: admin / password: admin123)")
        else:
            print("ℹ️ Admin user already exists.")

        worker = session.exec(select(User).where(
        User.username == "worker")).first()
        if not worker:
            worker = User(
            username="worker",
            password_hash=hash_password("worker123"),
            role=RoleEnum.WORKER
        )
            session.add(worker)
            session.commit()
            print("✅ Created Worker user (username: worker / password: worker123)")
        else:
            
            print("ℹ️ Worker user already exists.")

if __name__ == "__main__":
    init()
