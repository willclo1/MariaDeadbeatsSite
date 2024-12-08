from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from datetime import datetime, timezone
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login


class Users(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
                                                unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True,
                                             unique=True)
    # can use this for a bonus feature - last user access
    time_of_last_access: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    is_admin: so.Mapped[bool] = so.mapped_column(sa.Boolean)

    def __repr__(self):
        return '<Users {}>'.format(self.username)

    def set_is_admin(self, is_admin: bool):
        self.is_admin = is_admin

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class BannedUsers(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
                                                unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True,
                                             unique=True)


class UserLogs(db.Model):
    log_id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)
    team_name: so.Mapped[str] = so.mapped_column(sa.String(50), nullable=False)
    yearID: so.Mapped[int] = so.mapped_column(sa.SmallInteger, nullable=False)
    time_of_query: so.Mapped[datetime] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc), index=True)


@login.user_loader
def load_admin(user_id):
    return db.session.get(Users, int(user_id))
