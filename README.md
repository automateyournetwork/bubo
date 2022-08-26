# pyATS_REST_Connector_Example
Example using the pyATS REST Connector with IOS-XE / NXOS OpenConfig YANG Model 

## Ready to go with the Cisco DevNet Sandbox - CML Enterprise and the Always on IOS-XE platform
https://devnetsandbox.cisco.com/RM/Diagram/Index/bdb14197-43e0-4d1d-9c2b-216aeaae6241?diagramType=Topology
https://devnetsandbox.cisco.com/RM/Diagram/Index/7b4d4209-a17c-4bc3-9b38-f15184e53a94?diagramType=Topology

### Enable RESTCONF
On the CML IOS-XE Devices make sure to enable RESTCONF

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
(REST_Connector) $ git clone https://github.com/automateyournetwork/pyATS_REST_Connector_Example/
(REST_Connector) $ cd pyATS_REST_Connector_Example
```

### Install the required packages
```console
(REST_Connector) ~/pyATS_REST_Connector_Example$ pip install pyats[full]
(REST_Connector) ~/pyATS_REST_Connector_Example$ pip install tabulate
(REST_Connector) ~/pyATS_REST_Connector_Example$ pip install rest.connector
```

## Run the code
```console
(REST_Connector) ~/pyATS_REST_Connector_Example$
(REST_Connector) ~/pyATS_REST_Connector_Example$ pyats run job rest_connector_job.py
```