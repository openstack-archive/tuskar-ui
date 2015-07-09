#!/bin/bash
set -ex

USAGE="Usage: `basename $0` <undercloud_ip> <undercloud_admin_password>"

if [ "$#" -ne 2 ]; then
    echo $USAGE
    exit 1
fi

UNDERCLOUD_IP=$1
UNDERCLOUD_ADMIN_PASSWORD=$2

echo "Copying SSH key..."
cp /home/stack/.ssh/id_rsa /root/.ssh/

echo "Installing system requirements..."
yum install -y git python-devel swig openssl-devel mysql-devel libxml2-devel libxslt-devel gcc gcc-c++
easy_install pip nose

echo "Cloning repos..."
mkdir /opt/stack
cd /opt/stack
git clone git://github.com/openstack/horizon.git
git clone git://github.com/openstack/python-tuskarclient.git
git clone git://github.com/openstack/tuskar-ui.git
git clone git://github.com/rdo-management/tuskar-ui-extras.git

echo "Setting up repos..."
cd horizon
python tools/install_venv.py
./run_tests.sh -V
cp openstack_dashboard/local/local_settings.py.example openstack_dashboard/local/local_settings.py
tools/with_venv.sh pip install -e ../python-tuskarclient/
tools/with_venv.sh pip install -e ../tuskar-ui/
tools/with_venv.sh pip install -e ../tuskar-ui-extras/
cp ../tuskar-ui/_50_tuskar.py.example openstack_dashboard/local/enabled/_50_tuskar.py
cp ../tuskar-ui-extras/_60_tuskar_boxes.py.example openstack_dashboard/local/enabled/_60_tuskar_boxes.py
cp ../tuskar-ui/_10_admin.py.example openstack_dashboard/local/enabled/_10_admin.py
cp ../tuskar-ui/_20_project.py.example openstack_dashboard/local/enabled/_20_project.py
cp ../tuskar-ui/_30_identity.py.example openstack_dashboard/local/enabled/_30_identity.py
sed -i s/'OPENSTACK_HOST = "127.0.0.1"'/'OPENSTACK_HOST = "192.0.2.1"'/ openstack_dashboard/local/local_settings.py
echo 'IRONIC_DISCOVERD_URL = "http://%s:5050" % OPENSTACK_HOST' >> openstack_dashboard/local/local_settings.py
echo 'UNDERCLOUD_ADMIN_PASSWORD = "'$UNDERCLOUD_ADMIN_PASSWORD'"' >> openstack_dashboard/local/local_settings.py
echo 'DEPLOYMENT_MODE = "scale"' >> openstack_dashboard/local/local_settings.py

echo "Setting up networking..."
sudo ip route replace 192.0.2.0/24 dev virbr0 via $UNDERCLOUD_IP

echo "Setting up iptables on the undercloud..."
RULE_1="-A INPUT -p tcp -m tcp --dport 8585 -j ACCEPT"
RULE_2="-A INPUT -p tcp -m tcp --dport 9696 -j ACCEPT"
RULE_3="-A INPUT -p tcp -m tcp --dport 8777 -j ACCEPT"
ssh undercloud "sed -i '/$RULE_1/a $RULE_2' /etc/sysconfig/iptables"
ssh undercloud "sed -i '/$RULE_2/a $RULE_3' /etc/sysconfig/iptables"
ssh undercloud "service iptables restart"
