import os
import timeit
import pytest
from flowlog.parser import (
    load_tag_lookup,
    parse_flow_logs,
    load_protocol_map,
    generate_output,
    main
)


def test_load_tag_lookup():
    lookup = load_tag_lookup('tests/resources/test_tag_lookup.csv')
    expected_lookup = {
        (443, 'tcp'): 'sv_P1',
        (68, 'udp'): 'sv_P2',
        (80, 'tcp'): 'sv_P1',
        (31, 'udp'): 'SV_P3',
        (25, 'tcp'): 'sv_P2'
    }
    assert lookup == expected_lookup


def test_load_protocol_map():
    protocol_map = load_protocol_map('tests/resources/test_protocol_map.json')
    expected_protocol_map = {
        "6": "tcp",
        "17": "udp"
    }
    assert protocol_map == expected_protocol_map


def test_parse_flow_logs_file_not_found():
    lookup = load_tag_lookup('tests/resources/test_tag_lookup.csv')
    protocol_map = load_protocol_map('tests/resources/test_protocol_map.json')
    with pytest.raises(SystemExit) as excinfo:
        parse_flow_logs('nonexistent_flowlog_data.txt', lookup, protocol_map)
    assert excinfo.value.code == 1


def test_parse_flow_logs_invalid():
    lookup = load_tag_lookup('tests/resources/test_tag_lookup.csv')
    protocol_map = load_protocol_map('tests/resources/test_protocol_map.json')
    with pytest.raises(SystemExit) as excinfo:
        parse_flow_logs('tests/resources/invalid_file.png',
                        lookup,
                        protocol_map)
    assert excinfo.value.code == 1


def test_main():
    main('tests/resources/test_flowlog_data.txt',
         'tests/resources/test_tag_lookup.csv',
         'tests/resources/test_protocol_map.json')
    assert True


def test_parse_flow_logs():
    lookup = load_tag_lookup('tests/resources/test_tag_lookup.csv')
    protocol_map = load_protocol_map('tests/resources/test_protocol_map.json')
    tag_counts, combination_counts = parse_flow_logs(
        'tests/resources/test_flowlog_data.txt', lookup, protocol_map)

    expected_tag_counts = {
        'sv_P1': 2,
        'sv_P2': 2,
        'SV_P3': 1,
        'Untagged': 1
    }
    expected_combination_counts = {
        (443, 'tcp'): 1,
        (80, 'tcp'): 1,
        (25, 'tcp'): 1,
        (68, 'udp'): 1,
        (23, 'tcp'): 1,
        (31, 'udp'): 1

    }

    assert tag_counts == expected_tag_counts
    assert combination_counts == expected_combination_counts


def test_parse_flow_logs_invalid_lines():
    lookup = load_tag_lookup('tests/resources/test_tag_lookup.csv')
    protocol_map = load_protocol_map('tests/resources/test_protocol_map.json')
    tag_counts, combination_counts = parse_flow_logs(
        'tests/resources/test_invalid_flowlog_data.txt', lookup, protocol_map)

    expected_tag_counts = {
        'sv_P1': 1,
        'sv_P2': 1,
        'SV_P3': 1
    }
    expected_combination_counts = {
        (443, 'tcp'): 1,
        (25, 'tcp'): 1,
        (31, 'udp'): 1
    }

    assert tag_counts != expected_tag_counts
    assert combination_counts != expected_combination_counts


def test_load_tag_lookup_file_not_found():
    with pytest.raises(SystemExit) as excinfo:
        load_tag_lookup('nonexistent_file.csv')
    assert excinfo.value.code == 1


def test_load_tag_lookup_file_invalid():
    with pytest.raises(SystemExit) as excinfo:
        load_tag_lookup('tests/resources/invalid_file.png')
    assert excinfo.value.code == 1


def test_generate_output_invalid_file():
    with pytest.raises(SystemExit) as excinfo:
        generate_output(None, None)
    assert excinfo.value.code == 1


def test_generate_output():
    tag_counts = {
        'sv_P1': 2,
        'sv_P2': 2,
        'SV_P3': 1,
        'Untagged': 1
    }
    combination_counts = {
        (443, 'tcp'): 1,
        (80, 'tcp'): 1,
        (25, 'tcp'): 1,
        (68, 'udp'): 1,
        (23, 'tcp'): 1,
        (31, 'udp'): 1
    }

    output_filename = 'output.txt'
    # Ensure the file does not exist before the test
    if os.path.exists(output_filename):
        os.remove(output_filename)

    generate_output(tag_counts, combination_counts)

    assert os.path.exists(output_filename)

    with open(output_filename, 'r') as file:
        lines = file.readlines()

    print(lines)
    expected_lines = [
        'Tag Counts:\n', '\n',
        'Tag\t\tCount\n',
        'sv_P1\t\t2\n',
        'sv_P2\t\t2\n',
        'SV_P3\t\t1\n',
        'Untagged\t\t1\n', '\n',
        'Port/Protocol Combination Counts:\n', '\n',
        'Port\tProtocol\tCount\n',
        '443\ttcp\t1\n', '80\ttcp\t1\n',
        '25\ttcp\t1\n', '68\tudp\t1\n',
        '23\ttcp\t1\n', '31\tudp\t1\n'
    ]

    assert lines == expected_lines

    # Clean up
    os.remove(output_filename)


def test_generate_output_performance():
    tag_counts = {
        'sv_P1': 1000,
        'sv_P2': 2000,
        'SV_P3': 1500,
        'Untagged': 500
    }
    combination_counts = {
        (443, 'tcp'): 1000,
        (80, 'tcp'): 2000,
        (25, 'tcp'): 1500,
        (68, 'udp'): 500,
        (23, 'tcp'): 300,
        (31, 'udp'): 700
    }

    output_filename = 'output.txt'
    if os.path.exists(output_filename):
        os.remove(output_filename)

    def benchmark():
        generate_output(tag_counts, combination_counts)

    execution_time = timeit.timeit(benchmark, number=10)
    print(f"Average execution time over 10 \
          runs: {execution_time / 10:.6f} seconds")

    assert os.path.exists(output_filename)

    os.remove(output_filename)
