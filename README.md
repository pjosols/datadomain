datadomain.py
=======
A Python module for interacting with the DataDomain backup appliance. It uses the DataDomain REST API where possible 
and reverts to sending commands via SSH where necessary.

## Features 
- Create or delete an mtree
- Create or delete an NFS export
- Create or delete a VLAN interface
- Establish mtree replication



## Get started
```
from datadomain import DataDomain
from secrets import password

# Instantiate DataDomain
dd = DataDomain("nycdd01.mydomain.com")

# Login
dd.login("corp\\pauljolsen", password)

# Logout
dd.logout()
```

### Work with Mtrees
```
# Create Mtree
dd.create_mtree("pjo-test-22")

# Get All Mtrees
dd.get_mtree()

# Get specific Mtree
dd.get_mtree("pjo-test-22")

# Delete Mtree
dd.delete_mtree('pjo-test-22')
```

### Work with VLAN interfaces
```
# Create VLAN Interface
dd.create_interface("10.0.1.125", "255.255.255.0", physical_int="veth2")

# Get All VLAN Interfaces
dd.get_interface()

# Get Specific VLAN Interface
dd.get_interface("veth2.10")

# Delete VLAN Interface
dd.delete_interface("veth2.10")
```

### Work with NFS exports
```
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
```

### Establish Mtree replication
Note that it is assumed the same credentials used on the source also work on the destination.
```
dd.replicate_mtree(mtree="pjo-test-26", destination="londd01.mydomain.com") 

```
