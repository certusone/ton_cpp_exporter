# ton_cpp_exporter

node_exporter textfile collector for the TON C++ node implementation.

## Example queries

Check whether new key has been generated during election:

    ton_validator_election_date{index="0"} < on (instance) group_left ton_election_active_id
    
Check if node or chain are stuck:

    rate(ton_masterchainblocktime[5m]) < 0.8
    
Check if node is behind:

    ton_unixtime - ton_masterchainblocktime > 60
