
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)
import pymysql
import os
import re
import uuid
import bcrypt

from dotenv import load_dotenv
from werkzeug.utils import secure_filename

# =================================================
# LOAD ENVIRONMENT VARIABLES
# =================================================

load_dotenv()

# =================================================
# CREATE FLASK APPLICATION
# =================================================

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")

if not app.secret_key:
    raise RuntimeError("SECRET_KEY is missing from the .env file")

# =================================================
# IMAGE UPLOAD SETTINGS
# =================================================

UPLOAD_FOLDER = os.path.join(
    app.root_path, "static", "uploads"
)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


def save_image(image):
    if not image or image.filename == "":
        return None

    if not allowed_file(image.filename):
        raise ValueError(
            "Only PNG, JPG, JPEG and WEBP images are allowed"
        )

    extension = image.filename.rsplit(".", 1)[1].lower()

    filename = secure_filename(
        str(uuid.uuid4()) + "." + extension
    )

    image.save(
        os.path.join(app.config["UPLOAD_FOLDER"], filename)
    )

    return "uploads/" + filename


def delete_image(image_path):
    if not image_path:
        return

    # Delete only files inside our uploads folder.
    filename = os.path.basename(image_path)
    full_path = os.path.join(
        app.config["UPLOAD_FOLDER"], filename
    )

    if os.path.isfile(full_path):
        os.remove(full_path)


# =================================================
# MYSQL CONNECTIONS
# =================================================

def get_db_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor
    )


def get_library_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database="libraryy",
        cursorclass=pymysql.cursors.DictCursor
    )


# =================================================
# HELPER: VALIDATE EMAIL
# =================================================

def valid_email(email):
    return bool(
        re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+",
            email
        )
    )


# =================================================
# HELPER: GET USER TODOS
# =================================================

def get_user_todos(user_id):
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT todo_id, title, is_done, created_at
                FROM todos
                WHERE user_id = %s
                ORDER BY todo_id DESC
                """,
                (user_id,)
            )

            return cursor.fetchall()

    finally:
        connection.close()


# =================================================
# HOME / TO-DO LIST
# =================================================

@app.route("/")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))

    todos = get_user_todos(session["user_id"])

    return render_template(
        "todos.html",
        todos=todos,
        user_name=session["user_name"]
    )


# =================================================
# REGISTER
# =================================================

@app.route("/register", methods=["GET"])
def register():
    return render_template("register.html")


@app.route("/register", methods=["POST"])
def register_post():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not name:
        flash("Name is required", "error")
        return redirect(url_for("register"))

    if len(name) > 100:
        flash("Name is too long", "error")
        return redirect(url_for("register"))

    if not email:
        flash("Email is required", "error")
        return redirect(url_for("register"))

    if not valid_email(email):
        flash("Please enter a valid email", "error")
        return redirect(url_for("register"))

    if not password.strip():
        flash("Password is required", "error")
        return redirect(url_for("register"))

    if not confirm_password.strip():
        flash("Confirm password is required", "error")
        return redirect(url_for("register"))

    if password != confirm_password:
        flash("Passwords do not match", "error")
        return redirect(url_for("register"))

    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (email, name, password_hash)
                VALUES (%s, %s, %s)
                """,
                (email, name, password_hash)
            )

            connection.commit()
            user_id = cursor.lastrowid

    except pymysql.err.IntegrityError:
        connection.rollback()
        flash("Email Already Exists", "error")
        return redirect(url_for("register"))

    finally:
        connection.close()

    session.clear()
    session["user_id"] = user_id
    session["user_name"] = name

    return redirect(url_for("home"))


# =================================================
# LOGIN
# =================================================

