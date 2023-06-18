
from library.py.configuration_file import KConfigurationFile
from library.py.setup_tools import KModuleParams
from library.py.kafka_consumer import KMessageReader
import library.py.scripts as scripts
import library.py.json_tools as jsontools
import library.py.helpers as helpers
import os, logging, pytest, sys, shutil, json
logger = logging.getLogger(__name__)

# The below two variables are used by setup_tools.prepare_test_env
testModuleParams = KModuleParams(sys.modules[__name__])
confFile = KConfigurationFile(testModuleParams.test_conf_file)

# Changes in pmacctd.conf (or nfaccctd.conf), which are test case specific
@pytest.fixture(scope="module")
def prepare_config_local(request):
    confFile.replace_value_of_key('bgp_daemon_tag_map', testModuleParams.pmacct_mount_folder + '/pretag-00.map')
    confFile.replace_value_of_key('bmp_daemon_ip', '0.0.0.0')
    confFile.replace_value_of_key('bmp_daemon_port', '8989')
    confFile.replace_value_of_key('bmp_daemon_msglog_kafka_topic', testModuleParams.kafka_topic_name)
    confFile.replace_value_of_key('bmp_daemon_msglog_kafka_config_file', '/var/log/pmacct/librdkafka.conf')
    confFile.replace_value_of_key('bmp_daemon_msglog_kafka_avro_schema_registry', 'http://schema-registry:8081')
    confFile.replace_value_of_key('bmp_daemon_msglog_avro_schema_file', testModuleParams.pmacct_output_folder + '/flow_avroschema.avsc')
    confFile.print_to_file(testModuleParams.results_conf_file)


def test(check_root_dir, kafka_infra_setup_teardown, prepare_test, prepare_config_local, prepare_pcap, pmacct_setup_teardown):
    consumer = KMessageReader(testModuleParams.kafka_topic_name, testModuleParams.results_msg_dump)
    pcap_config_files, output_files, log_files = prepare_pcap
    pcap_config_file = pcap_config_files[0]
    output_file = output_files[0]

    # import yaml
    # with open(pcap_config_file) as f:
    #     data = yaml.load(f, Loader=yaml.FullLoader)
    # data['network']['map'][0]['repro_ip'] = '127.0.0.1'
    # data['bmp']['collector']['ip'] = '127.0.0.1'
    # data['bmp']['collector']['port'] = '2929'
    # with open(pcap_config_file, 'w') as f:
    #     data = yaml.dump(data, f)

    # Important to keep the indenting
    confPcap = KConfigurationFile(pcap_config_file)
    confPcap.replace_value_of_key('    repro_ip', '127.0.0.1')
    confPcap.replace_value_of_key('    ip', '127.0.0.1')
    confPcap.replace_value_of_key('    port', '2929')
    confPcap.print_to_file(pcap_config_file)

    assert os.path.isfile(pcap_config_file)
    scripts.replay_pcap_file(pcap_config_file)
    messages = consumer.get_messages(120, 131)

    logger.info('Checking for ERROR or WARN')

    assert not helpers.check_regex_sequence_in_file(testModuleParams.results_log_file, ['(ERROR|WARN)'])

    assert messages!=None and len(messages) > 0
    with open(output_file) as f:
        lines = f.readlines()
    jsons = [json.dumps(msg.value()) for msg in messages]
    ignore_fields = ['timestamp_max', 'peer_ip_src', 'timestamp_arrival', 'stamp_inserted', 'timestamp_min', \
                     'stamp_updated']
    assert jsontools.compare_json_lists(jsons, lines, ignore_fields)
