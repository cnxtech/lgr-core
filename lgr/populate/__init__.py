# -*- coding: utf-8 -*-
"""
__init__.py - Populate variants in an LGR
"""
from __future__ import unicode_literals

import logging

from lgr.exceptions import VariantAlreadyExists, NotInLGR
from lgr.validate.symmetry import check_symmetry
from lgr.validate.transitivity import check_transitivity
from lgr.utils import format_cp

logger = logging.getLogger(__name__)


def populate_lgr(lgr):
    """
    Populate an LGR with missing variants, and fix symmetry and transitivity

    :param lgr: The LGR to be populated.
    :return: Result of checks and summary as a string
    """
    now_in_lgr = []
    # not in LGR variants
    for a in lgr.repertoire:
        for b in a.get_variants():
            try:
                lgr.get_variants(b.cp)
            except NotInLGR:
                if b.cp not in now_in_lgr:
                    logger.info("Add missing code point '{}' in LGR as it is a variant of '{}'".format(
                        format_cp(b.cp), format_cp(a.cp)))
                    lgr.add_cp(b.cp)
                    now_in_lgr.append(b.cp)
                # add current code point as variant for missing code point
                logger.info("Add code point '{}' as variant of '{}' for symmetry".format(format_cp(a.cp),
                                                                                         format_cp(b.cp)))
                lgr.add_variant(b.cp, a.cp)

    while not check_symmetry(lgr, None) or not check_transitivity(lgr, None):
        # symmetry
        for a in lgr.repertoire:
            for b in a.get_variants():
                # Variant is defined in repertoire
                # let's see if the original character is in its
                # variants
                if a.cp not in [var.cp for var in lgr.get_variants(b.cp)]:
                    logger.info("Add code point '{}' as variant of '{}' for symmetry".format(format_cp(a.cp),
                                                                                             format_cp(b.cp)))
                    lgr.add_variant(b.cp, a.cp)

        # transitivity
        for a in lgr.repertoire:
            for b in a.get_variants():
                for c in [var for var in lgr.get_variants(b.cp) if var.cp != a.cp]:
                    # Iterate through all second-level variants
                    # which are not the original code point
                    if c.cp not in [var.cp for var in a.get_variants()]:
                        logger.info("Add code point '{}' as variant of '{}' for transitivity with '{}'".format(
                            format_cp(c.cp), format_cp(a.cp), format_cp(b.cp)))
                        lgr.add_variant(a.cp, c.cp)
