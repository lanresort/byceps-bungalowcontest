"""
byceps.services.bungalow_contest.image_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from pathlib import Path
from typing import Optional
from uuid import UUID

from flask import abort, current_app

from ...database import db
from ...util.image import create_thumbnail
from ...util import upload as uploader
from ...typing import PartyID

from ..image import service as image_service
from ..image.service import ImageTypeProhibited

from .models.contestant import Contestant, Image


def upload(
    contestant: Contestant,
    stream,
    allowed_types,
    maximum_dimensions,
    *,
    caption: Optional[str] = None,
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

    image = Image(contestant.id, caption=caption)
    db.session.add(image)
    db.session.commit()

    images_path = _get_images_path(contestant.contest.party_id)

    # Create path if it doesn't exist.
    images_path.mkdir(exist_ok=True)

    target_filename = images_path / image.filename

    # Might raise `FileExistsError`.
    uploader.store(stream, target_filename)


def delete(image_id: UUID) -> None:
    """Delete the contestant image."""
    image = Image.query.get(image_id)

    if image is None:
        raise ValueError('Unknown image ID')

    # Delete file.
    images_path = _get_images_path(image.contestant.contest.party_id)
    image_path = images_path / image.filename
    uploader.delete(image_path)

    # Delete database record.
    db.session.delete(image)
    db.session.commit()


def _get_images_path(party_id: PartyID) -> Path:
    """Return the file system path for contest images."""
    path_data = current_app.config['PATH_DATA']
    return path_data / 'parties' / party_id / 'bungalow-contest'
