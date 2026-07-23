import asyncio
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import AsyncSessionLocal
from src.models.content import Concept, Course, Lesson, Roadmap, RoadmapCourse


async def seed_courses(db: AsyncSession) -> None:
    courses_data: list[dict[str, Any]] = [
        {
            "slug": "python-fundamentals",
            "title": "Python Fundamentals",
            "description": "Master Python from the ground up. Learn syntax, data structures, functions, object-oriented programming, and build real projects.",
            "thumbnail": "https://images.unsplash.com/photo-1526379095098-d400fd843cea?w=800&auto=format&fit=crop",
            "category": "Backend",
            "programming_language": "Python",
            "technology": "Python",
            "difficulty": "beginner",
            "estimated_duration": 1800,
            "instructor": "DSir Learning Team",
            "skills": ["Python", "Data Structures", "OOP", "File I/O", "Error Handling"],
            "learning_objectives": [
                "Write clean, idiomatic Python code",
                "Understand variables, types, and control flow",
                "Build reusable functions and classes",
                "Handle errors and work with files",
            ],
            "is_published": True,
            "modules": [
                {
                    "slug": "getting-started",
                    "title": "Getting Started with Python",
                    "description": "Install Python, write your first program, and learn the basics.",
                    "order": 1,
                    "lessons": [
                        {
                            "slug": "introduction",
                            "title": "Introduction to Python",
                            "lesson_type": "reading",
                            "position": 1,
                            "duration_minutes": 15,
                            "content": {
                                "body": '# Introduction to Python\n\nPython is a versatile, high-level programming language known for its readability and simplicity. It\'s used in web development, data science, automation, and more.\n\n## Why Python?\n\n- Easy to learn and read\n- Huge community and ecosystem\n- Versatile: web, data, AI, automation\n\n## Your First Program\n\n```python\nprint("Hello, World!")\n```\n\nRun this code to see Python in action!'
                            },
                        },
                        {
                            "slug": "variables-and-data-types",
                            "title": "Variables and Data Types",
                            "lesson_type": "reading",
                            "position": 2,
                            "duration_minutes": 25,
                            "content": {
                                "body": '# Variables and Data Types\n\nIn Python, variables are created by assigning a value to a name.\n\n```python\nname = "Alice"\nage = 30\nis_student = True\n```\n\n## Common Data Types\n\n- `str` - text\n- `int` - whole numbers\n- `float` - decimal numbers\n- `bool` - True or False\n- `list` - ordered collection\n- `dict` - key-value pairs\n\nTry creating your own variables in the code editor.'
                            },
                        },
                    ],
                },
                {
                    "slug": "control-flow",
                    "title": "Control Flow",
                    "description": "Learn conditionals and loops to control program execution.",
                    "order": 2,
                    "lessons": [
                        {
                            "slug": "conditionals",
                            "title": "Conditionals",
                            "lesson_type": "reading",
                            "position": 1,
                            "duration_minutes": 20,
                            "content": {
                                "body": '# Conditionals\n\nUse `if`, `elif`, and `else` to make decisions in your code.\n\n```python\nscore = 85\nif score >= 90:\n    print("A")\nelif score >= 80:\n    print("B")\nelse:\n    print("Keep trying!")\n```'
                            },
                        },
                        {
                            "slug": "loops",
                            "title": "Loops",
                            "lesson_type": "reading",
                            "position": 2,
                            "duration_minutes": 25,
                            "content": {
                                "body": "# Loops\n\nRepeat actions with `for` and `while` loops.\n\n```python\nfor i in range(5):\n    print(i)\n\ncount = 0\nwhile count < 5:\n    print(count)\n    count += 1\n```"
                            },
                        },
                    ],
                },
                {
                    "slug": "functions",
                    "title": "Functions",
                    "description": "Define reusable blocks of code with functions.",
                    "order": 3,
                    "lessons": [
                        {
                            "slug": "defining-functions",
                            "title": "Defining Functions",
                            "lesson_type": "reading",
                            "position": 1,
                            "duration_minutes": 30,
                            "content": {
                                "body": '# Defining Functions\n\nFunctions help you organize code into reusable pieces.\n\n```python\ndef greet(name):\n    return f"Hello, {name}!"\n\nprint(greet("Alice"))\n```'
                            },
                        },
                    ],
                },
            ],
        },
        {
            "slug": "html-css-mastery",
            "title": "HTML & CSS Mastery",
            "description": "Build beautiful, responsive websites from scratch with HTML5 and CSS3.",
            "thumbnail": "https://images.unsplash.com/photo-1621839673705-661705edf509?w=800&auto=format&fit=crop",
            "category": "Frontend",
            "programming_language": "HTML/CSS",
            "technology": "HTML/CSS",
            "difficulty": "beginner",
            "estimated_duration": 1200,
            "instructor": "DSir Learning Team",
            "skills": ["HTML5", "CSS3", "Flexbox", "Grid", "Responsive Design"],
            "learning_objectives": [
                "Build semantic HTML structures",
                "Style pages with CSS",
                "Create responsive layouts",
                "Understand the box model",
            ],
            "is_published": True,
            "modules": [
                {
                    "slug": "html-basics",
                    "title": "HTML Basics",
                    "description": "Learn the building blocks of the web.",
                    "order": 1,
                    "lessons": [
                        {
                            "slug": "what-is-html",
                            "title": "What is HTML?",
                            "lesson_type": "reading",
                            "position": 1,
                            "duration_minutes": 15,
                            "content": {
                                "body": "# What is HTML?\n\nHTML (HyperText Markup Language) is the standard markup language for documents designed to be displayed in a web browser.\n\n```html\n<!DOCTYPE html>\n<html>\n  <body>\n    <h1>Hello, World!</h1>\n  </body>\n</html>\n```"
                            },
                        },
                    ],
                },
                {
                    "slug": "css-fundamentals",
                    "title": "CSS Fundamentals",
                    "description": "Style your HTML with CSS.",
                    "order": 2,
                    "lessons": [
                        {
                            "slug": "selectors-and-properties",
                            "title": "Selectors and Properties",
                            "lesson_type": "reading",
                            "position": 1,
                            "duration_minutes": 25,
                            "content": {
                                "body": "# Selectors and Properties\n\nCSS selects HTML elements and applies styles to them.\n\n```css\nh1 {\n  color: blue;\n  font-size: 24px;\n}\n```"
                            },
                        },
                    ],
                },
            ],
        },
        {
            "slug": "javascript-zero-to-advanced",
            "title": "JavaScript From Zero to Advanced",
            "description": "Go from JavaScript basics to advanced concepts like async programming and DOM manipulation.",
            "thumbnail": "https://images.unsplash.com/photo-1579468118864-1b9ea3c0db4b?w=800&auto=format&fit=crop",
            "category": "Frontend",
            "programming_language": "JavaScript",
            "technology": "JavaScript",
            "difficulty": "intermediate",
            "estimated_duration": 2400,
            "instructor": "DSir Learning Team",
            "skills": ["JavaScript", "ES6+", "DOM", "Async/Await", "Fetch API"],
            "learning_objectives": [
                "Understand JavaScript fundamentals",
                "Work with arrays, objects, and functions",
                "Manipulate the DOM",
                "Handle asynchronous operations",
            ],
            "is_published": True,
            "modules": [
                {
                    "slug": "js-basics",
                    "title": "JavaScript Basics",
                    "description": "Variables, types, and control flow in JavaScript.",
                    "order": 1,
                    "lessons": [
                        {
                            "slug": "variables-and-types",
                            "title": "Variables and Types",
                            "lesson_type": "reading",
                            "position": 1,
                            "duration_minutes": 20,
                            "content": {
                                "body": '# Variables and Types\n\nJavaScript has `let`, `const`, and `var` for declaring variables.\n\n```javascript\nconst name = "Alice";\nlet age = 30;\n```'
                            },
                        },
                    ],
                },
                {
                    "slug": "dom-manipulation",
                    "title": "DOM Manipulation",
                    "description": "Interact with web pages using JavaScript.",
                    "order": 2,
                    "lessons": [
                        {
                            "slug": "selecting-elements",
                            "title": "Selecting Elements",
                            "lesson_type": "reading",
                            "position": 1,
                            "duration_minutes": 25,
                            "content": {
                                "body": "# Selecting Elements\n\nUse JavaScript to select and modify HTML elements.\n\n```javascript\nconst heading = document.querySelector('h1');\nheading.textContent = 'Hello, JavaScript!';\n```"
                            },
                        },
                    ],
                },
            ],
        },
        {
            "slug": "fastapi-backend-development",
            "title": "FastAPI Backend Development",
            "description": "Build high-performance APIs with Python and FastAPI.",
            "thumbnail": "https://images.unsplash.com/photo-1555066931-43669f2e7f2a?w=800&auto=format&fit=crop",
            "category": "Backend",
            "programming_language": "Python",
            "technology": "FastAPI",
            "difficulty": "advanced",
            "estimated_duration": 2100,
            "instructor": "DSir Learning Team",
            "skills": ["FastAPI", "Pydantic", "SQLAlchemy", "Authentication", "API Design"],
            "learning_objectives": [
                "Build APIs with FastAPI",
                "Validate data with Pydantic",
                "Connect to databases with SQLAlchemy",
                "Implement authentication and authorization",
            ],
            "is_published": True,
            "modules": [
                {
                    "slug": "fastapi-introduction",
                    "title": "Introduction to FastAPI",
                    "description": "Get started with FastAPI and Pydantic.",
                    "order": 1,
                    "lessons": [
                        {
                            "slug": "what-is-fastapi",
                            "title": "What is FastAPI?",
                            "lesson_type": "reading",
                            "position": 1,
                            "duration_minutes": 15,
                            "content": {
                                "body": '# What is FastAPI?\n\nFastAPI is a modern, fast web framework for building APIs with Python.\n\n```python\nfrom fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get("/")\ndef read_root():\n    return {"message": "Hello, World!"}\n```'
                            },
                        },
                    ],
                },
                {
                    "slug": "pydantic-models",
                    "title": "Pydantic Models",
                    "description": "Validate and serialize data with Pydantic.",
                    "order": 2,
                    "lessons": [
                        {
                            "slug": "defining-schemas",
                            "title": "Defining Schemas",
                            "lesson_type": "reading",
                            "position": 1,
                            "duration_minutes": 30,
                            "content": {
                                "body": "# Defining Schemas\n\nPydantic models provide validation and serialization.\n\n```python\nfrom pydantic import BaseModel\n\nclass User(BaseModel):\n    name: str\n    age: int\n```"
                            },
                        },
                    ],
                },
            ],
        },
        {
            "slug": "full-stack-web-development",
            "title": "Full Stack Web Development",
            "description": "Build complete web applications with Next.js, React, and a backend API.",
            "thumbnail": "https://images.unsplash.com/photo-1517694712202-14d9537d8fa7?w=800&auto=format&fit=crop",
            "category": "Full Stack",
            "programming_language": "TypeScript",
            "technology": "Next.js",
            "difficulty": "intermediate",
            "estimated_duration": 3600,
            "instructor": "DSir Learning Team",
            "skills": ["React", "Next.js", "TypeScript", "Tailwind CSS", "API Integration"],
            "learning_objectives": [
                "Build frontend interfaces with React",
                "Create full-stack apps with Next.js",
                "Integrate frontend with APIs",
                "Deploy full-stack applications",
            ],
            "is_published": True,
            "modules": [
                {
                    "slug": "react-basics",
                    "title": "React Basics",
                    "description": "Build UI components with React.",
                    "order": 1,
                    "lessons": [
                        {
                            "slug": "components-and-props",
                            "title": "Components and Props",
                            "lesson_type": "reading",
                            "position": 1,
                            "duration_minutes": 25,
                            "content": {
                                "body": "# Components and Props\n\nReact applications are built from components.\n\n```jsx\nfunction Welcome({ name }) {\n  return <h1>Hello, {name}</h1>;\n}\n```"
                            },
                        },
                    ],
                },
                {
                    "slug": "nextjs-fundamentals",
                    "title": "Next.js Fundamentals",
                    "description": "Build full-stack apps with Next.js.",
                    "order": 2,
                    "lessons": [
                        {
                            "slug": "pages-and-routes",
                            "title": "Pages and Routes",
                            "lesson_type": "reading",
                            "position": 1,
                            "duration_minutes": 30,
                            "content": {
                                "body": "# Pages and Routes\n\nNext.js uses file-system based routing. Create a file in `pages/` or `app/` to define a route."
                            },
                        },
                    ],
                },
            ],
        },
    ]

    for course_data in courses_data:
        course = Course(
            id=uuid.uuid4(),
            slug=course_data["slug"],
            title=course_data["title"],
            description=course_data["description"],
            thumbnail=course_data["thumbnail"],
            category=course_data["category"],
            programming_language=course_data["programming_language"],
            technology=course_data["technology"],
            difficulty=course_data["difficulty"],
            estimated_duration=course_data["estimated_duration"],
            instructor=course_data["instructor"],
            skills=course_data["skills"],
            learning_objectives=course_data["learning_objectives"],
            is_published=course_data["is_published"],
        )
        db.add(course)
        await db.flush()

        for module_data in course_data["modules"]:
            concept = Concept(
                id=uuid.uuid4(),
                course_id=course.id,
                slug=module_data["slug"],
                title=module_data["title"],
                description=module_data["description"],
                order=module_data["order"],
                prerequisites=[],
            )
            db.add(concept)
            await db.flush()

            for lesson_data in module_data["lessons"]:
                lesson = Lesson(
                    id=uuid.uuid4(),
                    concept_id=concept.id,
                    slug=lesson_data["slug"],
                    title=lesson_data["title"],
                    content=lesson_data["content"],
                    lesson_type=lesson_data["lesson_type"],
                    position=lesson_data["position"],
                    duration_minutes=lesson_data["duration_minutes"],
                    meta={},
                )
                db.add(lesson)


async def seed_roadmap(db: AsyncSession, course_ids: list[uuid.UUID]) -> None:
    roadmap = Roadmap(
        id=uuid.uuid4(),
        slug="full-stack-developer",
        title="Full Stack Developer",
        description="Become a full stack developer with Python, JavaScript, and modern web technologies.",
        is_published=True,
    )
    db.add(roadmap)
    await db.flush()

    for position, course_id in enumerate(course_ids, start=1):
        db.add(RoadmapCourse(roadmap_id=roadmap.id, course_id=course_id, position=position))


async def main() -> None:
    async with AsyncSessionLocal() as db:
        await seed_courses(db)
        await db.commit()


if __name__ == "__main__":
    asyncio.run(main())
