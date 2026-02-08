"""
byceps.services.bungalow_contest.bungalow_contest_image_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from pathlib import Path
from uuid import UUID

from byceps.byceps_app import get_current_byceps_app
from byceps.database import db
from byceps.services.party.models import PartyID
from byceps.util import upload as uploader
from byceps.util.image.dimensions import determine_dimensions
from byceps.util.image.image_type import determine_image_type
from byceps.util.image.thumbnail import create_thumbnail
from byceps.util.result import Err, Ok, Result

from .dbmodels.contestant import DbContestant, DbImage


def upload(
    contestant: DbContestant,
    stream,
    allowed_types,
    maximum_dimensions,
    *,
    caption: str | None = None,
) -> Result[None, str]:
    """Upload a contestant image."""
    image_type_result = determine_image_type(stream, allowed_types)
    if image_type_result.is_err():
        return Err(image_type_result.unwrap_err())

    type_ = image_type_result.unwrap()
    dimensions = determine_dimensions(stream)

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

    return Ok(None)


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
    path_data = get_current_byceps_app().byceps_config.data_path
    return path_data / 'parties' / party_id / 'bungalow-contest'
