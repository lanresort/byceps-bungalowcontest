"""
byceps.services.bungalow_contest.bungalow_contest_image_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from pathlib import Path
from uuid import UUID

from flask import current_app

from byceps.database import db
from byceps.services.image import image_service
from byceps.services.image.image_service import (
    ImageTypeProhibited,  # Provide to view functions.  # noqa: F401
)
from byceps.typing import PartyID
from byceps.util import upload as uploader
from byceps.util.image import create_thumbnail

from .dbmodels.contestant import DbContestant, DbImage


def upload(
    contestant: DbContestant,
    stream,
    allowed_types,
    maximum_dimensions,
    *,
    caption: str | None = None,
) -> None:
    """Upload a contestant image.

    Raise `ImageTypeProhibited` if the stream data is not of one the
    allowed types.
    """
    type_ = image_service.determine_image_type(stream, allowed_types)
    dimensions = image_service.determine_dimensions(stream)

    # Resize if too large.
    image_too_large = dimensions > maximum_dimensions
    if image_too_large:
        stream = create_thumbnail(stream, type_.name, maximum_dimensions)

    db_image = DbImage(contestant.id, caption=caption)
    db.session.add(db_image)
    db.session.commit()

    images_path = _get_images_path(contestant.contest.party_id)

    # Create path if it doesn't exist.
    images_path.mkdir(exist_ok=True)

    target_filename = images_path / db_image.filename

    # Might raise `FileExistsError`.
    uploader.store(stream, target_filename)


def delete(image_id: UUID) -> None:
    """Delete the contestant image."""
    db_image = db.session.get(DbImage, image_id)

    if db_image is None:
        raise ValueError('Unknown image ID')

    # Delete file.
    images_path = _get_images_path(db_image.contestant.contest.party_id)
    image_path = images_path / db_image.filename
    uploader.delete(image_path)

    # Delete database record.
    db.session.delete(db_image)
    db.session.commit()


def _get_images_path(party_id: PartyID) -> Path:
    """Return the file system path for contest images."""
    path_data = current_app.config['PATH_DATA']
    return path_data / 'parties' / party_id / 'bungalow-contest'
