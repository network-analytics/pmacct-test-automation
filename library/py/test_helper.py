###################################################
# Automated Testing Framework for Network Analytics
# Wrapper class for common test case functionality
# nikolaos.tsokas@swisscom.com 22/2/2024
###################################################

import logging
import library.py.test_tools as test_tools
import library.py.helpers as helpers
import library.py.scripts as scripts
from library.py.test_params import KModuleParams
from typing import List

logger = logging.getLogger(__name__)


class KTestHelper:

    def __init__(self, testparams: KModuleParams, consumers):
        self.params = testparams
        self.consumers = consumers
        self.ignored_fields = []

    def spawn_traffic_container(self, container_name: str, detached: bool = False):
        logger.debug('Traffic folders: ' + str(self.params.traffic_folders))
        pcap_folder = self.params.traffic_folders.get_path_like(container_name)
        return scripts.replay_pcap(pcap_folder, detached)

    def delete_traffic_container(self, container_name: str):
        pcap_folder = self.params.traffic_folders.get_path_like(container_name)
        return scripts.stop_and_remove_traffic_container(pcap_folder)

    def set_ignored_fields(self, ignored_fields):
        self.ignored_fields = ignored_fields

    def read_and_compare_messages(self, topic_name: str, reference_json: str, wait_time: int = 120):
        consumer = self.consumers.get_consumer_of_topic_like(topic_name)
        return test_tools.read_and_compare_messages(consumer, self.params, reference_json,
                                                    self.ignored_fields, wait_time)

    def transform_log_file(self, log_tag: str, name: str = None):
        logfile = self.params.log_files.get_path_like(log_tag)
        repro_ip = None
        if name:
            repro_ip = helpers.get_reproduction_ip(self.params.traffic_folders.get_path_like(name) +
                                                   '/pcap0/traffic-reproducer.yml')
        test_tools.transform_log_file(logfile, repro_ip)

    def check_file_regex_sequence_in_pmacct_log(self, log_tag: str, pmacct_name: str = None):
        logfile = self.params.log_files.get_path_like(log_tag)
        pmacct = self.params.get_pmacct_with_name(pmacct_name) if pmacct_name else self.params.pmacct[0]
        return helpers.check_file_regex_sequence_in_file(pmacct.pmacct_log_file, logfile)

    def check_regex_sequence_in_pmacct_log(self, regexes: List, pmacct_name: str = None):
        pmacct = self.params.get_pmacct_with_name(pmacct_name) if pmacct_name else self.params.pmacct[0]
        return helpers.check_regex_sequence_in_file(pmacct.pmacct_log_file, regexes)

    def wait_and_check_logs(self, log_tag: str, max_seconds: int, seconds_repeat: int):
        logfile = self.params.log_files.get_path_like(log_tag)
        return helpers.retry_until_true('Checking expected logs',
                                        lambda: helpers.check_file_regex_sequence_in_file(self.params.pmacct_log_file,
                                                                                          logfile),
                                        max_seconds, seconds_repeat)

    def check_regex_in_pmacct_log(self, regex: str, pmacct_name: str = None):
        pmacct = self.params.get_pmacct_with_name(pmacct_name) if pmacct_name else self.params.pmacct[0]
        return helpers.check_regex_sequence_in_file(pmacct.pmacct_log_file, [regex])

    def disconnect_consumers(self):
        for c in self.consumers:
            c.disconnect()
