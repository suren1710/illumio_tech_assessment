# Flow Log Parser

This project parses flow log data and maps each row to a tag based on a lookup table.

## Assumptions

- The input flow log file is generated using Flow log record examples provided by aws "Accepted and rejected traffic" . Reference link  https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs-records-examples.html#flow-log-example-traffic-path
- Lookup table file generated using format provided by the assesment question.
- Assuming destination ports are found in column 7 and protocol in column 8 in the input flow log file. (The data is delimited by space)
- As the log file has protocol identifier instead of the protocol name, I have added protocol map json file. protcol-identifier taken from https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml

## Testing
- Unit testing is done with code coverage of 90%
- Performance benchmark test completed.
- Tested with flowlog_data.txt size 10 MB and Lookup table with 10000 mapping entries.


## How to Run

1. Creating\Setting virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate

2. Install the dependencies:
   ```sh
   make install

3. Run lint:
   ```sh
   make lint

4. Run type hints:
   ```sh
   make type

5. Run all tests:
   ```sh
   make test

6. Run performance benchmark:
   ```sh
   make perf

   Current benchmark:
   benchmark: 4.0.0 (defaults: timer=time.perf_counter disable_gc=False min_rounds=5 min_time=0.000005 max_time=1.0 calibration_precision=10 warmup=False warmup_iterations=100000)

6. To run the parser:
   ```sh
   PYTHONPATH=./src python -m flowlog.parser flowlog_data.txt tag_lookup.csv
   
   NOTE: you can replace your flow log data and lookup. It will generate output file with tag and combination counts.
   You dont need to install any dependencies to run the above command. This project can be run with just active virtual environment. 
   Dependencies are only for test, lint and type hint checks.


## Code coverage report
Code coverage report is uploaded under code_cov_report directory.


