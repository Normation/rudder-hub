import requests
from datetime import datetime
from dotenv import load_dotenv
import pytz
import os
from database import Database

RUDDER_ENDPOINT = 'https://192.168.210.2' # LAB Rudder
ENDPOINT_HTTPS = False


load_dotenv()  # Loads from .env file
API_TOKEN = os.getenv("API_TOKEN")

HEADERS = {"X-API-TOKEN": API_TOKEN}


def formated_current_datetime():
    return datetime.now(pytz.utc).strftime('%Y-%m-%d %H:%M:%S')

class RudderAPI:
    def __init__(self):
        self.base_url = f"{RUDDER_ENDPOINT}/rudder/api/latest"

    def fetch_campaigns(self):
        """Fetch campaigns from Rudder's API.
        Extract campaign id, campaign name, campaign type, campaign status, campaign frequency.

        Returns:
        List[Tuple]
        Example: [('06277867-0033-4349-9779-8566511a49bf', 'Update dev systems', 'system-update', 'enabled', 'weekly')]
        """
        response = requests.get(f'{self.base_url}/campaigns', headers=HEADERS, verify=ENDPOINT_HTTPS)
        try:
            res = []
            for campaign in response.json()['data']['campaigns']:
                res.append((campaign['info']['id'], campaign['info']['name'], campaign['campaignType'], campaign['info']['status']['value'], campaign['info']['schedule']['type']))
        except Exception as e:
            print(f"Error {e}")
        return res
    
    def fetch_campaigns_events(self):
        """
        Fetch campaign events from Rudder's API.
        Extract campaign event id, campaign id, campaign name, campaign state, campaign start date, campaign end date, nb nodes, nb errors.

        Returns:
        Tuple
        Example: [('b840a2b7-8d52-49c8-a750-4cc28a18612b', '06277867-0033-4349-9779-8566511a49bf', 'Update dev systems #40', 
            'scheduled', '2025-03-24T14:00:00Z', '2025-03-24T17:00:00Z', 0, 0)]"""
        response = requests.get(f'{self.base_url}/campaigns/events', headers=HEADERS, verify=ENDPOINT_HTTPS)
        try:
            res = []
            for campaign in response.json()['data']['campaignEvents']:                
                nb_nodes, nb_errors, nb_pkg_maj, nb_pkg_error = self.fetch_one_event(campaign['id'])
                data = (campaign['id'], campaign['campaignId'], campaign['name'], campaign['state']['value'], 
                        campaign['start'], campaign['end'], nb_nodes, nb_errors, nb_pkg_maj, nb_pkg_error )
                res.append(data)
        except Exception as e:
            raise Exception('Error', e)
        return res

    def fetch_one_event(self, event_id):
        """Fetch one campaign event from Rudder's API.
        Extract number of concerned nodes, number of campaign errors on these nodes.

        Returns:
        Tuple
        Example: (4,2)
        """
        response = requests.get(f'{self.base_url}/systemUpdate/events/{event_id}/result', headers=HEADERS, verify=ENDPOINT_HTTPS)
        try:
            event_result = response.json()['data']['eventResult']
            nb_errors, nb_pkg_maj, nb_pkg_error  = 0, 0, 0
            for node in event_result[0]['nodes']:
                if node['status'] == 'error':
                    nb_errors += 1
                    nb_pkg_error += node['nbPackages']
                else:
                    nb_pkg_maj += node['nbPackages']
                    
            nb_nodes = len(event_result[0]['nodes'])
            return nb_nodes, nb_errors, nb_pkg_maj, nb_pkg_error
        except Exception as e:
            raise Exception('Error', e)

    def fetch_nodes(self):
        """Fetch nodes from Rudder's API.
        Extract id, hostname, nb of softwares, nb of software updates, nb of security updates.

        Returns:
        List[Tuple]
        Example: [('root', 'rudder', 704, 78, 54), ('736320a2-998b-45f2-9bad-864b01d48d88', 'monitoring', 650, 50, 45)]
        """
        response = requests.get(f'{self.base_url}/nodes?include=full', headers=HEADERS, verify=ENDPOINT_HTTPS)
        try:
            res = []
            for node in response.json()['data']['nodes']:
                nb_security_updates = sum(1 for soft in node['softwareUpdate'] if soft['kind'] == 'security')
                res.append((node['id'], node['hostname'], node['os']['name'], node['os']['version'], len(node['software']), len(node['softwareUpdate']), nb_security_updates))
        except Exception as e:
            raise Exception('Error', e)
        return res
    
    def fetch_compliance(self):
        """Fetch compliance from Rudder's API.
        Extract compliance data

        Returns:
        List[Tuple]
        Example: [(94, 21.69, 30.65, 11.88, 6.25, 0.12, 0.49, 28.92)]
        """
        response = requests.get(f'{self.base_url}/compliance', headers=HEADERS, verify=ENDPOINT_HTTPS)
        try:
            comp = response.json()['data']['globalCompliance']
            res = [(
                comp.get('compliance'), 
                comp.get('complianceDetails').get('successAlreadyOK', 0), 
                comp.get('complianceDetails').get('successNotApplicable', 0), 
                comp.get('complianceDetails').get('auditCompliant', 0), 
                comp.get('complianceDetails').get('auditNonCompliant', 0), 
                comp.get('complianceDetails').get('error', 0), 
                comp.get('complianceDetails').get('successRepaired', 0), 
                comp.get('complianceDetails').get('auditNotApplicable', 0)
                )]
        except Exception as e:
            raise Exception('Error', e)
        return res
    
    def fetch_cve(self):
        """Fetch cve from Rudder's API.
        Extract in one tuple :
            cve id, 
            cve severity (high or critical), 
            current utc time (having cve present)

        In another, the list of nodes with the nb of critical cves associated

        Returns:
        (List[Tuple], List[Tuple])
        Example: ([('CVE-2025-24928','high', '2025-04-04 09:43:53')], (...)])
        """
        def update_cve_count_for_nodes(dic_nodes, vulnerable_nodes, severity):
            for node in vulnerable_nodes:
                dic_nodes.setdefault(node['nodeId'], {'critical': 0, 'high': 0})
                dic_nodes[node['nodeId']][severity] += 1
            return dic_nodes
        
        response = requests.get(f'{self.base_url}/cve/check/last', headers=HEADERS, verify=ENDPOINT_HTTPS)
        try:
            cves = response.json()['data']['CVEChecks']
            res = []
            nodes = {}
            for cve in cves['checks']:
                if 'severity' in cve['score'] and (cve['score']['severity'] == 'critical' or cve['score']['severity'] == 'high'):
                    nodes = update_cve_count_for_nodes(nodes, cve['nodes'], cve['score']['severity'])
                    res.append((cve['cveId'], cve['score']['severity'], formated_current_datetime()))
            nodes_having_cves = [(nodeId, nodes[nodeId]['critical'], nodes[nodeId]['high']) for nodeId in nodes] 
        except Exception as e:
            raise Exception('Error', e)
        return res, nodes_having_cves

    def fetch_nodes_compliance(self):
        """Fetch compliance for every node from Rudder's API.

        Returns:
        List[Tuple]
        Example: [('01633305-a389-4e6e-a6e4-ae7b2c7e1571', 94, 21.69, 30.65, 11.88, 6.25, 0.12, 0.49, 28.92)]

        """
        response = requests.get(f'{self.base_url}/compliance/nodes', headers=HEADERS, verify=ENDPOINT_HTTPS)
        try:
            nodes = response.json()['data']['nodes']
            res_nodes = []
            for node in nodes:
                res_nodes.append((
                    node.get('id'), 
                    node.get('compliance'), 
                    node.get('complianceDetails').get('successAlreadyOK', 0),
                    node.get('complianceDetails').get('successRepaired', 0),                    
                    node.get('complianceDetails').get('successNotApplicable', 0), 
                    node.get('complianceDetails').get('auditCompliant', 0), 
                    node.get('complianceDetails').get('auditNonCompliant', 0),
                    node.get('complianceDetails').get('error', 0),
                    node.get('complianceDetails').get('noReport', 0),  
                ))
        except Exception as e:
            raise Exception('Error', e)
        return res_nodes
      
    def fetch_compliance_by_rules(self):
        """Fetch compliance by rules from Rudder's API.
        Extract compliance data

        Returns:
        List[Tuple]
        Example: [('01633305-a389-4e6e-a6e4-ae7b2c7e1571', 'Rudder Agent upgrade - RedHat familiy', 94, 21.69, 30.65, 11.88, 6.25, 0.12, 0.49, 28.92)]
        """
        response = requests.get(f'{self.base_url}/compliance/rules', headers=HEADERS, verify=ENDPOINT_HTTPS)
        try:
            rules = response.json()['data']['rules']
            res_rules, nodes_in_rules = [], []
            for rule in rules:
                res_rules.append((
                    rule.get('id'), 
                    rule.get('name'), 
                    rule.get('compliance'), 
                    rule.get('complianceDetails').get('successAlreadyOK', 0), 
                    rule.get('complianceDetails').get('successNotApplicable', 0), 
                    rule.get('complianceDetails').get('auditCompliant', 0), 
                    rule.get('complianceDetails').get('auditNonCompliant', 0), 
                    rule.get('complianceDetails').get('error', 0), 
                    rule.get('complianceDetails').get('successRepaired', 0), 
                    rule.get('complianceDetails').get('auditNotApplicable', 0)
                ))
                for node in rule.get('nodes'):
                    nodes_in_rules.append((
                        node.get('id'),
                        rule.get('id'),
                        node.get('name'), 
                        node.get('compliance'), 
                        node.get('complianceDetails').get('successAlreadyOK', 0), 
                        node.get('complianceDetails').get('successNotApplicable', 0), 
                        node.get('complianceDetails').get('auditCompliant', 0), 
                        node.get('complianceDetails').get('auditNonCompliant', 0), 
                        node.get('complianceDetails').get('error', 0), 
                        node.get('complianceDetails').get('successRepaired', 0), 
                        node.get('complianceDetails').get('auditNotApplicable', 0)
                    ))
        except Exception as e:
            raise Exception('Error', e)
        return res_rules, nodes_in_rules

    def fetch_directives_compliance(self):
        """Fetch compliance by directives from Rudder's API.
        Extract compliance data

        Returns:
        List[Tuple]
        Example: [('01633305-a389-4e6e-a6e4-ae7b2c7e1571', 'Hardening pack for Rudder', 94, 21.69, 30.65, 11.88, 6.25, 0.12, 0.49, 28.92)]
        """
        response = requests.get(f'{self.base_url}/compliance/directives', headers=HEADERS, verify=ENDPOINT_HTTPS)
        try:
            directives = response.json()['data']['directivesCompliance']
            res = []
            for directive in directives:
                res.append((
                    directive.get('id'), 
                    directive.get('name'), 
                    directive.get('compliance'),
                    directive.get('complianceDetails').get('successAlreadyOK', 0), 
                    directive.get('complianceDetails').get('successNotApplicable', 0), 
                    directive.get('complianceDetails').get('successRepaired', 0), 
                    directive.get('complianceDetails').get('auditCompliant', 0), 
                    directive.get('complianceDetails').get('auditNonCompliant', 0), 
                    directive.get('complianceDetails').get('auditNotApplicable', 0), 
                    directive.get('complianceDetails').get('error', 0), 
                    directive.get('complianceDetails').get('noReport', 0)
                ))
        except Exception as e:
            raise Exception('Error', e)
        return res

