import functools
import logging
import traceback

from flask import jsonify
from functools import singledispatch
from db import db
from sqlalchemy.exc import OperationalError, IntegrityError

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename="ErrorLog.log",
    encoding="utf-8",
    level=logging.DEBUG,
    format="%(asctime)s %(message)s",
    datefmt="%d/%m/%Y %H:%M:%S ",
)


@singledispatch
def handle_error(exc: Exception):
    db.session.rollback()
    logger.error(f"Unexpected error: {traceback.format_exc()}")
    return jsonify({"error": f"Internal server error {exc}"}), 500


@handle_error.register(ValueError)
def _(exc: ValueError):
    return jsonify({"error": f"Incorrect Value {exc}"}), 400


@handle_error.register(IntegrityError)
def _(exc: IntegrityError):
    db.session.rollback()
    return jsonify({"error": f"Database integrity error {exc}"}), 400


@handle_error.register(OperationalError)
def _(exc: OperationalError):
    db.session.rollback()
    return jsonify({"error": f"Database operation error {exc}"}), 500


def error_handler(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            return handle_error(e)

    return wrapper
