"""Things to remember
Keep ip name and vm name same to easily get ip address
delete vm
delete nic
delete ip
delete vhd blob storage, not available with python sdk yet (check the blob storage pricing)
OS_DISK_NAME (vhd) name should be unique every time if existing vhds are not deleted"""

import traceback

import azure
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import DiskCreateOption
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.network.models import PublicIPAddress
from azure.mgmt.resource import ResourceManagementClient
from msrestazure.azure_exceptions import CloudError

AZURE_TENANT_ID = ""
AZURE_CLIENT_ID = ""
AZURE_CLIENT_SECRET = ""
AZURE_SUBSCRIPTION_ID = ""

LOCATION = 'westus2'
#im_crawler_keys 12/31/2299 /Q1QiVhgwNLrHOwwvaBAzKaBbgEA+p7YmnBT/6z8Taw=
# Resource Group
GROUP_NAME = ''

# Network
VNET_NAME = ''
SUBNET_NAME = ''

# VM
OS_DISK_NAME = ""
STORAGE_NAME = ""
SOURCE_CUSTOM_IMAGE_VHD = "https://imcrawleruswest2.blob.core.windows.net/vhds/im-crawler-trends-base20170615160218.vhd"

NIC_NAME = 'azure-sample-nic' # THis has to be dynamically generated unique for each vm
USERNAME = 'uname'
PASSWORD = 'password'

VM_NAME = 'TestVm'
PUBLIC_IP_NAME = VM_NAME

VM_REFERENCE = {
    'linux': {
        'publisher': 'Canonical',
        'offer': 'UbuntuServer',
        'sku': '17.04',
        'version': 'latest'
    },
    'windows': {
        'publisher': 'MicrosoftWindowsServerEssentials',
        'offer': 'WindowsServerEssentials',
        'sku': 'WindowsServerEssentials',
        'version': 'latest'
    }
}


def get_credentials():
    subscription_id = AZURE_SUBSCRIPTION_ID
    credentials = ServicePrincipalCredentials(
        client_id=AZURE_CLIENT_ID,
        secret=AZURE_CLIENT_SECRET,
        tenant=AZURE_TENANT_ID
    )
    return credentials, subscription_id

def run_example():
    """Virtual Machine management example."""
    #
    # Create all clients with an Application (service principal) token provider
    #
    credentials, subscription_id = get_credentials()
    resource_client = ResourceManagementClient(credentials, subscription_id)
    compute_client = ComputeManagementClient(credentials, subscription_id)
    network_client = NetworkManagementClient(credentials, subscription_id)
    try:
        # Create a NIC
        subnet_info = network_client.subnets.get(GROUP_NAME, VNET_NAME, SUBNET_NAME);
        nic = create_nic(network_client, subnet_info)


        #############
        # VM Sample #
        #############

        # Create Linux VM
        print('\nCreating Linux Virtual Machine')
        vm_parameters = create_vm_parameters(nic.id, VM_REFERENCE['linux'])
        async_vm_creation = compute_client.virtual_machines.create_or_update(
            GROUP_NAME, VM_NAME, vm_parameters)
        async_vm_creation.wait()

        virtual_machine = compute_client.virtual_machines.get(
            GROUP_NAME,
            VM_NAME
        )
    except CloudError:
        print('A VM operation failed:', traceback.format_exc(), sep='\n')
    else:
        print('All example operations completed successfully!')
        public_ip = network_client.public_ip_addresses.get(GROUP_NAME, PUBLIC_IP_NAME)
        print(public_ip.ip_address)
    finally:
        # Delete Resource group and everything in it
        print('\nDone')

def create_nic(network_client, subnet_info):
    public_ip = PublicIPAddress(public_ip_allocation_method='Dynamic', location=LOCATION)
    async_ip_creation = network_client.public_ip_addresses.create_or_update(resource_group_name=GROUP_NAME, parameters=public_ip, public_ip_address_name = PUBLIC_IP_NAME)
    result = async_ip_creation.result()

    async_nic_creation = network_client.network_interfaces.create_or_update(
        GROUP_NAME,
        NIC_NAME,
        {
            'location': LOCATION,
            'ip_configurations': [azure.mgmt.network.v2017_03_01.models.NetworkInterfaceIPConfiguration(
                name='default',
                subnet=subnet_info,
                public_ip_address=result,

            ),],
        }
    )
    return async_nic_creation.result()


def create_vm_parameters(nic_id, vm_reference):
    """Create the VM parameters structure.
    """
    storage_profile = azure.mgmt.compute.models.StorageProfile(
        os_disk=azure.mgmt.compute.models.OSDisk(
            caching=azure.mgmt.compute.models.CachingTypes.none,
            create_option=azure.mgmt.compute.models.DiskCreateOptionTypes.from_image,
            name=OS_DISK_NAME,
            vhd=azure.mgmt.compute.models.VirtualHardDisk(uri='https://{0}.blob.core.windows.net/vhds/{1}.vhd'.format(
                    STORAGE_NAME,
                    OS_DISK_NAME,)),
            os_type ='Linux',
            image = azure.mgmt.compute.models.VirtualHardDisk(uri=SOURCE_CUSTOM_IMAGE_VHD)
        )
    )

    return {
        'location': LOCATION,
        'os_profile': {
            'computer_name': VM_NAME,
            'admin_username': USERNAME,
            'admin_password': PASSWORD
        },
        'hardware_profile': {
            'vm_size': 'Standard_A1'
        },
        'storage_profile': storage_profile,
        'network_profile': {
            'network_interfaces': [{
                'id': nic_id,
            }]
        },
    }

if __name__ == "__main__":
    run_example()

def destroy(network_client, compute_client):
    async_vm_delete = compute_client.virtual_machines.delete(GROUP_NAME, VM_NAME)
    async_vm_delete.wait()
    delete_nic = network_client.network_interfaces.delete(GROUP_NAME, NIC_NAME)
    delete_nic.wait()
    result = network_client.public_ip_addresses.delete(
        GROUP_NAME,
        "test"
    )
    result.wait()



def get_public_ip_address():
    from azure.mgmt.network import NetworkManagementClient, NetworkManagementClientConfiguration

    subscription_id = '33333333-3333-3333-3333-333333333333'

    credentials = ...

    network_client = NetworkManagementClient(
        NetworkManagementClientConfiguration(
            credentials,
            subscription_id
        )
    )

    GROUP_NAME = 'XXX'
    VM_NAME = 'xxx'
    PUBLIC_IP_NAME = VM_NAME

    public_ip_address = network_client.public_ip_addresses.get(GROUP_NAME, VM_NAME)
    print(public_ip_address.ip_address)
    print(public_ip_address.ip_configuration.private_ip_address)
