[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/automateyournetwork/bubo)
# bubo
Example using the both the pyATS SSH CLI parsers and pyATS REST Connector with IOS-XE / NXOS OpenConfig YANG Model for test-driven development

## Ready to go with the Cisco DevNet Sandbox Always on IOS-XE platform

https://devnetsandbox.cisco.com/RM/Diagram/Index/7b4d4209-a17c-4bc3-9b38-f15184e53a94?diagramType=Topology

### Enable RESTCONF
Make sure to enable RESTCONF

```console
switch> enable
switch# conf t
switch(conf)# ip http secure-server
switch(conf)# restconf
```
## Installation

### Create a virtual environment
```console
$ python3 -m venv REST_Connector
$ source /REST_Connector/bin/activate
(REST_Connector) $
```

### Clone the repository 
```console
(REST_Connector) $ git clone https://github.com/automateyournetwork/bubo/
(REST_Connector) $ cd bubo
```

### Install the required packages
```console
(REST_Connector) ~/bubo$ pip install pyats[full]
(REST_Connector) ~/bubo$ pip install tabulate
(REST_Connector) ~/bubo$ pip install rest.connector
```

## Run the code - using RESTCONF
```console
(REST_Connector) ~/bubo$
(REST_Connector) ~/bubo$ pyats run job bubo_REST.py
```
## Run the code - using SSH
```console
(REST_Connector) ~/bubo$
(REST_Connector) ~/bubo$ pyats run job bubo_SSH.py
```