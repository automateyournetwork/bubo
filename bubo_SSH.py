import json
import logging
import re
from pyats import aetest
from pyats.log.utils import banner
from genie.utils.diff import Diff
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
        aetest.loop.mark(Test_Cisco_IOS_XE_Intent, device_name=testbed.devices)
        aetest.loop.mark(Test_Interfaces, device_name=testbed.devices)

# ----------------
# Test Case #1
# ----------------
class Test_Cisco_IOS_XE_Intent(aetest.Testcase):
    """Parse all pyATS learn config and learn interfaces data"""

    @aetest.test
    def setup(self, testbed, device_name):
        """ Testcase Setup section """
        # connect to device
        self.device = testbed.devices[device_name]
        # Loop over devices in tested for testing
    
    @aetest.test
    def get_parsed_config(self):
        parsed_config = self.device.learn("config")
        # Get the JSON payload
        self.parsed_json=parsed_config

    @aetest.test
    def create_files(self):
        # Create .JSON file
        with open(f'JSON/{self.device.alias}_Cisco_IOS_XE_Learned_Config_PRE_TEST.json', 'w') as f:
            f.write(json.dumps(self.parsed_json, indent=4, sort_keys=True))
    
    @aetest.test
    def test_ip_domain_name(self):
        # Test for input discards
        self.failed_domain_name={}
        table_data = []
        table_row = []
        if f"ip domain name { self.device.custom.domain_name }" in self.parsed_json:
            table_row.append(self.device.alias)
            table_row.append(self.device.custom.domain_name)
            table_row.append(self.device.custom.domain_name)
            table_row.append('Passed')
        else:
            table_row.append(self.device.alias)
            table_row.append(self.device.custom.domain_name)           
            table_row.append("Different Domain Name Configured")          
            table_row.append('Failed')
            self.failed_domain_name = "Error"
        table_data.append(table_row)
            # display the table
        log.info(tabulate(table_data,
                            headers=['Device', 'Intent Domain Name', 'Configured Domain Name', 'Passed/Failed'],
                            tablefmt='orgtbl'))
        # should we pass or fail?
        if self.failed_domain_name:
            self.failed('Device Has An Incorrect Domain Name')
        else:
            self.passed('Device Has The Correct Domain Name')

    @aetest.test
    def update_domain_name(self):
        if self.failed_domain_name:
            self.pre_change_parsed_json = self.parsed_json
            self.device.configure(f"ip domain name { self.device.custom.domain_name }")
        else:
            self.skipped('No domain name mismatches skipping test')

    @aetest.test
    def get_post_test_yang_data(self):
        if self.failed_domain_name:
            post_parsed_native = self.device.learn("config")
            self.post_parsed_json=post_parsed_native
        else:
            self.skipped('No domain name mismatches skipping test')

    @aetest.test
    def create_post_test_files(self):
        # Create .JSON file
        if self.failed_domain_name:
            with open(f'JSON/{self.device.alias}_Cisco_IOS_XE_Learned_Config_POST_TEST.json', 'w') as f:
                f.write(json.dumps(self.post_parsed_json, indent=4, sort_keys=True))
        else:
            self.skipped('No domain name mismatches skipping test')

    @aetest.test
    def pre_post_diff(self):
        if self.failed_domain_name:       
            pre_change = self.pre_change_parsed_json
            post_change = self.post_parsed_json
            diff = Diff(pre_change, post_change)
            diff.findDiff()
            log.info(diff)
        else:
            self.skipped('No domain name mismatches skipping test')

    @aetest.test
    def retest(self):
        if self.failed_domain_name:
            self.get_parsed_config()
            self.test_ip_domain_name()
        else:
            self.skipped('No domain name mismatches skipping test')

    @aetest.test
    def get_parsed_interfaces(self):
        self.parsed_interface = self.device.learn("interface")

    @aetest.test
    def test_configured_interfaces_in_intent(self):
        # Test for input discards
        self.failed_intent_interfaces={}
        table_data = []
        for actual_interface in self.parsed_interface.info:
            table_row = []
            configured_interface = f"{ actual_interface }"
            if configured_interface in self.device.interfaces:
                table_row.append(self.device.alias)
                table_row.append(configured_interface)
                table_row.append('Passed')
            else:
                table_row.append(self.device.alias)            
                table_row.append(configured_interface)          
                table_row.append('Failed')
                self.failed_intent_interfaces = configured_interface
            table_data.append(table_row)                
            # display the table
        
        log.info(tabulate(table_data,
                        headers=['Device', 'Configured Interface in Intent', 'Passed/Failed'],
                        tablefmt='orgtbl'))
        # should we pass or fail?
        if self.failed_intent_interfaces:
            self.failed('Device Has Configured Interface NOT in Intent YAML Model')
        else:
            self.passed('Device Has All Configured Interfaces in Intent YAML Model')

    @aetest.test
    def test_intended_interfaces_in_config(self):
        # Test for input discards
        self.failed_intent_interfaces={}
        table_data = []
        configured_interface_list = []
        for actual_interface in self.parsed_interface.info:
            configured_interface_list.append(f"{ actual_interface }")
        self.missing_interfaces = []
        for intended_interface in self.device.interfaces:
            table_row = []
            if intended_interface in configured_interface_list:
                table_row.append(self.device.alias)
                table_row.append(intended_interface)
                table_row.append('Passed')
            else:
                table_row.append(self.device.alias)            
                table_row.append(intended_interface)          
                table_row.append('Failed')
                self.failed_intent_interfaces = intended_interface
                self.missing_interfaces.append(intended_interface)
            table_data.append(table_row)                
            # display the table
        
        log.info(tabulate(table_data,
                        headers=['Device', 'Intended Interface in Configuration', 'Passed/Failed'],
                        tablefmt='orgtbl'))
        # should we pass or fail?
        if self.failed_intent_interfaces:
            self.failed('Device Has Intended Interfaces in YAML Intent NOT in Configuration')
        else:
            self.passed('Device Has All Intended Interfaces in Intent YAML Model Configured')

    @aetest.test
    def update_configured_interfaces_from_intent(self):
        if self.failed_intent_interfaces:
            self.pre_change_parsed_json = self.parsed_interface.info
            for interface in self.missing_interfaces:
                self.device.configure(f"interface { interface }")
        else:
            self.skipped('Device Has All Intended Interfaces in Intent YAML Model Configured')

    @aetest.test
    def get_post_test_data(self):
        if self.failed_intent_interfaces:
            self.post_parsed_json = self.device.learn("interface")
        else:
            self.skipped('Device Has All Intended Interfaces in Intent YAML Model Configured')

    @aetest.test
    def create_post_test_files(self):
        # Create .JSON file
        if self.failed_intent_interfaces:
            with open(f'JSON/{self.device.alias}_Cisco_IOS_XE_Learned_Config_POST_TEST.json', 'w') as f:
                f.write(json.dumps(self.post_parsed_json.info, indent=4, sort_keys=True))
        else:
            self.skipped('Device Has All Intended Interfaces in Intent YAML Model Configured')

    @aetest.test
    def pre_post_diff(self):
        if self.failed_intent_interfaces:           
            pre_change = self.pre_change_parsed_json
            post_change = self.post_parsed_json.info
            diff = Diff(pre_change, post_change)
            diff.findDiff()
            log.info(diff)
        else:
            self.skipped('Device Has All Intended Interfaces in Intent YAML Model Configured')

    @aetest.test
    def retest(self):
        if self.failed_intent_interfaces:
            self.get_parsed_interfaces()
            self.test_intended_interfaces_in_config()
        else:
            self.skipped('Device Has All Intended Interfaces in Intent YAML Model Configured')

