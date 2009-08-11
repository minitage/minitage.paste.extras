****************************************************************
Paste Scripts to install profiles into minitage based projects
****************************************************************

.. contents::

What is minitage.paste
=======================

Those are PasteScripts to help creating out projects living inside minitage.
You ll find in there:

Projects profiles
==================

    - minitage.instances.cas: create a cas instance

Usage
======

Use throught paster::

    easy_install minitage.paste.cas
    paster create -t minitage.instances.cas target_project

This will create a new project and a new minilay in your current minitage.

