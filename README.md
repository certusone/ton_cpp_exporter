# ton_cpp_exporter

node_exporter textfile collector for the TON C++ node implementation.

![image](https://user-images.githubusercontent.com/859697/81930178-82585600-95e8-11ea-923f-eae42452c5f4.png)

## Example queries
    
Check if node or chain are stuck:

    rate(ton_masterchainblocktime[5m]) < 0.8
    
Check if node is behind:

    ton_unixtime - ton_masterchainblocktime > 60
