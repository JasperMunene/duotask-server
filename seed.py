from models import db
from models.user import User
from models.user_info import UserInfo
from models.category import Category
from models.task import Task
from models.bid import Bid
from models.task_assignment import TaskAssignment
from models.task_location import TaskLocation
from models.review import Review
from app import app
from datetime import datetime, timedelta
import random
from sqlalchemy import text

def clear_tables():
    # Clear dependent tables first to satisfy foreign key constraints.
    Review.query.delete()               # Reviews depend on task assignments.
    TaskAssignment.query.delete()       # Delete assignments next.
    Bid.query.delete()                  # Delete bids.
    TaskLocation.query.delete()         # Delete task locations before tasks.
    db.session.execute(text("DELETE FROM task_categories"))  # Clear many-to-many relationships.
    Task.query.delete()                 # Then delete tasks.
    UserInfo.query.delete()             # Delete user infos.
    Category.query.delete()             # Delete categories.
    User.query.delete()                 # Finally, delete users.
    db.session.commit()

def make_users():
    # Create diverse users with Unsplash images
    users = [
        User(
            name="Alice Johnson",
            email="alice.johnson@example.com",
            phone="+11234567890",
            image="https://source.unsplash.com/600x600/?woman,portrait",
            is_verified=True,
            password="$2b$12$jIqf0Q/SpTvPrVXRWrltr.VmVS9Q8gu6CB4jZYqIPWSU63KlMn0Oy",
            auth_provider="email"
        ),
        User(
            name="Bob Smith",
            email="bob.smith@example.com",
            phone="+12345678901",
            image="https://source.unsplash.com/600x600/?man,portrait",
            is_verified=True,
            password="$2b$12$jIqf0Q/SpTvPrVXRWrltr.VmVS9Q8gu6CB4jZYqIPWSU63KlMn0Oy",
            auth_provider="email"
        ),
        User(
            name="Carlos Rivera",
            email="carlos.rivera@example.com",
            phone="+10987654321",
            image="https://source.unsplash.com/600x600/?hispanic,man",
            is_verified=True,
            password="$2b$12$jIqf0Q/SpTvPrVXRWrltr.VmVS9Q8gu6CB4jZYqIPWSU63KlMn0Oy",
            auth_provider="email"
        ),
        User(
            name="Sarah Lee",
            email="sarah.lee@example.com",
            phone="+19876543210",
            image="https://source.unsplash.com/600x600/?asian,woman",
            is_verified=True,
            password="$2b$12$jIqf0Q/SpTvPrVXRWrltr.VmVS9Q8gu6CB4jZYqIPWSU63KlMn0Oy",
            auth_provider="email"
        ),
        User(
            name="David Chen",
            email="david.chen@example.com",
            phone="+10123456789",
            image="https://source.unsplash.com/600x600/?asian,man",
            is_verified=True,
            password="$2b$12$jIqf0Q/SpTvPrVXRWrltr.VmVS9Q8gu6CB4jZYqIPWSU63KlMn0Oy",
            auth_provider="email"
        ),
        User(
            name="Emma Williams",
            email="emma.williams@example.com",
            phone="+14567890123",
            image="https://source.unsplash.com/600x600/?woman,smile",
            is_verified=True,
            password="$2b$12$jIqf0Q/SpTvPrVXRWrltr.VmVS9Q8gu6CB4jZYqIPWSU63KlMn0Oy",
            auth_provider="email"
        )
    ]
    db.session.add_all(users)
    db.session.commit()

    # Create corresponding UserInfo profiles
    user_infos = [
        UserInfo(user_id=users[0].id, tagline="Freelance Writer", bio="Passionate about storytelling and travel."),
        UserInfo(user_id=users[1].id, tagline="Web Developer", bio="Building seamless digital experiences."),
        UserInfo(user_id=users[2].id, tagline="Graphic Designer", bio="Creating visually compelling designs."),
        UserInfo(user_id=users[3].id, tagline="Photographer", bio="Capturing life’s precious moments."),
        UserInfo(user_id=users[4].id, tagline="Software Engineer", bio="Loves coding and innovative solutions."),
        UserInfo(user_id=users[5].id, tagline="Content Creator", bio="Sharing ideas and creative insights.")
    ]
    db.session.bulk_save_objects(user_infos)
    db.session.commit()

    print(f"Created {len(users)} users and {len(user_infos)} user profiles.")

def make_categories():
    # Create diverse categories with Unsplash images to serve as icons
    categories = [
        Category(name="Technology", icon="https://source.unsplash.com/600x600/?technology,abstract"),
        Category(name="Design", icon="https://source.unsplash.com/600x600/?design,graphic"),
        Category(name="Marketing", icon="https://source.unsplash.com/600x600/?marketing,business"),
        Category(name="Writing", icon="https://source.unsplash.com/600x600/?writing,notes"),
        Category(name="Photography", icon="https://source.unsplash.com/600x600/?photography,camera"),
        Category(name="Finance", icon="https://source.unsplash.com/600x600/?finance,investment"),
        Category(name="Health", icon="https://source.unsplash.com/600x600/?health,wellness")
    ]
    db.session.bulk_save_objects(categories)
    db.session.commit()
    print(f"Created {len(categories)} categories.")

