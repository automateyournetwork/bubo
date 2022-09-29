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
        aetest.loop.mark(Test_Cisco_IOS_XE_Native, device_name=testbed.devices)
        aetest.loop.mark(Test_Interfaces, device_name=testbed.devices)

# ----------------
# Test Case #1
# ----------------
class Test_Cisco_IOS_XE_Native(aetest.Testcase):
    """Parse all the commands"""

    @aetest.test
    def setup(self, testbed, device_name):
        """ Testcase Setup section """
        # connect to device
        self.device = testbed.devices[device_name]
        # Loop over devices in tested for testing
    
    @aetest.test
    def get_yang_data(self):
        # Use the RESTCONF OpenConfig YANG Model 
        parsed_native = self.device.rest.get("/restconf/data/Cisco-IOS-XE-native:native")
        # Get the JSON payload
        self.parsed_json=parsed_native.json()

    @aetest.test
    def create_files(self):
        # Create .JSON file
        with open(f'JSON/{self.device.alias}_Cisco_IOS_XE_Native_PRE_TEST.json', 'w') as f:
            f.write(json.dumps(self.parsed_json, indent=4, sort_keys=True))
    
    @aetest.test
    def test_motd(self):
        # Test for motd banner against intent
        self.failed_banner={}
        table_data = []
        table_row = []
        if 'banner' in self.parsed_json['Cisco-IOS-XE-native:native']:
            if 'motd' in self.parsed_json['Cisco-IOS-XE-native:native']['banner']:
                if self.parsed_json['Cisco-IOS-XE-native:native']['banner']['motd']['banner'] == self.device.custom.motd:
                    table_row.append(self.device.alias)
                    table_row.append("Has Correct Banner")
                    table_row.append('Passed')
                else:
                    table_row.append(self.device.alias)            
                    table_row.append("Has Incorrect Banner")          
                    table_row.append('Failed')
                    self.failed_banner = "Incorrect Banner"
            else:
                table_row.append(self.device.alias)            
                table_row.append("No MOTD Banner")          
                table_row.append('Failed')
                self.failed_banner = "No MOTD Banner"
        else:
            table_row.append(self.device.alias)            
            table_row.append("No MOTD Banner")          
            table_row.append('Failed')
            self.failed_banner = "No Banners"
        table_data.append(table_row)
            # display the table
        log.info(tabulate(table_data,
                            headers=['Device', 'Has Banner', 'Passed/Failed'],
                            tablefmt='orgtbl'))
        # should we pass or fail?
        if self.failed_banner:
            self.failed('Device Does Not Have A MOTD Banner')
        else:
            self.passed('Device Has Correct MOTD Banner')

    @aetest.test
    def update_motd_banner(self):
        if self.failed_banner:
            self.pre_change_parsed_json = self.parsed_json
            payload = json.dumps({
                                    "Cisco-IOS-XE-native:banner": f"{ self.device.custom.motd }"
                                })
            update_motd_banner = self.device.rest.put("/restconf/data/Cisco-IOS-XE-native:native/banner/motd/banner", payload=payload)
            log.info(f"The PUT to update the motd banner status code was { update_motd_banner }")
            log.info("Re-testing motd")        
        else:
            self.skipped('No motd mismatches skipping test')

    @aetest.test
    def get_post_test_yang_data(self):
        if self.failed_banner:
            # Use the RESTCONF OpenConfig YANG Model 
            post_parsed_native = self.device.rest.get("/restconf/data/Cisco-IOS-XE-native:native")
            # Get the JSON payload
            self.post_parsed_json=post_parsed_native.json()
        else:
            self.skipped('No motd mismatches skipping test')

    @aetest.test
    def create_post_test_files(self):
        # Create .JSON file
        if self.failed_banner:
            with open(f'JSON/{self.device.alias}_Cisco_IOS_XE_Native_POST_TEST.json', 'w') as f:
                f.write(json.dumps(self.post_parsed_json, indent=4, sort_keys=True))
        else:
            self.skipped('No motd mismatches skipping test')

    @aetest.test
    def pre_post_diff(self):
        if self.failed_banner:
            if 'banner' in self.parsed_json['Cisco-IOS-XE-native:native']:
                if 'motd' in self.parsed_json['Cisco-IOS-XE-native:native']['banner']:            
                    pre_change = self.pre_change_parsed_json['Cisco-IOS-XE-native:native']['banner']['motd']
                else: 
                    pre_change = {
                        "Cisco-IOS-XE-native:motd": {
                            "banner": ""
                        }
                    }
            else:
                pre_change = {
                                "Cisco-IOS-XE-native:motd": {
                                 "banner": ""
                            }
                        }
            post_change = self.post_parsed_json['Cisco-IOS-XE-native:native']['banner']['motd']
            diff = Diff(pre_change, post_change)
            diff.findDiff()
            log.info(diff)
        else:
            self.skipped('No MOTD mismatches skipping test')

    @aetest.test
    def retest(self):
        if self.failed_banner:
            self.get_yang_data()
            self.test_motd()
        else:
            self.skipped('No MOTD mismatches skipping test')

    @aetest.test
    def test_ip_domain_name(self):
        # Test for input discards
        self.failed_domain_name={}
        table_data = []
        table_row = []
        if 'ip' in self.parsed_json['Cisco-IOS-XE-native:native']:
            if 'domain' in self.parsed_json['Cisco-IOS-XE-native:native']['ip']:
                if 'name' in self.parsed_json['Cisco-IOS-XE-native:native']['ip']['domain']:
                    if self.parsed_json['Cisco-IOS-XE-native:native']['ip']['domain']['name'] == self.device.custom.domain_name:
                        table_row.append(self.device.alias)
                        table_row.append(self.device.custom.domain_name)
                        table_row.append(self.parsed_json['Cisco-IOS-XE-native:native']['ip']['domain']['name'])
                        table_row.append('Passed')
                    else:
                        table_row.append(self.device.alias)
                        table_row.append(self.device.custom.domain_name)           
                        table_row.append(self.parsed_json['Cisco-IOS-XE-native:native']['ip']['domain']['name'])          
                        table_row.append('Failed')
                        self.failed_domain_name = self.parsed_json['Cisco-IOS-XE-native:native']['ip']['domain']['name']
                else:
                    table_row.append(self.device.alias)
                    table_row.append(self.device.custom.domain_name)
                    table_row.append("No Domain Name Configured")
                    table_row.append('Failed')
                    self.failed_domain_name = "No Domain Name"
            else:
                table_row.append(self.device.alias)
                table_row.append(self.device.custom.domain_name)
                table_row.append("No Domain Name Configured")
                table_row.append('Failed')
                self.failed_domain_name = "No Domain Name"
        else:
            table_row.append(self.device.alias)
            table_row.append(self.device.custom.domain_name)
            table_row.append("No Domain Name Configured")
            table_row.append('Failed')
            self.failed_domain_name = "No Domain Name"

        table_data.append(table_row)
            # display the table
        log.info(tabulate(table_data,
                            headers=['Device', 'Intent Domain Name', 'Configured Domain Name', 'Passed/Failed'],
                            tablefmt='orgtbl'))
        # should we pass or fail?
        if self.failed_domain_name:
            self.failed('Device Does Not Have A Domain Name')
        else:
            self.passed('Device Has The Correct Domain Name')

    @aetest.test
    def update_domain_name(self):
        if self.failed_domain_name:
            self.pre_change_parsed_json = self.parsed_json
            payload = json.dumps({
                                    "Cisco-IOS-XE-native:name": f"{self.device.custom.domain_name}"
                                })
            update_domain_name = self.device.rest.put("/restconf/data/Cisco-IOS-XE-native:native/ip/domain/name", payload=payload)
            log.info(f"The PUT to update the domain name status code was { update_domain_name }")
            log.info("Re-testing domain name")        
        else:
            self.skipped('No domain name mismatches skipping test')

    @aetest.test
    def get_post_test_yang_data(self):
        if self.failed_domain_name:
            # Use the RESTCONF OpenConfig YANG Model 
            post_parsed_native = self.device.rest.get("/restconf/data/Cisco-IOS-XE-native:native")
            # Get the JSON payload
            self.post_parsed_json=post_parsed_native.json()
        else:
            self.skipped('No domain name mismatches skipping test')

    @aetest.test
    def create_post_test_files(self):
        # Create .JSON file
        if self.failed_domain_name:
            with open(f'JSON/{self.device.alias}_Cisco_IOS_XE_Native_POST_TEST.json', 'w') as f:
                f.write(json.dumps(self.post_parsed_json, indent=4, sort_keys=True))
        else:
            self.skipped('No domain name mismatches skipping test')

    @aetest.test
    def pre_post_diff(self):
        if self.failed_domain_name:
            if 'ip' in self.parsed_json['Cisco-IOS-XE-native:native']:
                if 'domain' in self.parsed_json['Cisco-IOS-XE-native:native']['ip']:
                    if 'name' in self.parsed_json['Cisco-IOS-XE-native:native']['ip']['domain']:           
                        pre_change = self.pre_change_parsed_json['Cisco-IOS-XE-native:native']['ip']['domain']
                    else: 
                        pre_change = {
                                "Cisco-IOS-XE-native:domain": {
                                "name": ""
                                }
                            }
                else:
                    pre_change = {
                            "Cisco-IOS-XE-native:domain": {
                            "name": ""
                            }
                        }
            else:
                pre_change = {
                        "Cisco-IOS-XE-native:domain": {
                        "name": ""
                        }
                    }
            post_change = self.post_parsed_json['Cisco-IOS-XE-native:native']['ip']['domain']
            diff = Diff(pre_change, post_change)
            diff.findDiff()
            log.info(diff)
        else:
            self.skipped('No domain name mismatches skipping test')

    @aetest.test
    def retest(self):
        if self.failed_domain_name:
            self.get_yang_data()
            self.test_ip_domain_name()
        else:
            self.skipped('No domain name mismatches skipping test')

    @aetest.test
    def test_configured_interfaces_in_intent(self):
        # Test for input discards
        self.failed_intent_interfaces={}
        table_data = []
        for actual_interface,actual_value in self.parsed_json['Cisco-IOS-XE-native:native']['interface'].items():
            for actual_key in actual_value:
                table_row = []
                configured_interface = f"{ actual_interface }{ actual_key['name'] }"
                if configured_interface in self.device.custom.interfaces:
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
        for actual_interface,actual_value in self.parsed_json['Cisco-IOS-XE-native:native']['interface'].items():
            for actual_key in actual_value:
                configured_interface_list.append(f"{ actual_interface }{ actual_key['name'] }")
        self.missing_interfaces = []
        for intended_interface in self.device.custom.interfaces:
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
            self.pre_change_parsed_json = self.parsed_json
            for interface in self.missing_interfaces:
                interface_type = re.search(r"[a-zA-Z]*", f"{ interface }").group()
                interface_number = re.search('\d+|$', f'{ interface }').group()
                payload = json.dumps({
                                "Cisco-IOS-XE-native:interface": {
                                f"{ interface_type }": [
                                {
                                    "name": f"{ interface_number }"
                                }
                                        ]
                                }
                            }
                            )
                create_interface = self.device.rest.patch("/restconf/data/Cisco-IOS-XE-native:native/interface", payload=payload)
                log.info(f"The PATCH to create the missing intended interface status code was { create_interface }")
                log.info("Re-testing motd")        
        else:
            self.skipped('Device Has All Intended Interfaces in Intent YAML Model Configured')

    @aetest.test
    def get_post_test_yang_data(self):
        if self.failed_intent_interfaces:
            # Use the RESTCONF OpenConfig YANG Model 
            post_parsed_native = self.device.rest.get("/restconf/data/Cisco-IOS-XE-native:native")
            # Get the JSON payload
            self.post_parsed_json=post_parsed_native.json()
        else:
            self.skipped('Device Has All Intended Interfaces in Intent YAML Model Configured')

    @aetest.test
    def create_post_test_files(self):
        # Create .JSON file
        if self.failed_intent_interfaces:
            with open(f'JSON/{self.device.alias}_Cisco_IOS_XE_Native_POST_TEST.json', 'w') as f:
                f.write(json.dumps(self.post_parsed_json, indent=4, sort_keys=True))
        else:
            self.skipped('Device Has All Intended Interfaces in Intent YAML Model Configured')

    @aetest.test
    def pre_post_diff(self):
        if self.failed_intent_interfaces:           
            pre_change = self.pre_change_parsed_json['Cisco-IOS-XE-native:native']['interface']
            post_change = self.post_parsed_json['Cisco-IOS-XE-native:native']['interface']
            diff = Diff(pre_change, post_change)
            diff.findDiff()
            log.info(diff)
        else:
            self.skipped('Device Has All Intended Interfaces in Intent YAML Model Configured')

    @aetest.test
    def retest(self):
        if self.failed_intent_interfaces:
            self.get_yang_data()
            self.test_intended_interfaces_in_config()
        else:
            self.skipped('Device Has All Intended Interfaces in Intent YAML Model Configured')