@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_post():
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if not email:
        flash("Email is required", "error")
        return redirect(url_for("login"))

    if not valid_email(email):
        flash("Please enter a valid email", "error")
        return redirect(url_for("login"))

    if not password.strip():
        flash("Password is required", "error")
        return redirect(url_for("login"))

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT user_id, name, password_hash
                FROM users
                WHERE email = %s
                """,
                (email,)
            )

            user = cursor.fetchone()

    finally:
        connection.close()

    if user is None:
        flash("Invalid email or password", "error")
        return redirect(url_for("login"))

    password_correct = bcrypt.checkpw(
        password.encode("utf-8"),
        user["password_hash"].encode("utf-8")
    )

    if not password_correct:
        flash("Invalid email or password", "error")
        return redirect(url_for("login"))

    session.clear()
    session["user_id"] = user["user_id"]
    session["user_name"] = user["name"]

    return redirect(url_for("home"))


# =================================================
# ADD TO-DO
# =================================================

@app.route("/todo/add", methods=["POST"])
def add_todo():
    if "user_id" not in session:
        return redirect(url_for("login"))

    title = request.form.get("title", "").strip()

    if not title:
        flash("Title is required", "error")
        return redirect(url_for("home"))

    if len(title) > 200:
        flash("Title is too long", "error")
        return redirect(url_for("home"))

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO todos (user_id, title)
                VALUES (%s, %s)
                """,
                (session["user_id"], title)
            )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    return redirect(url_for("home"))


# =================================================
# EDIT TO-DO
# =================================================

@app.route("/todo/edit/<int:todo_id>", methods=["POST"])
def edit_todo(todo_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    title = request.form.get("title", "").strip()

    if not title:
        flash("Title is required", "error")
        return redirect(url_for("home"))

    if len(title) > 200:
        flash("Title is too long", "error")
        return redirect(url_for("home"))

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE todos
                SET title = %s
                WHERE todo_id = %s AND user_id = %s
                """,
                (title, todo_id, session["user_id"])
            )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    return redirect(url_for("home"))


# =================================================
# TOGGLE TO-DO
# =================================================

@app.route("/todo/toggle/<int:todo_id>", methods=["POST"])
def toggle_todo(todo_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT is_done
                FROM todos
                WHERE todo_id = %s AND user_id = %s
                """,
                (todo_id, session["user_id"])
            )

            todo = cursor.fetchone()

            if todo is None:
                return redirect(url_for("home"))

            new_status = 0 if todo["is_done"] == 1 else 1

            cursor.execute(
                """
                UPDATE todos
                SET is_done = %s
                WHERE todo_id = %s AND user_id = %s
                """,
                (new_status, todo_id, session["user_id"])
            )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    return redirect(url_for("home"))


# =================================================
# DELETE TO-DO
# =================================================

@app.route("/todo/delete/<int:todo_id>", methods=["POST"])
def delete_todo(todo_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM todos
                WHERE todo_id = %s AND user_id = %s
                """,
                (todo_id, session["user_id"])
            )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    return redirect(url_for("home"))


# =================================================
# LOGOUT
# =================================================

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# =================================================
# LIBRARY: SHOW BOOKS AND AUTHORS
# =================================================

@app.route("/library")
def library():
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_library_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT book_id, title, price, author_id, image
                FROM BOOK
            """)
            books = cursor.fetchall()

            cursor.execute("""
                SELECT author_id, name, country, image
                FROM AUTHOR
            """)
            authors = cursor.fetchall()

        return render_template(
            "library.html",
            books=books,
            authors=authors
        )

    finally:
        connection.close()


# =================================================
# ADD BOOK
# =================================================

@app.route("/library/book/add", methods=["POST"])
def add_book():
    if "user_id" not in session:
        return redirect(url_for("login"))

    title = request.form.get("title", "").strip()
    price_text = request.form.get("price", "").strip()
    author_text = request.form.get("author_id", "").strip()
    image = request.files.get("image")

    if not title or not price_text or not author_text:
        flash("Title, price and author are required", "error")
        return redirect(url_for("library"))

    connection = None
    image_path = None

    try:
        price = float(price_text)
        author_id = int(author_text)

        if price < 0 or author_id <= 0:
            raise ValueError("Enter a valid price and author ID")

        image_path = save_image(image)

        connection = get_library_connection()

        with connection.cursor() as cursor:
            # Check that the author exists
            cursor.execute(
                "SELECT author_id FROM AUTHOR WHERE author_id = %s",
                (author_id,)
            )

            author = cursor.fetchone()

            if author is None:
                if image_path:
                    delete_image(image_path)

                flash("Author does not exist", "error")
                return redirect(url_for("library"))

            cursor.execute("""
                INSERT INTO BOOK (title, price, author_id, image)
                VALUES (%s, %s, %s, %s)
            """, (title, price, author_id, image_path))

        connection.commit()

    except (ValueError, TypeError) as error:
        if image_path:
            delete_image(image_path)

        flash(str(error) or "Enter valid book information", "error")
        return redirect(url_for("library"))

    except pymysql.MySQLError as error:
        if connection:
            connection.rollback()

        if image_path:
            delete_image(image_path)

        print("ADD BOOK DATABASE ERROR:", error)
        flash("Could not add book. Check the database and author ID.", "error")
        return redirect(url_for("library"))

    finally:
        if connection:
            connection.close()

    flash("Book added successfully", "success")
    return redirect(url_for("library"))


