##############################################################################
#
#   Imperial College London
#
#   $Id$
#
#   Copyright (C) 2017 Antonio Berlanga-Taylor
#
#   This program is free software; you can redistribute it and/or
#   modify it under the terms of the GNU General Public License
#   as published by the Free Software Foundation; either version 3
#   of the License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
###############################################################################
"""===========================
Pipeline template
===========================

:Author: Antonio Berlanga-Taylor
:Release: $Id$
:Date: |today|
:Tags: Python

.. Replace the documentation below with your own description of the
   pipeline's purpose

Overview
========

This pipeline pre-processes genome-wide genotype data from a microarray (Illumina, Affymetrix) and carries out quality control
processing. It outputs varies plots, tables and a final QC'd file for downstream analysis (GWAS, imputation, etc.).

See the files :file:``pipeline.ini` and :file:`conf.py` to configure with different parameters and reporting.

The pipeline is based on the UK Biobank protocol and other methods. See references. 

It requires CGAT tools (pipelines and scripts).


Usage
=====

See :ref:`PipelineSettingUp` and :ref:`PipelineRunning` on general
information how to use CGAT pipelines.

Configuration
-------------

The pipeline requires a configured :file:`pipeline.ini` file.
CGATReport report requires a :file:`conf.py` and optionally a
:file:`cgatreport.ini` file (see :ref:`PipelineReporting`).

Default configuration files can be generated by executing:

   python <srcdir>/pipeline_genotype_QC.py config

Input files
-----------

Genotype file as provided by Illumina, Affymetrix or converted to Plink formats.

Requirements
------------

The pipeline requires various tools to be installed:

Default CGAT setup
CGATPipelines
cgat tools


Requirements:

* samtools >= 1.1

Pipeline output
===============

.. Describe output files of the pipeline here

Glossary
========

.. glossary::


Code
====

"""
from ruffus import *

import sys
import os
import sqlite3
import CGAT.Experiment as E
import CGATPipelines.Pipeline as P

# load options from the config file
PARAMS = P.getParameters(
    ["%s/pipeline.ini" % os.path.splitext(__file__)[0],
     "../pipeline.ini",
     "pipeline.ini"])

# add configuration values from associated pipelines
#
# 1. pipeline_annotations: any parameters will be added with the
#    prefix "annotations_". The interface will be updated with
#    "annotations_dir" to point to the absolute path names.
PARAMS.update(P.peekParameters(
    PARAMS["annotations_dir"],
    "pipeline_annotations.py",
    on_error_raise=__name__ == "__main__",
    prefix="annotations_",
    update_interface=True))


# if necessary, update the PARAMS dictionary in any modules file.
# e.g.:
#
# import CGATPipelines.PipelineGeneset as PipelineGeneset
# PipelineGeneset.PARAMS = PARAMS
#
# Note that this is a hack and deprecated, better pass all
# parameters that are needed by a function explicitely.

# -----------------------------------------------
# Utility functions
def connect():
    '''utility function to connect to database.

    Use this method to connect to the pipeline database.
    Additional databases can be attached here as well.

    Returns an sqlite3 database handle.
    '''

    dbh = sqlite3.connect(PARAMS["database_name"])
    statement = '''ATTACH DATABASE '%s' as annotations''' % (
        PARAMS["annotations_database"])
    cc = dbh.cursor()
    cc.execute(statement)
    cc.close()

    return dbh


# ---------------------------------------------------
# Specific pipeline tasks
@transform(("pipeline.ini", "conf.py"),
           regex("(.*)\.(.*)"),
           r"\1.counts")
def countWords(infile, outfile):
    '''count the number of words in the pipeline configuration files.'''

    # the command line statement we want to execute
    statement = '''awk 'BEGIN { printf("word\\tfreq\\n"); } 
    {for (i = 1; i <= NF; i++) freq[$i]++}
    END { for (word in freq) printf "%%s\\t%%d\\n", word, freq[word] }'
    < %(infile)s > %(outfile)s'''

    # execute command in variable statement.
    #
    # The command will be sent to the cluster.  The statement will be
    # interpolated with any options that are defined in in the
    # configuration files or variable that are declared in the calling
    # function.  For example, %(infile)s will we substituted with the
    # contents of the variable "infile".
    P.run()


@transform(countWords,
           suffix(".counts"),
           "_counts.load")
def loadWordCounts(infile, outfile):
    '''load results of word counting into database.'''
    P.load(infile, outfile, "--add-index=word")


# ---------------------------------------------------
# Generic pipeline tasks
@follows(loadWordCounts)
def full():
    pass


@follows(mkdir("report"))
def build_report():
    '''build report from scratch.

    Any existing report will be overwritten.
    '''

    E.info("starting report build process from scratch")
    P.run_report(clean=True)


@follows(mkdir("report"))
def update_report():
    '''update report.

    This will update a report with any changes inside the report
    document or code. Note that updates to the data will not cause
    relevant sections to be updated. Use the cgatreport-clean utility
    first.
    '''

    E.info("updating report")
    P.run_report(clean=False)


@follows(update_report)
def publish_report():
    '''publish report in the CGAT downloads directory.'''

    E.info("publishing report")
    P.publish_report()

if __name__ == "__main__":
    sys.exit(P.main(sys.argv))
