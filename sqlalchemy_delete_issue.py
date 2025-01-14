# Imports
# https://www.youtube.com/watch?v=jobpptS9f8I&t=1515s
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.exc import IntegrityError


# Create your Database
# engine = create_engine("sqlite:///:memory:", echo=True)
engine = create_engine("sqlite:///tasks.db", echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


# Define Models (User / Task)
# Data Models?, Database setup
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)

    tasks = relationship('Task', back_populates='user', cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    title = Column(String(50), nullable=True)
    description = Column(String)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='tasks')


Base.metadata.create_all(engine)

# Utility Functions
def get_user_by_email(email):
    return session.query(User).filter_by(email=email).first()

def confirm_action(prompt:str) -> bool:
    return input (f"{prompt} (yes/no): ").strip().lower == 'yes'


# CRUD Ops
def add_user():
    name, email = input("Enter user name: "), input("Enter the email: ")
    if get_user_by_email(email):
        print(f'user already exits: {email}')
        return

    try:
        session.add(User(name=name, email=email))
        session.commit()
        print(f'User: {name} added!')
    except IntegrityError:
        session.rollback()
        print(f'ERROR')


def add_task():
    email = input("Enter the email of the user to add tasks:")
    user = get_user_by_email(email)
    if not user:
        print(f'No user found with that email!')
        return
    
    title, description = input("Enter the title:"), input("Enter the Description:")
    session.add(Task(title=title, description=description, user=user))
    session.commit()
    print(f'Added to the database: {title}:{description}')

 
# Querying
def query_users():
    for user in session.query(User).all():
        print(f'ID: {user.id}, Name: {user.name}, Email: {user.email}')

def query_tasks():
    email = input("Enter the email of the user fro tasks: ")
    user = get_user_by_email(email)
    # user = session.query(User).filter_by(email=email).first()
    if not user:
        print('There was no user with that email')
        return

    for task in user.tasks:
        print(f'Task ID: {task.id}, Title: {task.title}')


# Update User
def update_user():
    email = input("Email of who you want to update: ")
    user = get_user_by_email(email)
    if not user:
        print('There is no user with that email')
        return
    
    user.name = input("Enter a new name for the user (leave blank to stay the same): ") or user.name
    user.email = input("Enter a new email (leave blank to stay the same): ") or user.email
    session.commit()
    print('User has been updated!')


# Deleting user (Row)
def delete_user():
    email = input("Email of who you want to Delete: ")
    user = get_user_by_email(email)
    # user = session.query(User).filter_by(email=email).first()
    print('Selected username: ', user.name)
    if not user:
        print('There is no user with that email')
        return
    
    if confirm_action(f'Are you sure youwant to delete: {user.name}?'):
        print('deleting username: ', user.name)
        session.delete(user)
        session.commit()
        print('User has been deleted!')

# Deleting a Task (Cell)
def delete_task():
    email = input("Email of who you want to Delete: ")
    user = get_user_by_email(email)

    for task in user.tasks:
        print(f'Task ID: {task.id}, Title: {task.title}')

    task_id = input("Enter th ID of the task to delete: ")
    
    task = next((t for t in user.tasks if str(t.id) == task_id), None)

    # task_id = input("Enter th ID of the task to delete: ")
    # task = session.query(task).get(task_id)
    # if not task:
    #     print("There is no task to delete!")
    #     return
    
    if confirm_action(f'Are you sure youwant to delete: {task.id}?'):
        session.delete(task)
        session.commit()
        print('Task has been deleted!')


# Main Ops
def main() -> None:
    actions = {
        "1":add_user,
        "2":add_task,
        "3":query_users,
        "4":query_tasks,
        "5":update_user,
        "6":delete_user,
        "7":delete_task
    }

    while True:
        print('\nOptions:\n1. Add User\n2. Add Task\n3. Query Users\n4. Query Tasks\n5. Update User\n6. Delete User\n7. Delete Task\n8. Exit')
        choice = input("Enter an option: ")
        if choice == "8":
            print("Adios")
            break
        action = actions.get(choice)
        if action:
            action()
        else:
            print('That is not an option!')

if __name__ == "__main__":
    main()