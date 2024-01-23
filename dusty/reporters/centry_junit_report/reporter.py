#!/usr/bin/python3
# coding=utf-8
# pylint: disable=I0011,E0401

#   Copyright 2024 getcarrier.io
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""
    Reporter: Centry jUnit report
"""

import requests

from dusty.tools import log
from dusty.models.module import DependentModuleModel
from dusty.models.reporter import ReporterModel


class Reporter(DependentModuleModel, ReporterModel):
    """ Report findings from scanners """

    def __init__(self, context):
        """ Initialize reporter instance """
        super().__init__()
        self.context = context
        self.config = \
            self.context.config["reporters"][__name__.split(".")[-2]]

    def report(self):
        """ Report """
        log.info("Sending jUnit report to Centry")
        # Get options
        bucket = self.config.get("bucket")
        tgtobj = self.config.get("object")
        # Get jUnit report path
        junit_report_file = \
            self.context.performers["reporting"].get_module_meta("junit", "report_file", None)
        if not junit_report_file:
            log.error("jUnit report not present")
            return
        # Send to Centry
        with open(junit_report_file, "rb") as tgt_file:
            requests.post(
                f'{self.config["url"]}/api/v1/artifacts/artifacts/{self.config["project_id"]}/{bucket}',  # pylint: disable=C0301
                files={"file": (f"{tgtobj}", tgt_file)},
                headers={"Authorization": f'Bearer {self.config["token"]}'},
                verify=self.config.get("ssl_verify", False),
            )

    @staticmethod
    def fill_config(data_obj):
        """ Make sample config """
        data_obj.insert(
            len(data_obj), "bucket", "sast",
            comment="Target bucket"
        )
        data_obj.insert(
            len(data_obj), "object", "target.xml",
            comment="Target object"
        )

    @staticmethod
    def validate_config(config):
        """ Validate config """
        required = ["bucket", "object"]
        not_set = [item for item in required if item not in config]
        if not_set:
            error = f"Required configuration options not set: {', '.join(not_set)}"
            log.error(error)
            raise ValueError(error)

    @staticmethod
    def depends_on():
        """ Return required depencies """
        return ["junit"]

    @staticmethod
    def get_name():
        """ Reporter name """
        return "Centry jUnit report"

    @staticmethod
    def get_description():
        """ Reporter description """
        return "Centry REST API jUnit reporter"
