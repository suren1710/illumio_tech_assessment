import json
import os
import sys
import csv
import logging
from collections import defaultdict
from typing import DefaultDict, Dict, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')


def load_tag_lookup(filename: str) -> Dict[Tuple[int, str], str]:
    """
    Loads the tag lookup information from a CSV file.

    The CSV file is expected to have three columns:
                        'dstport', 'protocol', and 'tag'.
    The function reads the CSV file, skips the header, 
    and maps each (dstport, protocol) pair to the corresponding tag.

    Args:
        filename (str):
            The path to the CSV file containing the tag lookup data.

    Returns:
        Dict[Tuple[int, str], str]:
            A dictionary mapping (dstport, protocol) tuples to tags.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        Exception: If there is an error reading the file or
        processing its contents.

    Logs:
        INFO: When the tag mappings are successfully loaded.
        ERROR: If there is an issue loading the lookup file or
        processing its contents.
    """
    lookup = {}
    try:
        with open(filename, mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                dstport, protocol, tag = row
                lookup[(int(dstport), protocol.lower())] = tag
        logging.info(f"Loaded {len(lookup)} tag mappings from {filename}")
    except FileNotFoundError:
        logging.error(f"Lookup file not found: {filename}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error loading lookup file: {e}")
        sys.exit(1)
    return lookup


def load_protocol_map(filename):
    """
    Loads the protocol map from a JSON file.

    The JSON file is expected to contain key-value pairs where the keys are
    protocol identifiers (as strings) and the values are protocol
    names (as strings). The functionreads the JSON file and
    returns the resulting dictionary.

    Args:
        filename (str): The path to the JSON file containing the protocol map.

    Returns:
        dict: A dictionary mapping protocol identifiers to protocol names.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        json.JSONDecodeError: If there is an error decoding the JSON file.
        Exception: If there is an error reading the file or
        processing its contents.

    Example:
        >>> load_protocol_map('protocol_map.json')
        {'6': 'tcp', '17': 'udp'}
    """
    with open(filename, 'r') as f:
        return json.load(f)


def parse_flow_logs(
        filename: str,
        lookup: Dict[Tuple[int, str], str],
        protocol_map: dict) -> Tuple[Dict[str, int],
                                     Dict[Tuple[int, str], int]]:
    """
    Parses the flow logs from the given file and generates counts for tags and 
    port/protocol combinations.

    The function reads the flow log file line by line, extracts
    the destination port and protocol, and uses the provided lookup
    and protocol map to categorize and count the occurrences of each tag
    and port/protocol combination.

    Args:
        filename (str): The path to the flow log file.
        lookup (Dict[Tuple[int, str], str]):
            A dictionary mapping (dstport, protocol) tuples to tags.

        protocol_map (dict): 
            A dictionary mapping protocol identifiers to protocol names.

    Returns:
        Tuple[Dict[str, int], Dict[Tuple[int, str], int]]:
            - A dictionary mapping tags to their counts.
            - A dictionary mapping (dstport, protocol) tuples to their counts.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        Exception: If there is an error reading the file or
        processing its contents.

    Example:
        >>> lookup = {(443, 'tcp'): 'sv_P1', (68, 'udp'): 'sv_P2'}
        >>> protocol_map = {'6': 'tcp', '17': 'udp'}
        >>> parse_flow_logs('flowlog_data.txt', lookup, protocol_map)
        ({'sv_P1': 10, 'sv_P2': 5, 'Untagged': 3},
         {(443, 'tcp'): 10, (68, 'udp'): 5, (80, 'tcp'): 3})
    """
    tag_counts: DefaultDict[str, int] = defaultdict(int)
    combination_counts: DefaultDict[Tuple[int, str], int] = defaultdict(int)
    try:
        with open(filename, mode='r') as file:
            for line in file:
                parts = line.strip().split()
                if len(parts) < 8:
                    logging.warning(f"Skipping invalid line: {line.strip()}")
                    continue  # Skip invalid lines
                dstport = int(parts[6])
                protocol = protocol_map.get(parts[7], 'unknown')
                combination_counts[(dstport, protocol)] += 1
                tag = lookup.get((dstport, protocol), "Untagged")
                tag_counts[tag] += 1
        logging.info(f"Parsed flow logs from {filename}")
    except FileNotFoundError:
        logging.error(f"Flow log file not found: {filename}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error parsing flow log file: {e}")
        sys.exit(1)
    return tag_counts, combination_counts


def generate_output(tag_counts: Dict[str, int],
                    combination_counts: Dict[Tuple[int, str], int]) -> None:
    """
    Generates an output file containing counts of tags and
    port/protocol combinations.

    This function writes the provided tag counts and
    port/protocol combination counts to an output file named `output.txt`.
    The output file contains two sections:
    1. **Tag Counts**:
        Lists each tag and its corresponding count.
    2. **Port/Protocol Combination Counts**:
        Lists each port/protocol combination and its corresponding count.

    Args:
        tag_counts (Dict[str, int]):
            A dictionary where keys are tags and values
            are the counts of each tag.
        combination_counts (Dict[Tuple[int, str], int]):
            A dictionary where keys are tuples of (port, protocol) and values
            are the counts of each port/protocol combination.

    Raises:
        Exception: If there is an error writing to the output file.

    Example:
        >>> tag_counts = {'sv_P1': 10, 'sv_P2': 5, 'Untagged': 3}
        >>> combination_counts = {(443, 'tcp'): 10, (68, 'udp'): 5,
             (80, 'tcp'): 3}
        >>> generate_output(tag_counts, combination_counts)
        # This will create an output.txt file with the specified tag
        # and combination counts.
    """
    try:
        with open('output.txt', 'w') as file:
            file.write("Tag Counts:\n\n")
            file.write("Tag\t\tCount\n")
            for tag, count in tag_counts.items():
                file.write(f"{tag}\t\t{count}\n")

            file.write("\nPort/Protocol Combination Counts:\n\n")
            file.write("Port\tProtocol\tCount\n")
            for (port, protocol), count in combination_counts.items():
                file.write(f"{port}\t{protocol}\t{count}\n")
        logging.info("Generated output.txt with tag and combination counts")
    except Exception as e:
        logging.error(f"Error generating output file: {e}")
        sys.exit(1)


def main(flowlog_file: str,
         lookup_file: str,
         protocol_map_filename: str) -> None:
    lookup = load_tag_lookup(lookup_file)
    protocol_map = load_protocol_map(protocol_map_filename)
    tag_counts, combination_counts = parse_flow_logs(flowlog_file,
                                                     lookup,
                                                     protocol_map)
    generate_output(tag_counts, combination_counts)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python -m flowlog.parser <flowlog_file> <lookup_file>")
        sys.exit(1)
    flowlog_file = sys.argv[1]
    lookup_file = sys.argv[2]
    # Construct full path to the protocol_map.json
    script_dir = os.path.dirname(__file__)
    protocol_map_filename = os.path.join(script_dir, "protocol_map.json")
    main(flowlog_file, lookup_file, protocol_map_filename)
