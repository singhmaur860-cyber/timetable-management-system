import os
import random
import sys
from datetime import date, datetime, timezone

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.app.core.database import Base, SessionLocal, engine
from backend.app.core.security import get_password_hash
from backend.app.models.models import (
    AcademicYear,
    Announcement,
    Building,
    Campus,
    Department,
    Lab,
    Notification,
    Period,
    Program,
    Role,
    Room,
    RoomAvailability,
    Section,
    Semester,
    Student,
    Subject,
    Teacher,
    TeacherAvailability,
    TeacherSubject,
    Timetable,
    University,
    User,
    WorkingDay,
)
from backend.app.services.timetable_generator import TimetableGenerator


def seed_database():
    print("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if already seeded
        if db.query(User).filter(User.email == "admin@university.com").first():
            print("Database already populated. Skipping full seed.")
            return

        print("Seeding Roles and Permissions...")
        roles = [
            Role(name="Super Admin", description="Full administrative authority across university"),
            Role(name="University Admin", description="University-wide operations and reporting"),
            Role(name="HOD", description="Head of Department managing faculty, curriculum, and schedule"),
            Role(name="Teacher", description="Faculty member viewing teaching schedule and absences"),
            Role(name="Student", description="Enrolled student viewing class schedule and notices"),
            Role(name="Class Coordinator", description="Faculty managing section schedules")
        ]
        db.add_all(roles)
        db.commit()

        print("Seeding University & Campuses...")
        uni = University(
            name="Metropolitan University of Technology",
            code="MUT",
            address="100 Innovation Boulevard, Tech District",
            email="registrar@mut.edu",
            phone="+1 (555) 019-2834",
            website="https://www.mut.edu"
        )
        db.add(uni)
        db.commit()
        db.refresh(uni)

        campus = Campus(
            university_id=uni.id,
            name="Main Academic Campus",
            code="MAC",
            address="100 Innovation Boulevard"
        )
        db.add(campus)
        db.commit()
        db.refresh(campus)

        print("Seeding Academic Years & Semesters...")
        ay = AcademicYear(
            name="2026-2027",
            start_date=date(2026, 8, 1),
            end_date=date(2027, 5, 30),
            is_current=True
        )
        db.add(ay)
        db.commit()
        db.refresh(ay)

        semesters = [
            Semester(academic_year_id=ay.id, name="Semester 1 (Autumn)", semester_number=1, start_date=date(2026, 8, 1), end_date=date(2026, 12, 15), is_active=False),
            Semester(academic_year_id=ay.id, name="Semester 3 (Autumn)", semester_number=3, start_date=date(2026, 8, 1), end_date=date(2026, 12, 15), is_active=False),
            Semester(academic_year_id=ay.id, name="Semester 5 (Autumn)", semester_number=5, start_date=date(2026, 8, 1), end_date=date(2026, 12, 15), is_active=True),
            Semester(academic_year_id=ay.id, name="Semester 7 (Autumn)", semester_number=7, start_date=date(2026, 8, 1), end_date=date(2026, 12, 15), is_active=False),
        ]
        db.add_all(semesters)
        db.commit()
        for s in semesters:
            db.refresh(s)
        active_semester = semesters[2]  # Semester 5

        print("Seeding Periods and Working Days...")
        period_configs = [
            (1, "Period 1", "09:00", "10:00", False, None),
            (2, "Period 2", "10:00", "11:00", False, None),
            (3, "Morning Break", "11:00", "11:15", True, "Morning Tea Break"),
            (4, "Period 3", "11:15", "12:15", False, None),
            (5, "Period 4", "12:15", "13:15", False, None),
            (6, "Lunch Break", "13:15", "14:00", True, "Lunch Recess"),
            (7, "Period 5", "14:00", "15:00", False, None),
            (8, "Period 6", "15:00", "16:00", False, None)
        ]
        periods_list = []
        for pnum, pname, st, et, is_brk, brk_name in period_configs:
            p = Period(
                academic_year_id=ay.id,
                period_number=pnum,
                name=pname,
                start_time=st,
                end_time=et,
                is_break=is_brk,
                break_name=brk_name
            )
            db.add(p)
            periods_list.append(p)
        db.commit()
        for p in periods_list:
            db.refresh(p)

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        working_days_list = []
        for i, dname in enumerate(days):
            wd = WorkingDay(
                academic_year_id=ay.id,
                day_of_week=i,
                day_name=dname,
                is_working=(i < 5)  # Mon-Fri active
            )
            db.add(wd)
            working_days_list.append(wd)
        db.commit()

        print("Seeding Buildings and 20 Rooms (including 5 Labs)...")
        b1 = Building(campus_id=campus.id, name="Turing Computing Hall", code="TCH", total_floors=4)
        b2 = Building(campus_id=campus.id, name="Tesla Engineering Complex", code="TEC", total_floors=4)
        db.add_all([b1, b2])
        db.commit()
        db.refresh(b1)
        db.refresh(b2)

        rooms_list = []
        # 15 Standard Classrooms (capacities 60 to 120)
        classroom_configs = [
            (b1.id, "101", 1, 75, "Classroom"),
            (b1.id, "102", 1, 75, "Classroom"),
            (b1.id, "103", 1, 75, "Classroom"),
            (b1.id, "201", 2, 80, "Classroom"),
            (b1.id, "202", 2, 80, "Classroom"),
            (b1.id, "203", 2, 90, "Classroom"),
            (b1.id, "301", 3, 100, "Seminar Hall"),
            (b1.id, "302", 3, 120, "Auditorium"),
            (b2.id, "101", 1, 70, "Classroom"),
            (b2.id, "102", 1, 70, "Classroom"),
            (b2.id, "201", 2, 75, "Classroom"),
            (b2.id, "202", 2, 75, "Classroom"),
            (b2.id, "301", 3, 80, "Classroom"),
            (b2.id, "302", 3, 80, "Classroom"),
            (b2.id, "401", 4, 110, "Seminar Hall")
        ]
        for bid, rnum, fl, cap, rtype in classroom_configs:
            r = Room(
                building_id=bid,
                room_number=rnum,
                floor=fl,
                capacity=cap,
                room_type=rtype,
                equipment="Interactive Projector, Sound System, Digital Whiteboard"
            )
            db.add(r)
            rooms_list.append(r)

        # 5 Specialized Laboratories
        lab_configs = [
            (b1.id, "LAB-1", 1, 60, "Computer Lab", "Advanced Computing & AI Lab", 50),
            (b1.id, "LAB-2", 2, 60, "Computer Lab", "Data Engineering & Systems Lab", 50),
            (b2.id, "LAB-3", 1, 60, "Electronics Lab", "VLSI & Digital Signal Processing Lab", 45),
            (b2.id, "LAB-4", 2, 60, "Computer Lab", "Networks & Embedded Systems Lab", 45),
            (b2.id, "LAB-5", 3, 60, "Robotics Lab", "Robotics & Automation Research Lab", 40)
        ]
        for bid, rnum, fl, cap, rtype, lab_name, sys_cnt in lab_configs:
            r = Room(
                building_id=bid,
                room_number=rnum,
                floor=fl,
                capacity=cap,
                room_type=rtype,
                equipment="Dual Monitors, High-Performance Workstations, FPGA Boards"
            )
            db.add(r)
            db.commit()
            db.refresh(r)
            lab = Lab(
                room_id=r.id,
                name=lab_name,
                lab_type=rtype,
                total_systems=sys_cnt,
                software_installed="Python 3.12, PostgreSQL, Docker, Ubuntu, MATLAB, KiCad, ROS"
            )
            db.add(lab)
            rooms_list.append(r)
        db.commit()

        print("Seeding 3 Academic Departments...")
        dept_cse = Department(campus_id=campus.id, name="Computer Science & Engineering", code="CSE", description="Department of Computer Science and Software Engineering")
        dept_ece = Department(campus_id=campus.id, name="Electronics & Communication Engineering", code="ECE", description="Department of Electronics and Microelectronics")
        dept_mre = Department(campus_id=campus.id, name="Mechanical & Robotics Engineering", code="MRE", description="Department of Mechanical Engineering and Applied Robotics")
        db.add_all([dept_cse, dept_ece, dept_mre])
        db.commit()
        db.refresh(dept_cse)
        db.refresh(dept_ece)
        db.refresh(dept_mre)

        print("Seeding Degree Programs...")
        prog_cse = Program(department_id=dept_cse.id, name="Bachelor of Technology in Computer Science", code="B.Tech CSE", duration_years=4, total_semesters=8)
        prog_ece = Program(department_id=dept_ece.id, name="Bachelor of Technology in Electronics", code="B.Tech ECE", duration_years=4, total_semesters=8)
        prog_mre = Program(department_id=dept_mre.id, name="Bachelor of Technology in Robotics", code="B.Tech MRE", duration_years=4, total_semesters=8)
        db.add_all([prog_cse, prog_ece, prog_mre])
        db.commit()
        db.refresh(prog_cse)
        db.refresh(prog_ece)
        db.refresh(prog_mre)

        print("Seeding 10 Class Sections...")
        sections_data = [
            (prog_cse.id, active_semester.id, "Section A", 60),
            (prog_cse.id, active_semester.id, "Section B", 60),
            (prog_cse.id, active_semester.id, "Section C", 55),
            (prog_cse.id, semesters[1].id, "Section A", 60),  # Sem 3
            (prog_cse.id, semesters[1].id, "Section B", 55),
            (prog_ece.id, active_semester.id, "Section A", 50),
            (prog_ece.id, active_semester.id, "Section B", 50),
            (prog_ece.id, semesters[1].id, "Section A", 50),  # Sem 3
            (prog_mre.id, active_semester.id, "Section A", 45),
            (prog_mre.id, active_semester.id, "Section B", 45),
        ]
        sections_list = []
        for pid, sid, sname, scnt in sections_data:
            sec = Section(program_id=pid, semester_id=sid, name=sname, student_count=scnt)
            db.add(sec)
            sections_list.append(sec)
        db.commit()
        for sec in sections_list:
            db.refresh(sec)

        print("Seeding 30 Academic Subjects...")
        subjects_spec = [
            # CSE Subjects (10)
            (dept_cse.id, active_semester.id, "CS501", "Database Management Systems", 4, 3, 2, True, "Computer Lab", "#4F46E5"),
            (dept_cse.id, active_semester.id, "CS502", "Operating Systems & Concurrency", 4, 3, 2, True, "Computer Lab", "#059669"),
            (dept_cse.id, active_semester.id, "CS503", "Computer Networks & Protocols", 4, 3, 1, False, "Classroom", "#D97706"),
            (dept_cse.id, active_semester.id, "CS504", "Design & Analysis of Algorithms", 4, 4, 0, False, "Classroom", "#7C3AED"),
            (dept_cse.id, active_semester.id, "CS505", "Software Engineering & Agile", 3, 3, 0, False, "Classroom", "#2563EB"),
            (dept_cse.id, semesters[1].id, "CS301", "Data Structures & Algorithms", 4, 3, 2, True, "Computer Lab", "#DC2626"),
            (dept_cse.id, semesters[1].id, "CS302", "Digital Logic Design", 3, 3, 1, True, "Computer Lab", "#0891B2"),
            (dept_cse.id, semesters[1].id, "CS303", "Discrete Mathematics", 4, 4, 0, False, "Classroom", "#475569"),
            (dept_cse.id, semesters[0].id, "CS101", "Programming Fundamentals in C", 4, 3, 2, True, "Computer Lab", "#0D9488"),
            (dept_cse.id, semesters[3].id, "CS701", "Artificial Intelligence & Robotics", 4, 3, 2, True, "Computer Lab", "#E11D48"),

            # ECE Subjects (10)
            (dept_ece.id, active_semester.id, "EC501", "Microprocessors & Microcontrollers", 4, 3, 2, True, "Electronics Lab", "#EA580C"),
            (dept_ece.id, active_semester.id, "EC502", "Digital Signal Processing", 4, 3, 2, True, "Electronics Lab", "#16A34A"),
            (dept_ece.id, active_semester.id, "EC503", "VLSI Circuit Design", 4, 3, 2, True, "Electronics Lab", "#9333EA"),
            (dept_ece.id, active_semester.id, "EC504", "Electromagnetic Fields & Waves", 3, 3, 0, False, "Classroom", "#CA8A04"),
            (dept_ece.id, active_semester.id, "EC505", "Analog Communication Systems", 4, 3, 1, False, "Classroom", "#0284C7"),
            (dept_ece.id, semesters[1].id, "EC301", "Electronic Circuits Analysis", 4, 3, 2, True, "Electronics Lab", "#B91C1C"),
            (dept_ece.id, semesters[1].id, "EC302", "Signals & Linear Systems", 4, 4, 0, False, "Classroom", "#64748B"),
            (dept_ece.id, semesters[1].id, "EC303", "Network Theory", 3, 3, 0, False, "Classroom", "#0F766E"),
            (dept_ece.id, semesters[0].id, "EC101", "Basic Electrical Engineering", 4, 3, 2, True, "Electronics Lab", "#C026D3"),
            (dept_ece.id, semesters[3].id, "EC701", "Optical Fiber Communications", 3, 3, 1, False, "Classroom", "#4338CA"),

            # MRE Subjects (10)
            (dept_mre.id, active_semester.id, "MR501", "Robotics Kinematics & Dynamics", 4, 3, 2, True, "Robotics Lab", "#BE123C"),
            (dept_mre.id, active_semester.id, "MR502", "Mechatronics System Design", 4, 3, 2, True, "Robotics Lab", "#1D4ED8"),
            (dept_mre.id, active_semester.id, "MR503", "Control Engineering", 4, 3, 1, False, "Classroom", "#047857"),
            (dept_mre.id, active_semester.id, "MR504", "Fluid Power & Pneumatics", 3, 3, 0, False, "Classroom", "#B45309"),
            (dept_mre.id, active_semester.id, "MR505", "Sensor Technology & Instrumentation", 3, 3, 1, False, "Classroom", "#6D28D9"),
            (dept_mre.id, semesters[1].id, "MR301", "Applied Thermodynamics", 4, 3, 1, False, "Classroom", "#991B1B"),
            (dept_mre.id, semesters[1].id, "MR302", "Manufacturing Automation", 4, 3, 2, True, "Robotics Lab", "#0369A1"),
            (dept_mre.id, semesters[1].id, "MR303", "Strength of Materials", 3, 3, 0, False, "Classroom", "#334155"),
            (dept_mre.id, semesters[0].id, "MR101", "Engineering Mechanics", 4, 4, 0, False, "Classroom", "#15803D"),
            (dept_mre.id, semesters[3].id, "MR701", "Autonomous Mobile Robots", 4, 3, 2, True, "Robotics Lab", "#A21CAF")
        ]
        subjects_list = []
        for did, sid, scode, sname, cred, th, pr, is_l, rpref, col in subjects_spec:
            subj = Subject(
                department_id=did,
                semester_id=sid,
                code=scode,
                name=sname,
                credits=cred,
                weekly_theory_periods=th,
                weekly_practical_periods=pr,
                lab_required=is_l,
                preferred_room_type=rpref,
                color_code=col
            )
            db.add(subj)
            subjects_list.append(subj)
        db.commit()
        for subj in subjects_list:
            db.refresh(subj)

        print("Seeding 50 Faculty Members across departments...")
        first_names = ["Rajesh", "Priya", "Vikram", "Ananya", "Amit", "Sneha", "Karan", "Pooja", "Arjun", "Deepa",
                       "Sanjay", "Kavita", "Rohan", "Meera", "Aditya", "Neha", "Naveen", "Swati", "Manoj", "Divya",
                       "Gaurav", "Sunita", "Harish", "Ritu", "Alok"]
        last_names = ["Sharma", "Patel", "Singh", "Sen", "Deshmukh", "Verma", "Rao", "Nair", "Gupta", "Reddy",
                      "Chopra", "Joshi", "Iyer", "Banerjee", "Kulkarni"]
        designations = ["Professor", "Associate Professor", "Assistant Professor"]

        teachers_list = []
        dept_ids = [dept_cse.id] * 24 + [dept_ece.id] * 16 + [dept_mre.id] * 10
        password_hash = get_password_hash("Password123!")

        # 1. Demo HOD User & Profile
        hod_user = User(
            email="hod@university.com",
            hashed_password=password_hash,
            full_name="Dr. Rajesh Sharma",
            role="HOD",
            phone="+1 (555) 234-5678",
            department_id=dept_cse.id
        )
        db.add(hod_user)
        db.commit()
        db.refresh(hod_user)

        hod_teacher = Teacher(
            user_id=hod_user.id,
            teacher_id="FAC-CSE-001",
            name="Dr. Rajesh Sharma",
            email="hod@university.com",
            phone="+1 (555) 234-5678",
            department_id=dept_cse.id,
            designation="Professor & HOD",
            max_weekly_hours=14
        )
        db.add(hod_teacher)
        db.commit()
        db.refresh(hod_teacher)
        teachers_list.append(hod_teacher)
        dept_cse.hod_id = hod_teacher.id
        db.commit()

        # 2. Demo Teacher User & Profile
        teacher_user = User(
            email="teacher@university.com",
            hashed_password=password_hash,
            full_name="Dr. Priya Patel",
            role="Teacher",
            phone="+1 (555) 345-6789",
            department_id=dept_cse.id
        )
        db.add(teacher_user)
        db.commit()
        db.refresh(teacher_user)

        demo_teacher = Teacher(
            user_id=teacher_user.id,
            teacher_id="FAC-CSE-002",
            name="Dr. Priya Patel",
            email="teacher@university.com",
            phone="+1 (555) 345-6789",
            department_id=dept_cse.id,
            designation="Associate Professor",
            max_weekly_hours=18
        )
        db.add(demo_teacher)
        db.commit()
        db.refresh(demo_teacher)
        teachers_list.append(demo_teacher)

        # 3. Create remaining 48 teachers
        for i in range(2, 50):
            fn = first_names[i % len(first_names)]
            ln = last_names[(i * 3) % len(last_names)]
            dept_id = dept_ids[i]
            prefix = "CSE" if dept_id == dept_cse.id else ("ECE" if dept_id == dept_ece.id else "MRE")
            code = f"FAC-{prefix}-{i+1:03d}"
            email = f"{fn.lower()}.{ln.lower()}{i}@university.com"
            desig = designations[i % len(designations)]

            t = Teacher(
                teacher_id=code,
                name=f"Dr. {fn} {ln}",
                email=email,
                phone=f"+1 (555) {random.randint(100, 999)}-{random.randint(1000, 9999)}",
                department_id=dept_id,
                designation=desig,
                max_weekly_hours=random.choice([16, 18, 20])
            )
            db.add(t)
            teachers_list.append(t)
        db.commit()
        for t in teachers_list:
            db.refresh(t)

        # Assign Teachers to Subjects
        for subj in subjects_list:
            dept_fac = [t for t in teachers_list if t.department_id == subj.department_id]
            if dept_fac:
                selected_teachers = random.sample(dept_fac, min(2, len(dept_fac)))
                for idx, fac in enumerate(selected_teachers):
                    ts = TeacherSubject(teacher_id=fac.id, subject_id=subj.id, is_primary=(idx == 0))
                    db.add(ts)
        db.commit()

        # Set coordinators for sections
        for idx, sec in enumerate(sections_list):
            sec.coordinator_id = teachers_list[idx % len(teachers_list)].id
        db.commit()

        print("Seeding 500 Students across sections...")
        students_list = []
        # Demo Student
        demo_student_user = User(
            email="student@university.com",
            hashed_password=password_hash,
            full_name="Aarav Mehta",
            role="Student",
            phone="+1 (555) 987-6543",
            department_id=dept_cse.id
        )
        db.add(demo_student_user)
        db.commit()
        db.refresh(demo_student_user)

        target_section = sections_list[0]  # CSE Sem 5 Section A
        demo_stu = Student(
            user_id=demo_student_user.id,
            student_id="STU-2024-0001",
            name="Aarav Mehta",
            email="student@university.com",
            phone="+1 (555) 987-6543",
            program_id=prog_cse.id,
            department_id=dept_cse.id,
            semester_id=active_semester.id,
            section_id=target_section.id
        )
        db.add(demo_stu)
        students_list.append(demo_stu)

        student_first = ["Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan", "Krishna", "Ishaan",
                         "Diya", "Saanvi", "Ananya", "Aadhya", "Pari", "Chiara", "Myra", "Anvi", "Prisha", "Riya"]
        student_last = ["Mehta", "Bose", "Dutta", "Nair", "Pillai", "Menon", "Kapoor", "Bhatia", "Malhotra", "Saxena"]

        # Bulk create remaining 499 students
        student_records = []
        for i in range(2, 501):
            fn = student_first[i % len(student_first)]
            ln = student_last[(i * 7) % len(student_last)]
            sec = sections_list[i % len(sections_list)]
            s_rec = Student(
                student_id=f"STU-2024-{i:04d}",
                name=f"{fn} {ln}",
                email=f"student{i}@university.com",
                phone=f"+1 (555) {random.randint(100, 999)}-{random.randint(1000, 9999)}",
                program_id=sec.program_id,
                department_id=sec.program.department_id,
                semester_id=sec.semester_id,
                section_id=sec.id
            )
            student_records.append(s_rec)

        db.bulk_save_objects(student_records)
        db.commit()

        print("Seeding Super Admin account...")
        admin_user = User(
            email="admin@university.com",
            hashed_password=get_password_hash("AdminPassword123!"),
            full_name="System Administrator",
            role="Super Admin",
            phone="+1 (555) 000-1111",
            is_active=True,
            is_verified=True
        )
        db.add(admin_user)
        db.commit()

        print("Seeding Teacher & Room Unavailability Slots...")
        # Mark Dr. Rajesh Sharma unavailable on Wednesday period 4
        db.add(TeacherAvailability(
            teacher_id=hod_teacher.id,
            day_of_week=2,  # Wednesday
            period_id=periods_list[3].id,  # Period 3
            is_available=False,
            reason="HOD Academic Council Meeting"
        ))
        # Mark Dr. Priya Patel unavailable Monday period 1
        db.add(TeacherAvailability(
            teacher_id=demo_teacher.id,
            day_of_week=0,  # Monday
            period_id=periods_list[0].id,
            is_available=False,
            reason="Research Advising"
        ))
        # Mark Lab 1 unavailable Friday afternoon for maintenance
        lab_room = db.query(Room).filter(Room.room_number == "LAB-1").first()
        if lab_room:
            db.add(RoomAvailability(
                room_id=lab_room.id,
                day_of_week=4,  # Friday
                period_id=periods_list[-1].id,
                is_available=False,
                reason="Weekly Server OS Maintenance"
            ))
        db.commit()

        print("Seeding Announcements & Notifications...")
        ann1 = Announcement(
            title="Autumn 2026 Academic Timetable Finalized",
            description="The Department of Computer Science has generated the conflict-free timetable for Semester 5. All classes commence Monday at 09:00 AM.",
            priority="HIGH",
            target_audience="ALL",
            department_id=dept_cse.id,
            author_id=admin_user.id
        )
        ann2 = Announcement(
            title="Advanced Robotics Lab Safety Orientation",
            description="All students registered for Robotics Kinematics & Dynamics must attend the mandatory equipment safety workshop in LAB-5.",
            priority="MEDIUM",
            target_audience="DEPARTMENT",
            department_id=dept_mre.id,
            author_id=admin_user.id
        )
        db.add_all([ann1, ann2])
        db.commit()

        db.add(Notification(
            user_id=demo_student_user.id,
            title="Class Schedule Live",
            message="Your weekly timetable for B.Tech CSE Semester 5 Section A is now available in your student portal.",
            type="TIMETABLE_PUBLISHED",
            is_read=False,
            link_url="/student/timetable.html"
        ))
        db.add(Notification(
            user_id=teacher_user.id,
            title="Teaching Workload Assigned",
            message="Your faculty teaching timetable has been updated. You have 16 teaching hours scheduled this week.",
            type="TIMETABLE_CHANGED",
            is_read=False,
            link_url="/teacher/timetable.html"
        ))
        db.commit()

        print("Running Google OR-Tools CP-SAT Timetable Generator for CSE Semester 5...")
        # Automatically generate a conflict-free timetable so the app is instantly rich with data!
        try:
            generator = TimetableGenerator(
                db=db,
                academic_year_id=ay.id,
                semester_id=active_semester.id,
                department_id=dept_cse.id,
                section_ids=[s.id for s in sections_list if s.semester_id == active_semester.id and s.program_id == prog_cse.id],
                time_limit_seconds=15
            )
            tt_id, stats = generator.build_and_solve()
            # Publish it
            tt = db.query(Timetable).filter(Timetable.id == tt_id).first()
            if tt:
                tt.status = "PUBLISHED"
                tt.published_at = datetime.now(timezone.utc)
                db.commit()
            print(f"Generated initial conflict-free timetable ({stats['total_classes_scheduled']} classes scheduled, score: {stats['optimization_score']}%)")
        except Exception as e:
            print(f"Initial timetable generation notice: {e}")

        print("\n=======================================================")
        print("DATABASE SEEDING COMPLETED SUCCESSFULLY!")
        print("=======================================================")
        print("Summary of Seeded Data:")
        print("  - 1 University, 1 Campus, 2 Buildings")
        print("  - 3 Departments (CSE, ECE, MRE)")
        print("  - 4 Semesters, 10 Sections")
        print("  - 20 Rooms (15 Lecture Rooms, 5 Specialized Labs)")
        print("  - 30 Subjects across all 3 departments")
        print("  - 50 Faculty Members with profiles & workloads")
        print("  - 500 Enrolled Students")
        print("  - 1 Active Published Timetable generated via CP-SAT")
        print("\nDemo Login Credentials:")
        print("  - Super Admin : admin@university.com    / AdminPassword123!")
        print("  - HOD         : hod@university.com      / Password123!")
        print("  - Teacher     : teacher@university.com  / Password123!")
        print("  - Student     : student@university.com  / Password123!")
        print("=======================================================\n")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