def concatenate_lists(list1, list2, list3):
    """Concatenate 3 lists of tuple in one in merging the tuple considering their id (first item)
    This function is used to update the nodes table once for every execution of this script.
    """
    res = []
    for item1 in list1:
        concatenated_item = item1
        is_node_in_list = False
        for item2 in list2:
            if item1[0] == item2[0]:
                concatenated_item = item1 + item2[1:]
                is_node_in_list = True
        if is_node_in_list is False:
            # We add (0,0) to fill the gap between list 1 and list 3. 
            # 2 zeros because len(list2)=3 with the first item as the id
            concatenated_item = item1 + (0,0)
        for item3 in list3:
            if item1[0] == item3[0]:
                concatenated_item = concatenated_item + item3[1:]
        res.append(concatenated_item)
    return res


bdd = Database()

rudder = RudderAPI()

data_nodes = rudder.fetch_nodes()

data = rudder.fetch_campaigns()
bdd.update_table("campaigns",('id', 'name', 'campaign_type', 'status', 'frequency'),  data)

data = rudder.fetch_campaigns_events()
bdd.update_table("campaignEvents",
              ('id', 'campaign_id', 'name', 'state', 'start_date', 'end_date', 'updated_nodes', 'failed_nodes', 'updated_pkg', 'failed_pkg'),  data)

