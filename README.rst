.. _datadomainpy:

datadomain.py
=============

A Python package for interacting with the DataDomain backup appliance. It
uses the DataDomain REST API where possible and reverts to sending
commands via SSH where necessary.

Features
--------

-  Create or delete an mtree
-  Create or delete an NFS export
-  Create or delete a VLAN interface
-  Establish MTree replication

Get started
-----------
::

    pip install git+https://github.com/pauljolsen/datadomain

::

   from datadomain import DataDomain
   from secrets import password

   # Instantiate DataDomain
   dd = DataDomain("nycdd01.mydomain.com")

   # Login
   dd.login("mydomain\\pauljolsen", password)

   # Logout
   dd.logout()

Work with MTrees
~~~~~~~~~~~~~~~~

::

   # Create MTree
   dd.create_mtree("pjo-test-22")

   # Get All MTrees
   dd.get_mtree()

   # Get specific MTree
   dd.get_mtree("pjo-test-22")

   # Delete MTree
   dd.delete_mtree('pjo-test-22')

Work with VLAN interfaces
~~~~~~~~~~~~~~~~~~~~~~~~~

::

   # Create VLAN Interface
   dd.create_interface("10.0.1.125", "255.255.255.0", vlan_id=10, physical_int="veth2")

   # Get All VLAN Interfaces
   dd.get_interface()

   # Get Specific VLAN Interface
   dd.get_interface("veth2.10")

   # Delete VLAN Interface
   dd.delete_interface("veth2.10")

Work with NFS exports
~~~~~~~~~~~~~~~~~~~~~

::

   # Create NFS Export
   dd.create_export(
       name='pjo-test-22',
       clients=[
           {
               "name": "10.0.1.0/24",
               "options": "sec=sys rw no_root_squash no_all_squash secure version=3"
           }
   ])

   # Get All NFS Exports
   dd.get_export()

   # Get specific NFS Export
   dd.get_export("pjo-test-22")

   # Delete NFS Export
   dd.delete_export("pjo-test-22")

Establish MTree replication
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Note that it is assumed the same credentials used on the source also
work on the destination.

::

   dd.replicate_mtree(mtree="pjo-test-22", destination="londd01.mydomain.com")
