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
    Loads the tag from lookup CSV.
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
    with open(filename, 'r') as f:
        return json.load(f)


def parse_flow_logs(
        filename: str,
        lookup: Dict[Tuple[int, str], str],
        protocol_map: dict) -> Tuple[Dict[str, int],
                                     Dict[Tuple[int, str], int]]:
    """
    Parses the flow log from the data file.
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