data = rudder.fetch_compliance()
bdd.update_table("globalCompliance",
                 ('global_compliance', 'success_already_ok', 'success_not_applicable', 'audit_compliant', 
                  'audit_non_compliant', 'error', 'success_repaired', 'audit_not_applicable'),  data)

data_cves = rudder.fetch_cve()
bdd.update_table("cves", ('cve_id', 'severity', 'last_presence_check'),  data_cves[0])
bdd.update_table("cves", ('cve_id', 'severity', 'last_presence_check'),  [])

compliance_nodes = rudder.fetch_nodes_compliance()

l = concatenate_lists(data_nodes, data_cves[1], compliance_nodes)
bdd.update_table("nodes", (
    'id', 'hostname', 'os_name', 'os_version', 'softwares', 'software_updates', 'software_security_updates',
    'critical_cves', 'high_cves',
    'compliance', 'success_already_ok', 'success_repaired','success_not_applicable', 'audit_compliant', 'audit_non_compliant', 'error', 'no_report'), 
    l)


rules, nodes_in_rules = rudder.fetch_compliance_by_rules()
bdd.update_table("rules", (
    'id', 'name', 'compliance', 'success_already_ok', 'success_not_applicable','audit_compliant',
    'audit_non_compliant', 'error', 'success_repaired', 'audit_not_applicable'), rules)
bdd.update_table("nodesInRules", (
    'id', 'rule_id', 'hostname', 'compliance', 'success_already_ok', 'success_not_applicable','audit_compliant',
    'audit_non_compliant', 'error', 'success_repaired', 'audit_not_applicable'), nodes_in_rules)

directives = rudder.fetch_directives_compliance()
bdd.update_table("directives", (
    'id', 'name', 'compliance', 'success_already_ok', 'success_not_applicable', 'success_repaired', 'audit_compliant',
    'audit_non_compliant', 'audit_not_applicable', 'error','no_report'), directives)