# =================================================
# EDIT BOOK
# =================================================

@app.route("/library/book/edit/<int:book_id>", methods=["POST"])
def edit_book(book_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    title = request.form.get("title", "").strip()
    price_text = request.form.get("price", "").strip()
    author_text = request.form.get("author_id", "").strip()
    image = request.files.get("image")

    if not title or not price_text or not author_text:
        flash("Title, price and author are required", "error")
        return redirect(url_for("library"))

    connection = None
    new_image_path = None
    old_image_path = None

    try:
        price = float(price_text)
        author_id = int(author_text)

        if price < 0 or author_id <= 0:
            raise ValueError("Enter a valid price and author ID")

        connection = get_library_connection()

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT image FROM BOOK WHERE book_id = %s",
                (book_id,)
            )
            book = cursor.fetchone()

            if book is None:
                flash("Book not found", "error")
                return redirect(url_for("library"))

            cursor.execute(
                "SELECT author_id FROM AUTHOR WHERE author_id = %s",
                (author_id,)
            )

            author = cursor.fetchone()

            if author is None:
                flash("Author does not exist", "error")
                return redirect(url_for("library"))

            old_image_path = book["image"]

            # Keep the old image unless a new one is uploaded
            if image and image.filename:
                new_image_path = save_image(image)
                image_path = new_image_path
            else:
                image_path = old_image_path

            cursor.execute("""
                UPDATE BOOK
                SET title = %s,
                    price = %s,
                    author_id = %s,
                    image = %s
                WHERE book_id = %s
            """, (title, price, author_id, image_path, book_id))

        connection.commit()

    except (ValueError, TypeError) as error:
        if new_image_path:
            delete_image(new_image_path)

        flash(str(error) or "Enter valid book information", "error")
        return redirect(url_for("library"))

    except pymysql.MySQLError as error:
        if connection:
            connection.rollback()

        if new_image_path:
            delete_image(new_image_path)

        print("EDIT BOOK DATABASE ERROR:", error)
        flash("Could not update book. Check the database and author ID.", "error")
        return redirect(url_for("library"))

    finally:
        if connection:
            connection.close()

    if new_image_path and old_image_path:
        delete_image(old_image_path)

    flash("Book updated successfully", "success")
    return redirect(url_for("library"))


# =================================================
# ADD AUTHOR
# =================================================

