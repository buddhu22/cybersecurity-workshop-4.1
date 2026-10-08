"""Local Flask lost-and-found notice board for a secure development workshop."""

import logging
import os
import secrets
from logging.handlers import RotatingFileHandler
from datetime import date
from pathlib import Path

from flask import Flask, abort, flash, redirect, render_template, request, url_for

from database import NoticeStoreError, create_notice, load_notices, resolve_notice


BASE_DIR = Path(__file__).parent
CATEGORIES = ["Electronics", "Books", "ID Card", "Keys", "Clothing", "Accessories", "Other"]
LOCATION_ZONES = [
    "Library", "Lab Area", "Classroom Block", "Cafeteria", "Sports Area", "Parking Area", "Other"
]
CONTACT_PREFERENCES = ["Campus Helpdesk", "Notice Board", "Department Office"]
ITEM_TYPES = ["Lost", "Found"]
MAX_DESCRIPTION_LENGTH = 500


def configure_logging(app: Flask) -> None:
    """Write concise local application logs without logging notice descriptions."""
    log_path = BASE_DIR / "logs" / "app.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(log_path, maxBytes=100_000, backupCount=3, encoding="utf-8")
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(SECRET_KEY=os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32))
    if test_config:
        app.config.update(test_config)
    configure_logging(app)

    def get_notices() -> list[dict]:
        try:
            return load_notices(app.config.get("DATA_FILE", BASE_DIR / "data" / "notices.json"))
        except NoticeStoreError:
            app.logger.exception("Notice storage is unavailable")
            flash("Notice data is temporarily unavailable. Please try again later.", "error")
            abort(500)

    def validate_form(form) -> tuple[dict[str, str], dict[str, str]]:
        fields = {
            "item_type": form.get("item_type", "").strip(),
            "item_category": form.get("item_category", "").strip(),
            "description": form.get("description", "").strip(),
            "location_zone": form.get("location_zone", "").strip(),
            "date_lost_found": form.get("date_lost_found", "").strip(),
            "contact_preference": form.get("contact_preference", "").strip(),
        }
        errors: dict[str, str] = {}
        if fields["item_type"] not in ITEM_TYPES:
            errors["item_type"] = "Choose Lost or Found."
        if fields["item_category"] not in CATEGORIES:
            errors["item_category"] = "Invalid category selected."
        if not fields["description"]:
            errors["description"] = "Description is required."
        elif len(fields["description"]) > MAX_DESCRIPTION_LENGTH:
            errors["description"] = "Description must be 500 characters or fewer."
        if fields["location_zone"] not in LOCATION_ZONES:
            errors["location_zone"] = "Invalid location zone selected."
        try:
            parsed_date = date.fromisoformat(fields["date_lost_found"])
            if parsed_date > date.today():
                errors["date_lost_found"] = "Date cannot be in the future."
        except ValueError:
            errors["date_lost_found"] = "Enter a valid date."
        if fields["contact_preference"] not in CONTACT_PREFERENCES:
            errors["contact_preference"] = "Choose one of the listed contact preferences."
        return fields, errors

    @app.get("/")
    def index():
        notices = get_notices()
        category = request.args.get("category", "All")
        location = request.args.get("location", "All")
        if category not in ["All", *CATEGORIES]:
            category = "All"
        if location not in ["All", *LOCATION_ZONES]:
            location = "All"
        filtered = [
            notice for notice in notices
            if (category == "All" or notice.get("item_category") == category)
            and (location == "All" or notice.get("location_zone") == location)
        ]
        return render_template(
            "index.html", notices=filtered, categories=CATEGORIES, locations=LOCATION_ZONES,
            selected_category=category, selected_location=location,
            total_count=len(notices),
            lost_count=sum(item.get("status") == "Lost" for item in notices),
            found_count=sum(item.get("status") == "Found" for item in notices),
            resolved_count=sum(item.get("status") == "Resolved" for item in notices),
        )

    @app.get("/notice/<notice_id>")
    def detail(notice_id: str):
        notice = next((item for item in get_notices() if item.get("id") == notice_id), None)
        if notice is None:
            app.logger.info("Notice detail requested for missing ID %s", notice_id)
            abort(404)
        return render_template("detail.html", notice=notice)

    @app.route("/create", methods=["GET", "POST"])
    def create():
        if request.method == "GET":
            return render_template(
                "create.html", categories=CATEGORIES, locations=LOCATION_ZONES,
                contacts=CONTACT_PREFERENCES, item_types=ITEM_TYPES, form_data={}, errors={}, today=date.today().isoformat(),
            )
        fields, errors = validate_form(request.form)
        if errors:
            app.logger.info("Notice creation validation failed for fields: %s", ", ".join(errors))
            flash("Please correct the highlighted fields.", "error")
            return render_template(
                "create.html", categories=CATEGORIES, locations=LOCATION_ZONES,
                contacts=CONTACT_PREFERENCES, item_types=ITEM_TYPES, form_data=fields, errors=errors, today=date.today().isoformat(),
            ), 400
        try:
            notice = create_notice(get_notices(), fields, app.config.get("DATA_FILE", BASE_DIR / "data" / "notices.json"))
        except NoticeStoreError:
            app.logger.exception("Notice creation could not be saved")
            abort(500)
        app.logger.info("Notice %s created", notice["id"])
        flash(f"Notice {notice['id']} was created.", "success")
        return redirect(url_for("detail", notice_id=notice["id"]))

    @app.post("/notice/<notice_id>/resolve")
    def resolve(notice_id: str):
        notices = get_notices()
        try:
            changed = resolve_notice(notices, notice_id, app.config.get("DATA_FILE", BASE_DIR / "data" / "notices.json"))
        except NoticeStoreError:
            app.logger.exception("Notice %s could not be resolved", notice_id)
            abort(500)
        if not changed:
            if not any(item.get("id") == notice_id for item in notices):
                app.logger.info("Resolve requested for missing notice %s", notice_id)
                abort(404)
            flash("This notice has already been resolved.", "info")
        else:
            app.logger.info("Notice %s resolved", notice_id)
            flash("Notice marked as resolved.", "success")
        return redirect(url_for("detail", notice_id=notice_id))

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(_error):
        return render_template("error.html"), 500

    @app.errorhandler(Exception)
    def unexpected_error(error):
        app.logger.exception("Unexpected application error", exc_info=error)
        return render_template("error.html"), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
