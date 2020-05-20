# ton_cpp_exporter

node_exporter textfile collector for the TON C++ node implementation.

![image](https://user-images.githubusercontent.com/859697/81930178-82585600-95e8-11ea-923f-eae42452c5f4.png) 

## Example queries
    
Is the node or chain stuck?

    rate(ton_masterchainblocktime[5m]) < 0.8
    
Is the node behind?

    ton_unixtime - ton_masterchainblocktime > 60

Did we vote in the current election?

    (ton_election_active_id > bool 0) and on (instance) (ton_election_participated == 0)
    
Is one of our validators in the active set?

    sum by (instance) (ton_validator_is_active) != 1