@app.route("/library/author/add", methods=["POST"])
def add_author():
    if "user_id" not in session:
        return redirect(url_for("login"))

    name = request.form.get("name", "").strip()
    country = request.form.get("country", "").strip()
    image = request.files.get("image")

    if not name:
        flash("Author name is required", "error")
        return redirect(url_for("library"))

    connection = None
    image_path = None

    try:
        image_path = save_image(image)

        connection = get_library_connection()

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO AUTHOR (name, country, image)
                VALUES (%s, %s, %s)
            """, (name, country or None, image_path))

        connection.commit()

    except ValueError as error:
        if image_path:
            delete_image(image_path)

        flash(str(error), "error")
        return redirect(url_for("library"))

    except pymysql.MySQLError as error:
        if connection:
            connection.rollback()

        if image_path:
            delete_image(image_path)

        print("ADD AUTHOR DATABASE ERROR:", error)
        flash("Could not add author. Check the AUTHOR table structure.", "error")
        return redirect(url_for("library"))

    finally:
        if connection:
            connection.close()

    flash("Author added successfully", "success")
    return redirect(url_for("library"))


# =================================================
# EDIT AUTHOR
# =================================================

@app.route("/library/author/edit/<int:author_id>", methods=["POST"])
def edit_author(author_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    name = request.form.get("name", "").strip()
    country = request.form.get("country", "").strip()
    image = request.files.get("image")

    if not name:
        flash("Author name is required", "error")
        return redirect(url_for("library"))

    connection = None
    new_image_path = None
    old_image_path = None

    try:
        connection = get_library_connection()

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT image FROM AUTHOR WHERE author_id = %s",
                (author_id,)
            )

            author = cursor.fetchone()

            if author is None:
                flash("Author not found", "error")
                return redirect(url_for("library"))

            old_image_path = author["image"]

            if image and image.filename:
                new_image_path = save_image(image)
                image_path = new_image_path
            else:
                image_path = old_image_path

            cursor.execute("""
                UPDATE AUTHOR
                SET name = %s,
                    country = %s,
                    image = %s
                WHERE author_id = %s
            """, (name, country or None, image_path, author_id))

        connection.commit()

    except ValueError as error:
        if new_image_path:
            delete_image(new_image_path)

        flash(str(error), "error")
        return redirect(url_for("library"))

    except pymysql.MySQLError as error:
        if connection:
            connection.rollback()

        if new_image_path:
            delete_image(new_image_path)

        print("EDIT AUTHOR DATABASE ERROR:", error)
        flash("Could not update author. Check the AUTHOR table structure.", "error")
        return redirect(url_for("library"))

    finally:
        if connection:
            connection.close()

    if new_image_path and old_image_path:
        delete_image(old_image_path)

    flash("Author updated successfully", "success")
    return redirect(url_for("library"))



# =================================================
# DELETE BOOK
# =================================================

@app.route("/library/book/delete/<int:book_id>", methods=["POST"])
def delete_book(book_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = None
    image_path = None

    try:
        connection = get_library_connection()

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT image FROM BOOK WHERE book_id = %s",
                (book_id,)
            )
            book = cursor.fetchone()

            if book is None:
                flash("Book not found", "error")
                return redirect(url_for("library"))

            image_path = book["image"]

            cursor.execute(
                "DELETE FROM BOOK WHERE book_id = %s",
                (book_id,)
            )

        connection.commit()

    except pymysql.MySQLError as error:
        if connection:
            connection.rollback()

        print("DELETE BOOK DATABASE ERROR:", error)
        flash("Could not delete book", "error")
        return redirect(url_for("library"))

    finally:
        if connection:
            connection.close()

    if image_path:
        delete_image(image_path)

    flash("Book deleted successfully", "success")
    return redirect(url_for("library"))


# =================================================
# DELETE AUTHOR
# =================================================

@app.route("/library/author/delete/<int:author_id>", methods=["POST"])
def delete_author(author_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = None
    image_paths = []

    try:
        connection = get_library_connection()

        with connection.cursor() as cursor:
            # Get the author's image
            cursor.execute(
                "SELECT image FROM AUTHOR WHERE author_id = %s",
                (author_id,)
            )
            author = cursor.fetchone()

            if author is None:
                flash("Author not found", "error")
                return redirect(url_for("library"))

            if author["image"]:
                image_paths.append(author["image"])

            # Get images of books belonging to this author
            cursor.execute(
                "SELECT image FROM BOOK WHERE author_id = %s",
                (author_id,)
            )
            books = cursor.fetchall()

            for book in books:
                if book["image"]:
                    image_paths.append(book["image"])

            # Delete the author's books first
            cursor.execute(
                "DELETE FROM BOOK WHERE author_id = %s",
                (author_id,)
            )

            # Then delete the author
            cursor.execute(
                "DELETE FROM AUTHOR WHERE author_id = %s",
                (author_id,)
            )

        connection.commit()

    except pymysql.MySQLError as error:
        if connection:
            connection.rollback()

        print("DELETE AUTHOR DATABASE ERROR:", error)
        flash("Could not delete author", "error")
        return redirect(url_for("library"))

    finally:
        if connection:
            connection.close()

    # Delete the saved image files after database deletion
    for image_path in image_paths:
        delete_image(image_path)

    flash("Author and related books deleted successfully", "success")
    return redirect(url_for("library"))



if __name__ == "__main__":
    app.run(debug=True)
