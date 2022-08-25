import json
import logging
from pyats import aetest
from pyats.log.utils import banner
from tabulate import tabulate

# ----------------
# Get logger for script
# ----------------

log = logging.getLogger(__name__)

# ----------------
# AE Test Setup
# ----------------
class common_setup(aetest.CommonSetup):
    """Common Setup section"""
# ----------------
# Connected to devices
# ----------------
    @aetest.subsection
    def connect_to_devices(self, testbed):
        """Connect to all the devices"""
        testbed.connect()
# ----------------
# Mark the loop for Input Discards
# ----------------
    @aetest.subsection
    def loop_mark(self, testbed):
        aetest.loop.mark(Test_Input_Discards, device_name=testbed.devices)

# ----------------
# Test Case #1
# ----------------
class Test_Input_Discards(aetest.Testcase):
    """Parse all the commands"""

    @aetest.test
    def setup(self, testbed, device_name):
        """ Testcase Setup section """
        # connect to device
        self.device = testbed.devices[device_name]
        # Loop over devices in tested for testing
        aetest.loop.mark(
            self.get_yang_data(),
            self.create_files(),
            self.test_interface_input_discards(),
        )
    
    @aetest.test
    def get_yang_data(self):
        # Use the RESTCONF OpenConfig YANG Model 
        parsed_openconfig_interfaces = self.device.rest.get("/restconf/data/openconfig-interfaces:interfaces")
        # Get the JSON payload
        self.parsed_json=parsed_openconfig_interfaces.json()

    @aetest.test
    def create_files(self):
        # Create .JSON file
        with open(f'{self.device.alias}_OpenConfig_Interfaces.json', 'w') as f:
            f.write(json.dumps(self.parsed_json, indent=4, sort_keys=True))

    def test_interface_input_discards(self):
        # Test for input discards
        in_discards_threshold = 0
        self.failed_interfaces = {}
        table_data = []
        for intf in self.parsed_json['openconfig-interfaces:interfaces']['interface']:
            counter = intf['state']['counters']['in-discards']
            if counter:
                table_row = []
                table_row.append(self.device.alias)
                table_row.append(intf['name'])
                table_row.append(counter)
                if int(counter) > in_discards_threshold:
                    table_row.append('Failed')
                    self.failed_interfaces[intf['name']] = int(counter)
                    self.interface_name = intf['name']
                    self.error_counter = self.failed_interfaces[intf['name']]
                else:
                    table_row.append('Passed')
            else:
                table_row.append(self.device.alias)
                table_row.append(intf)
                table_row.append('N/A')
                table_row.append('N/A')
            table_data.append(table_row)
            # display the table
        log.info(tabulate(table_data,
                            headers=['Device', 'Interface',
                                    'Input Discard Counter',
                                    'Passed/Failed'],
                            tablefmt='orgtbl'))
        # should we pass or fail?
        if self.failed_interfaces:
            aetest.loop.mark(self.interface_babbles_check,
                                name = self.failed_interfaces.keys())
            self.failed('Some interfaces have input discards')
        else:
            self.passed('No interfaces have input discards')