# ----------------
# Test Case #2
# ----------------
class Test_Interfaces(aetest.Testcase):
    """Parse the pyATS Learn Interface Data"""

    @aetest.test
    def setup(self, testbed, device_name):
        """ Testcase Setup section """
        # connect to device
        self.device = testbed.devices[device_name]
        # Loop over devices in tested for testing
    
    @aetest.test
    def get_pre_test_interface_data(self):
        self.parsed_interfaces = self.device.learn("interface")

    @aetest.test
    def create_pre_test_files(self):
        # Create .JSON file
        with open(f'JSON/{self.device.alias}_pyATS_Learn_Interface_PRE_TEST.json', 'w') as f:
            f.write(json.dumps(self.parsed_interfaces.info, indent=4, sort_keys=True))
    
    @aetest.test
    def test_interface_input_errors(self):
        # Test for input discards
        in_errors_threshold = 0
        self.failed_interfaces = {}
        table_data = []
        for intf,value in self.parsed_interfaces.info.items():
            if 'counters' in value:
                counter = value['counters']['in_errors']
                table_row = []
                table_row.append(self.device.alias)
                table_row.append(intf)
                table_row.append(counter)
                if int(counter) > in_errors_threshold:
                    table_row.append('Failed')
                    self.failed_interfaces[intf] = int(counter)
                    self.interface_name = intf
                    self.error_counter = self.failed_interfaces[intf]
                else:
                    table_row.append('Passed')
                table_data.append(table_row)
        
        # display the table
        log.info(tabulate(table_data,
            headers=['Device', 'Interface',
                    'Input Errors Counter',
                    'Passed/Failed'],
                    tablefmt='orgtbl'))

        # should we pass or fail?
        if self.failed_interfaces:
            self.failed('Some interfaces have input errors')
        else:
            self.passed('No interfaces have input errors')

    @aetest.test
    def test_interface_input_crc_errors(self):
        # Test for input crc discards
        in_errors_threshold = 0
        self.failed_interfaces = {}
        table_data = []
        for intf,value in self.parsed_interfaces.info.items():
            if 'counters' in value:
                counter = value['counters']['in_crc_errors']
                table_row = []
                table_row.append(self.device.alias)
                table_row.append(intf)
                table_row.append(counter)
                if int(counter) > in_errors_threshold:
                    table_row.append('Failed')
                    self.failed_interfaces[intf] = int(counter)
                    self.interface_name = intf
                    self.error_counter = self.failed_interfaces[intf]
                else:
                    table_row.append('Passed')
                table_data.append(table_row)
            # display the table
        log.info(tabulate(table_data,
                            headers=['Device', 'Interface',
                                    'Input CRC Errors Counter',
                                    'Passed/Failed'],
                            tablefmt='orgtbl'))
        # should we pass or fail?
        if self.failed_interfaces:
            self.failed('Some interfaces have input CRC errors')
        else:
            self.passed('No interfaces have input CRC errors')

    @aetest.test
    def test_interface_output_errors(self):
        # Test for input crc discards
        in_errors_threshold = 0
        self.failed_interfaces = {}
        table_data = []
        for intf,value in self.parsed_interfaces.info.items():
            if 'counters' in value:
                counter = value['counters']['out_errors']
                table_row = []
                table_row.append(self.device.alias)
                table_row.append(intf)
                table_row.append(counter)
                if int(counter) > in_errors_threshold:
                    table_row.append('Failed')
                    self.failed_interfaces[intf] = int(counter)
                    self.interface_name = intf
                    self.error_counter = self.failed_interfaces[intf]
                else:
                    table_row.append('Passed')
                table_data.append(table_row)
            # display the table
        log.info(tabulate(table_data,
                            headers=['Device', 'Interface',
                                    'Output Errors Counter',
                                    'Passed/Failed'],
                            tablefmt='orgtbl'))
        # should we pass or fail?
        if self.failed_interfaces:
            self.failed('Some interfaces have input CRC errors')
        else:
            self.passed('No interfaces have input CRC errors')

    @aetest.test
    def test_interface_full_duplex(self):
        # Test for Full Duplex
        duplex_threshold = "FULL"
        self.failed_interfaces = {}
        table_data = []
        for intf,value in self.parsed_interfaces.info.items():
            if 'duplex_mode' in value:
                counter = value['duplex_mode']
                table_row = []
                table_row.append(self.device.alias)
                table_row.append(intf)
                table_row.append(counter)
                if counter != duplex_threshold:
                    table_row.append('Failed')
                    self.failed_interfaces[intf] = counter
                    self.interface_name = intf
                    self.error_counter = self.failed_interfaces[intf]
                else:
                    table_row.append('Passed')
                table_data.append(table_row)
                # display the table
        log.info(tabulate(table_data,
                            headers=['Device', 'Interface',
                                    'Duplex Mode',
                                    'Passed/Failed'],
                            tablefmt='orgtbl'))
        # should we pass or fail?
        if self.failed_interfaces:
            self.failed('Some interfaces are half duplex')
        else:
            self.passed('All interfaces are full duplex')

    @aetest.test
    def test_interface_oper_status(self):
        # Test for Operational Status
        duplex_threshold = "up"
        self.failed_interfaces = {}
        table_data = []
        for intf,value in self.parsed_interfaces.info.items():
            if 'oper_status' in value:
                counter = value['oper_status']
                table_row = []
                table_row.append(self.device.alias)
                table_row.append(intf)
                table_row.append(counter)
                if counter != duplex_threshold:
                    table_row.append('Failed')
                    self.failed_interfaces[intf] = counter
                    self.interface_name = intf
                    self.error_counter = self.failed_interfaces[intf]
                else:
                    table_row.append('Passed')
                table_data.append(table_row)
                # display the table
        log.info(tabulate(table_data,
                            headers=['Device', 'Interface',
                                    'Operational Status',
                                    'Passed/Failed'],
                            tablefmt='orgtbl'))
        # should we pass or fail?
        if self.failed_interfaces:
            self.failed('Some interfaces are operationally down')
        else:
            self.passed('All interfaces are operationally up')

    @aetest.test
    def test_interface_description_matches_intent(self):
        # Test for input discards
        self.failed_interfaces = {}
        table_data = []
        for self.intf,value in self.parsed_interfaces.info.items():
            if 'description' in value:
                for interface,intent_value in self.device.interfaces.items():
                    if self.intf == interface:
                        self.intended_desc = intent_value['description']
                        actual_desc = value['description']
                        table_row = []
                        table_row.append(self.device.alias)
                        table_row.append(self.intf)
                        table_row.append(self.intended_desc)
                        table_row.append(actual_desc)
                        if actual_desc != self.intended_desc:
                            table_row.append('Failed')
                            self.failed_interfaces[self.intf] = self.intended_desc
                            self.interface_name = self.intf
                            self.error_counter = self.failed_interfaces[self.intf]
                        else:
                            table_row.append('Passed')
                        table_data.append(table_row)
            else:
                for interface,intent_value in self.device.interfaces.items():
                    if self.intf == interface:
                        self.intended_desc = intent_value['description']
                        actual_desc = ""
                        table_row = []
                        table_row.append(self.device.alias)
                        table_row.append(self.intf)
                        table_row.append(self.intended_desc)
                        table_row.append(actual_desc)
                        if actual_desc != self.intended_desc:
                            table_row.append('Failed')
                            self.failed_interfaces[self.intf] = self.intended_desc
                            self.interface_name = self.intf
                            self.error_counter = self.failed_interfaces[self.intf]
                            self.update_interface_description()
                        table_data.append(table_row)                            
        # display the table
        log.info(tabulate(table_data,
                            headers=['Device', 'Interface',
                                    'Intent Desc',
                                    'Actual Desc',
                                    'Passed/Failed'],
                            tablefmt='orgtbl'))

        # should we pass or fail?
        if self.failed_interfaces:
            self.failed('Some interfaces intent / actual descriptions mismatch')            
        else:
            self.passed('All interfaces intent / actual descriptions match')

    def update_interface_description(self):
        if self.failed_interfaces:
            self.device.configure(f'''interface { self.intf }
                                      description { self.intended_desc } 
                                    ''')
        else:
            self.skipped('No description mismatches skipping test')

    @aetest.test
    def get_post_test_interface_data(self):
        if self.failed_interfaces:
            self.pre_change_parsed_json = self.parsed_interfaces
            self.post_parsed_interfaces = self.device.learn("interface")
        else:
            self.pre_change_parsed_json = self.parsed_interfaces
            self.skipped('No description mismatches skipping test')

    @aetest.test
    def create_post_test_files(self):
        # Create .JSON file
        if self.failed_interfaces:
            with open(f'JSON/{self.device.alias}_Learn_Interfaces_POST_TEST.json', 'w') as f:
                f.write(json.dumps(self.post_parsed_interfaces.info, indent=4, sort_keys=True))
        else:
            self.skipped('No description mismatches skipping test')

    @aetest.test
    def pre_post_diff(self):
        if self.failed_interfaces:
            for intf,pre_value in self.pre_change_parsed_json.info.items():
                    for interface,post_value in self.post_parsed_interfaces.info.items():
                        if intf == interface:
                            diff = Diff(pre_value, post_value)
                            diff.findDiff()
                            log.info(diff)
        else:
            self.skipped('No description mismatches skipping test')

    @aetest.test
    def retest(self):
        if self.failed_interfaces:
            self.get_pre_test_interface_data()
            self.test_interface_description_matches_intent()
        else:
            self.skipped('No description mismatches skipping test')

class CommonCleanup(aetest.CommonCleanup):
    @aetest.subsection
    def disconnect_from_devices(self, testbed):
        testbed.disconnect()

# for running as its own executable
if __name__ == '__main__':
    aetest.main()