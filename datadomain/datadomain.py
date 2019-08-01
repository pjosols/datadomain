import requests
import json
import paramiko


class DataDomain(object):

    def __init__(self, hostname):

        self.username = str()
        self.password = str()
        self.hostname = hostname
        self.verify = False
        self.url = "https://{}:3009/rest/v1.0".format(hostname)
        self.url_auth = "{}/auth".format(self.url)
        self.url_mtree = "{}/dd-systems/0/mtrees".format(self.url)
        self.url_network = "{}/dd-systems/0/networks".format(self.url)
        self.url_export = "{}/dd-systems/0/protocols/nfs/exports".format(self.url)
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def _get(self, url):
        return requests.get(url, verify=self.verify, headers=self.headers)

    def _post(self, url, json_):
        return requests.post(url, verify=self.verify, headers=self.headers, json=json_)

    def _delete(self, url):
        return requests.delete(url, verify=self.verify, headers=self.headers)

    def login(self, username, password):
        self.username = username
        self.password = password
        auth_payload = {
            "auth_info": {
                "username": username,
                "password": password
            }
        }
        login_ = self._post(self.url_auth, auth_payload)
        if login_.status_code != 201:
            return False
        token_ = login_.headers["X-DD-AUTH-TOKEN"]
        self.headers.update({"X-DD-AUTH-TOKEN": token_})
        return True

    def logout(self):
        logout_ = self._delete(self.url_auth)
        if logout_.status_code != 200:
            return False
        return True

    def _ssh_connect(self, hostname):
        """
        Helper method for those methods that use SSH.
        :return:
        """
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(hostname, username=self.username, password=self.password)  # use ssh keys instead
        except paramiko.ssh_exception.AuthenticationException:
            return False
        except Exception:
            return False
        return ssh

    def create_interface(self, ip_address, netmask, vlan_id, physical_int="veth2"):
        """
        Here we use SSH because the DataDomain API v1.0 doesn't support creating a VLAN.
        :param ip_address:
        :param netmask:
        :param vlan_id:
        :param physical_int:  Specify the physical interface on which to create the VLAN interface. "veth2" by default.
        :return:
        """
        # Connect to DataDomain via ssh
        ssh = self._ssh_connect(self.hostname)
        if not ssh:
            return False

        # Create the VLAN
        chan = ssh.get_transport().open_session()
        chan.exec_command("net create interface {} vlan {}".format(physical_int, vlan_id))
        if chan.recv_exit_status() != 0:
            return False

        # Configure the IP address
        chan = ssh.get_transport().open_session()
        chan.exec_command("net config {}.{} {} netmask {}".format(physical_int, vlan_id, ip_address, netmask))
        if chan.recv_exit_status() != 0:
            return False
        return True

    def get_interface(self, name=None):
        """

        :param name: Optional name like "veth2.242"
        :return:
        """
        if name:
            url_network = "{}/{}".format(self.url_network, name)
        else:
            url_network = self.url_network
        network_ = self._get(url_network)
        if network_.status_code != 200:
            return False
        return network_.content

    def delete_interface(self, name):
        ssh = self._ssh_connect(self.hostname)
        if not ssh:
            return False
        chan = ssh.get_transport().open_session()
        chan.exec_command("net destroy {}".format(name))
        if chan.recv_exit_status() != 0:
            return False

        return True

    def create_mtree(self, name):
        mtree_payload = {
             "mtree_create": {
                 "name": "/data/col1/{}".format(name)  # like /data/col1/pjo-test-1
             }
         }
        mtree_ = self._post(self.url_mtree, mtree_payload)
        if mtree_.status_code != 201:
            return False
        return mtree_.content

    def get_mtree(self, name=None):
        """

        :param name:  Optional name like "my-mtree"
        :return:
        """
        if name:
            url_mtree = "{}/%2Fdata%2Fcol1%2F{}".format(self.url_mtree, name)
        else:
            url_mtree = self.url_mtree

        mtree_ = self._get(url_mtree)
        if mtree_.status_code != 200:
            return False
        return mtree_.content

    def delete_mtree(self, name):
        url_mtree = "{}/%2Fdata%2Fcol1%2F{}".format(self.url_mtree, name)
        mtree_ = self._delete(url_mtree)
        if mtree_.status_code != 200:
            return False
        return True

    def create_export(self, name, clients):
        export_payload = {
            "export_create": {
                "path": "/data/col1/{}".format(name),
                "clients": clients
            }
        }
        export_ = self._post(self.url_export, export_payload)
        if export_.status_code != 201:
            return False
        return export_.content

    def get_export(self, name=None):
        if name:
            url_export = "{}/%2Fdata%2Fcol1%2F{}".format(self.url_export, name)
        else:
            url_export = self.url_export

        export_ = self._get(url_export)
        if export_.status_code != 200:
            return False
        return export_.content

    def delete_export(self, name):
        url_export = "{}/%2Fdata%2Fcol1%2F{}".format(self.url_export, name)
        export_ = self._delete(url_export)
        if export_.status_code != 200:
            return False
        return True

    def replicate_mtree(self, mtree, destination):
        """
        Replicate an mtree from the current DataDomain to a specified destination. Note that this assumes the source and
        destination use the same credentials.
        :param mtree:
        :param destination: FQDN of the destination
        :return:
        """
        # Connect to source DataDomain via ssh
        src = self._ssh_connect(self.hostname)
        if not src:
            return False

        # Connect to destination DataDomain via ssh
        dst = self._ssh_connect(destination)
        if not dst:
            return False

        # on dest run 'replication add source destination'
        chan1 = dst.get_transport().open_session()
        chan1.exec_command(
            "replication add source mtree://{0}/data/col1/{1} destination mtree://{2}/data/col1/{1}".format(
                self.hostname,
                mtree,
                destination
            ))
        if chan1.recv_exit_status() != 0:
            return False

        # on source run 'replication add source destination'
        chan2 = src.get_transport().open_session()
        chan2.exec_command(
            "replication add source mtree://{0}/data/col1/{1} destination mtree://{2}/data/col1/{1}".format(
                self.hostname,
                mtree,
                destination
            ))
        if chan2.recv_exit_status() != 0:
            return False

        # on either run 'replication initialize destination'
        chan3 = src.get_transport().open_session()
        chan3.exec_command("replication initialize mtree://{0}/data/col1/{1}".format(
            destination,
            mtree
        ))
        if chan3.recv_exit_status() != 0:
            return False

        return True
