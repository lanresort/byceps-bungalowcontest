"""
byceps.signals.bungalow_contest
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from blinker import Namespace


bungalow_contest_signals = Namespace()


# fmt: off
contestant_registered = bungalow_contest_signals.signal('contestant-registered')
contestant_updated = bungalow_contest_signals.signal('contestant-updated')
contestant_image_created = bungalow_contest_signals.signal('contestant-image-created')
# fmt: on