# ----------------
# Test Case #2
# ----------------
class Test_Interfaces(aetest.Testcase):
    """Parse the OpenConfig YANG Model - interfaces:interfaces"""

    @aetest.test
    def setup(self, testbed, device_name):
        """ Testcase Setup section """
        # connect to device
        self.device = testbed.devices[device_name]
        # Loop over devices in tested for testing
    
    @aetest.test
    def get_pre_test_yang_data(self):
        # Use the RESTCONF OpenConfig YANG Model 
        parsed_openconfig_interfaces = self.device.rest.get("/restconf/data/openconfig-interfaces:interfaces")
        # Get the JSON payload
        self.parsed_json=parsed_openconfig_interfaces.json()

    @aetest.test
    def create_pre_test_files(self):
        # Create .JSON file
        with open(f'JSON/{self.device.alias}_OpenConfig_Interfaces_PRE_TEST.json', 'w') as f:
            f.write(json.dumps(self.parsed_json, indent=4, sort_keys=True))
    
    @aetest.test
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
            self.failed('Some interfaces have input discards')
        else:
            self.passed('No interfaces have input discards')

    @aetest.test
    def test_interface_input_errors(self):
        # Test for input discards
        in_errors_threshold = 0
        self.failed_interfaces = {}
        table_data = []
        for intf in self.parsed_json['openconfig-interfaces:interfaces']['interface']:
            counter = intf['state']['counters']['in-errors']
            if counter:
                table_row = []
                table_row.append(self.device.alias)
                table_row.append(intf['name'])
                table_row.append(counter)
                if int(counter) > in_errors_threshold:
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
                                    'Input Errors Counter',
                                    'Passed/Failed'],
                            tablefmt='orgtbl'))
        # should we pass or fail?
        if self.failed_interfaces:
            self.failed('Some interfaces have input errors')
        else:
            self.passed('No interfaces have input errors')

    @aetest.test
    def test_interface_input_fcs_errors(self):
        # Test for input discards
        in_fcs_errors_threshold = 0
        self.failed_interfaces = {}
        table_data = []
        for intf in self.parsed_json['openconfig-interfaces:interfaces']['interface']:
            counter = intf['state']['counters']['in-fcs-errors']
            if counter:
                table_row = []
                table_row.append(self.device.alias)
                table_row.append(intf['name'])
                table_row.append(counter)
                if int(counter) > in_fcs_errors_threshold:
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
                                    'Input FCS Errors Counter',
                                    'Passed/Failed'],
                            tablefmt='orgtbl'))
        # should we pass or fail?
        if self.failed_interfaces:
            self.failed('Some interfaces have input fcs errors')
        else:
            self.passed('No interfaces have input fcs errors')

    @aetest.test
    def test_interface_input_unknown_protocols(self):
        # Test for input discards
        in_unknown_protocols_threshold = 0
        self.failed_interfaces = {}
        table_data = []
        for intf in self.parsed_json['openconfig-interfaces:interfaces']['interface']:
            counter = intf['state']['counters']['in-unknown-protos']
            if counter:
                table_row = []
                table_row.append(self.device.alias)
                table_row.append(intf['name'])
                table_row.append(counter)
                if int(counter) > in_unknown_protocols_threshold:
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
                                    'Input Unknown Protocols Counter',
                                    'Passed/Failed'],
                            tablefmt='orgtbl'))
        # should we pass or fail?
        if self.failed_interfaces:
            self.failed('Some interfaces have input unknown protocols')
        else:
            self.passed('No interfaces have input unknwon protocols')

    @aetest.test
    def test_interface_output_discards(self):
        # Test for input discards
        out_discards_threshold = 0
        self.failed_interfaces = {}
        table_data = []
        for intf in self.parsed_json['openconfig-interfaces:interfaces']['interface']:
            counter = intf['state']['counters']['out-discards']
            if counter:
                table_row = []
                table_row.append(self.device.alias)
                table_row.append(intf['name'])
                table_row.append(counter)
                if int(counter) > out_discards_threshold:
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
                                    'Output Discards Counter',
                                    'Passed/Failed'],
                            tablefmt='orgtbl'))
        # should we pass or fail?
        if self.failed_interfaces:
            self.failed('Some interfaces have output discards')
        else:
            self.passed('No interfaces have output discards')

    @aetest.test
    def test_interface_output_errors(self):
        # Test for input discards
        out_errors_threshold = 0
        self.failed_interfaces = {}
        table_data = []
        for intf in self.parsed_json['openconfig-interfaces:interfaces']['interface']:
            counter = intf['state']['counters']['out-errors']
            if counter:
                table_row = []
                table_row.append(self.device.alias)
                table_row.append(intf['name'])
                table_row.append(counter)
                if int(counter) > out_errors_threshold:
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
                                    'Output Errors Counter',
                                    'Passed/Failed'],
                            tablefmt='orgtbl'))
        # should we pass or fail?
        if self.failed_interfaces:
            self.failed('Some interfaces have output errors')
        else:
            self.passed('No interfaces have output errors')

    @aetest.test
    def test_interface_full_duplex(self):
        # Test for input discards
        duplex_threshold = "FULL"
        self.failed_interfaces = {}
        table_data = []
        for intf in self.parsed_json['openconfig-interfaces:interfaces']['interface']:
            if 'openconfig-if-ethernet:ethernet' in intf:
                counter = intf['openconfig-if-ethernet:ethernet']['state']['negotiated-duplex-mode']
                if counter:
                    table_row = []
                    table_row.append(self.device.alias)
                    table_row.append(intf['name'])
                    table_row.append(counter)
                    if counter != duplex_threshold:
                        table_row.append('Failed')
                        self.failed_interfaces[intf['name']] = counter
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
                                    'Duplex Mode',
                                    'Passed/Failed'],
                            tablefmt='orgtbl'))
        # should we pass or fail?
        if self.failed_interfaces:
            self.failed('Some interfaces have are half duplex')
        else:
            self.passed('All interfaces are full duplex')

    @aetest.test
    def test_interface_admin_oper_status(self):
        # Test for input discards
        self.failed_interfaces = {}
        table_data = []
        for intf in self.parsed_json['openconfig-interfaces:interfaces']['interface']:
            if 'admin-status' in intf['state']:            
                admin_status = intf['state']['admin-status']
                oper_status = intf['state']['oper-status']
                table_row = []
                table_row.append(self.device.alias)
                table_row.append(intf['name'])
                table_row.append(admin_status)
                table_row.append(oper_status)
                if oper_status != admin_status:
                    table_row.append('Failed')
                    self.failed_interfaces[intf['name']] = oper_status
                    self.interface_name = intf['name']
                    self.error_counter = self.failed_interfaces[intf['name']]
                else:
                    table_row.append('Passed')
                table_data.append(table_row)
                # display the table
        log.info(tabulate(table_data,
                            headers=['Device', 'Interface',
                                    'Admin Status',
                                    'Oper_Status',
                                    'Passed/Failed'],
                            tablefmt='orgtbl'))
        # should we pass or fail?
        if self.failed_interfaces:
            self.failed('Some interfaces are admin / oper state mismatch')
        else:
            self.passed('All interfaces admin / oper state match')

    @aetest.test
    def test_interface_description_matches_intent(self):
        # Test for input discards
        self.failed_interfaces = {}
        table_data = []
        for self.intf in self.parsed_json['openconfig-interfaces:interfaces']['interface']:
            if 'description' in self.intf['config']:
                for interface,value in self.device.custom.interfaces.items():
                    if self.intf['name'] == interface:
                        self.intended_desc = value['description']
                        actual_desc = self.intf['config']['description']
                        table_row = []
                        table_row.append(self.device.alias)
                        table_row.append(self.intf['name'])
                        table_row.append(self.intended_desc)
                        table_row.append(actual_desc)
                        if actual_desc != self.intended_desc:
                            table_row.append('Failed')
                            self.failed_interfaces[self.intf['name']] = self.intended_desc
                            self.interface_name = self.intf['name']
                            self.error_counter = self.failed_interfaces[self.intf['name']]
                        else:
                            table_row.append('Passed')
                        table_data.append(table_row)
            else:
                for interface,value in self.device.custom.interfaces.items():
                    if self.intf['name'] == interface:
                        self.intended_desc = value['description']
                        actual_desc = ""
                        table_row = []
                        table_row.append(self.device.alias)
                        table_row.append(self.intf['name'])
                        table_row.append(self.intended_desc)
                        table_row.append(actual_desc)
                        if actual_desc != self.intended_desc:
                            table_row.append('Failed')
                            self.failed_interfaces[self.intf['name']] = self.intended_desc
                            self.interface_name = self.intf['name']
                            self.error_counter = self.failed_interfaces[self.intf['name']]
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
            self.pre_change_parsed_json = self.parsed_json
            payload = json.dumps({
                            "openconfig-interfaces:description": f"{ self.intended_desc }"
                        })
            update_interface_description = self.device.rest.put(f"/restconf/data/openconfig-interfaces:interfaces/interface={ self.intf['name'] }/config/description", payload=payload)
            log.info(f"The PUT to update the interface {self.intf['name'] } description status code was { update_interface_description }")
            log.info("Re-testing interface")        
        else:
            self.skipped('No description mismatches skipping test')

    @aetest.test
    def get_post_test_yang_data(self):
        if self.failed_interfaces:
            # Use the RESTCONF OpenConfig YANG Model 
            post_parsed_openconfig_interfaces = self.device.rest.get("/restconf/data/openconfig-interfaces:interfaces")
            # Get the JSON payload
            self.post_parsed_json=post_parsed_openconfig_interfaces.json()
        else:
            self.skipped('No description mismatches skipping test')

    @aetest.test
    def create_post_test_files(self):
        # Create .JSON file
        if self.failed_interfaces:
            with open(f'JSON/{self.device.alias}_OpenConfig_Interfaces_POST_TEST.json', 'w') as f:
                f.write(json.dumps(self.post_parsed_json, indent=4, sort_keys=True))
        else:
            self.skipped('No description mismatches skipping test')

    @aetest.test
    def pre_post_diff(self):
        if self.failed_interfaces:
            for intf in self.pre_change_parsed_json['openconfig-interfaces:interfaces']['interface']:
                    for interface in self.post_parsed_json['openconfig-interfaces:interfaces']['interface']:
                        if intf['name'] == interface['name']:
                            diff = Diff(intf['config'], interface['config'])
                            diff.findDiff()
                            log.info(diff)
        else:
            self.skipped('No description mismatches skipping test')

    @aetest.test
    def retest(self):
        if self.failed_interfaces:
            self.get_pre_test_yang_data()
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