def make_tasks():
    # Create diverse tasks
    users = User.query.all()
    categories = Category.query.all()

    tasks = [
        Task(
            user_id=users[0].id,
            title="Website Redesign",
            description="We need a complete redesign of our website with a focus on user experience.",
            work_mode="remote",
            budget=1500.00,
            schedule_type="flexible",
            status="open"
        ),
        Task(
            user_id=users[1].id,
            title="Logo Design",
            description="Design a modern, minimalistic logo for our startup.",
            work_mode="remote",
            budget=800.00,
            schedule_type="specific_day",
            specific_date=datetime.now() + timedelta(days=5),
            status="open"
        ),
        Task(
            user_id=users[2].id,
            title="Product Photography",
            description="Capture high-quality product images for our online catalog.",
            work_mode="physical",
            budget=1000.00,
            schedule_type="before_day",
            deadline_date=datetime.now() + timedelta(days=7),
            status="open"
        ),
        Task(
            user_id=users[3].id,
            title="Content Writing",
            description="Write 10 engaging blog posts on tech innovations.",
            work_mode="remote",
            budget=1200.00,
            schedule_type="flexible",
            status="open"
        ),
        Task(
            user_id=users[4].id,
            title="Social Media Campaign",
            description="Manage a social media campaign to boost brand awareness.",
            work_mode="remote",
            budget=900.00,
            schedule_type="specific_day",
            specific_date=datetime.now() + timedelta(days=3),
            status="open"
        ),
        Task(
            user_id=users[5].id,
            title="Mobile App Development",
            description="Develop a cross-platform mobile app with a focus on performance.",
            work_mode="remote",
            budget=2500.00,
            schedule_type="before_day",
            deadline_date=datetime.now() + timedelta(days=10),
            status="open"
        )
    ]
    db.session.add_all(tasks)
    db.session.commit()
    print(f"Created {len(tasks)} tasks.")

    # Randomly assign one category per task
    for task in tasks:
        task.categories.append(random.choice(categories))
    db.session.commit()

def make_bids():
    # Create diverse bids
    users = User.query.all()
    tasks = Task.query.all()

    bids = [
        Bid(task_id=tasks[0].id, user_id=users[1].id, amount=1300.00, message="I have multiple website redesigns in my portfolio."),
        Bid(task_id=tasks[1].id, user_id=users[2].id, amount=750.00, message="I specialize in clean and modern logo designs."),
        Bid(task_id=tasks[2].id, user_id=users[3].id, amount=950.00, message="Experienced in product photography with a professional setup."),
        Bid(task_id=tasks[3].id, user_id=users[0].id, amount=1100.00, message="Skilled in creating detailed and engaging content."),
        Bid(task_id=tasks[4].id, user_id=users[5].id, amount=850.00, message="I can manage dynamic social media campaigns effectively."),
        Bid(task_id=tasks[5].id, user_id=users[4].id, amount=2400.00, message="Expert in cross-platform app development with agile methods.")
    ]
    db.session.bulk_save_objects(bids)
    db.session.commit()
    print(f"Created {len(bids)} bids.")

def make_task_assignments():
    # Create task assignments for bids with diverse statuses.
    bids = Bid.query.all()
    assignments = []
    for bid in bids:
        status = random.choice(["completed", "assigned"])
        assignment = TaskAssignment(
            task_id=bid.task_id,
            task_giver=bid.task.user_id,
            task_doer=bid.user_id,
            agreed_price=bid.amount,
            bid_id=bid.id,
            status=status
        )
        assignments.append(assignment)
    # Add one additional assignment with status "cancelled" for variety.
    if bids:
        cancelled_assignment = TaskAssignment(
            task_id=bids[0].task_id,
            task_giver=bids[0].task.user_id,
            task_doer=bids[0].user_id,
            agreed_price=bids[0].amount,
            bid_id=bids[0].id,
            status="cancelled"
        )
        assignments.append(cancelled_assignment)

    db.session.bulk_save_objects(assignments)
    db.session.commit()
    print(f"Created {len(assignments)} task assignments.")

def make_task_locations():
    # Create locations for physical tasks only
    tasks = Task.query.filter_by(work_mode="physical").all()
    locations = []
    for task in tasks:
        # Generate random coordinates within a plausible range.
        latitude = random.uniform(34.0, 42.0)
        longitude = random.uniform(-124.0, -117.0)
        location = TaskLocation(
            task_id=task.id,
            latitude=latitude,
            longitude=longitude,
            country="USA",
            state="California",
            city="Random City",
            area="Random Area"
        )
        locations.append(location)
    db.session.bulk_save_objects(locations)
    db.session.commit()
    print(f"Created {len(locations)} task locations.")

def make_all_data():
    clear_tables()
    make_users()
    make_categories()
    make_tasks()
    make_bids()
    make_task_assignments()
    make_task_locations()

if __name__ == '__main__':
    with app.app_context():
        make_all_data()
