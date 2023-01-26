==========================
LANresort Bungalow Contest
==========================

At our LANresort_ events, which are LAN parties in holiday village
bungalows, we have the "bungalow contest". Participants can present
their decorated bungalows and all attendees can rate them.

This repository contains code that extends the BYCEPS_ LAN party
platform to provide a user frontend to register and vote for bungalows
as well as an admin UI to manage the contest and see the partially
aggregated ratings.

The implementation depends on the actual `bungalows system`_
(specifically, the "bungalow occupation" entity, which is the
information that a bungalow is occupied and by which users) that has
been open-sourced in 2023.

**However**, it should be easy to make the contest system independent of
the bungalows system by cutting out the connection to the bungalow
occupation.

There can be one contest per party.

While the contest system does not work independently right out of the
box, it serves as an example of how an extension to BYCEPS can look
like.

.. _LANresort: https://www.lanresort.de/
.. _BYCEPS: https://byceps.nwsnet.de/
.. _bungalows system: https://github.com/lanresort/byceps-bungalows


Installation
============

To integrate this with BYCEPS:

- Drop the code into a BYCEPS installation.
- Register the blueprints (in ``byceps/blueprints/blueprints.py``):

  - site blueprint: ``site.bungalow_contest`` to URL path
    ``/bungalow-contest``

  - admin blueprint: ``admin.bungalow_contest`` to URL path
    ``/admin/bungalow-contest``

- Link to those URL paths in your party website's and the admin UI's
  respective navigations.


Screenshots
===========


The list display of candidates during the rating phase looks like this:

.. figure:: https://raw.githubusercontent.com/lanresort/bungalowcontest/main/screenshots/bungalow-contest_rating.png
   :align: left
   :alt: Screenshot of bungalow contest candidates rating
   :height: 565
   :width: 800


The integrated admin UI for a bungalow contest looks like this:

.. figure:: https://raw.githubusercontent.com/lanresort/bungalowcontest/main/screenshots/bungalow-contest_admin.png
   :align: left
   :alt: Screenshot of bungalow contest admin UI
   :height: 1130
   :width: 800


Author
======

The bungalow contest system was created, and is developed and
maintained, by Jochen Kupperschmidt.


License
=======

The bungalow contest system is licensed under the `BSD 3-Clause "New" or
"Revised" License <https://choosealicense.com/licenses/bsd-3-clause/>`_.

The license text is provided in the `LICENSE <LICENSE>`_ file.
