#!/bin/sh
# -*- encoding: utf-8 -*-
#
# Copyright 2014 Telefónica Investigación y Desarrollo, S.A.U
#
# This file is part of FI-WARE project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License at:
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#
# See the License for the specific language governing permissions and
# limitations under the License.
#
# For those usages not covered by the Apache version 2.0 License please
# contact with opensource@tid.es
#
# File to install fiware-cloto into the system
#
# __author__ = 'gjp'

if [ "$(whoami)" != "root" ]; then
    echo "Sorry, try to install fiware-cloto using root."
    exit 1
fi

echo "Do you wish to insert configuration data before installing?"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) echo "Enter Keystone URL:"; read openstackurl;
        echo "Enter Openstack Admin User:"; read admuser;
        echo "Enter Openstack Admin passwd:"; read admpass;
        echo "Enter Openstack Admin Tenant:"; read admtenant;
        echo "Enter Mysql user:"; read dbuser;
        echo "Enter Mysql user passwd:"; read dbpass;

        match1="OPENSTACK_URL = u'";
        match2="ADM_USER = u'";
        match3="ADM_PASS = u'";
        match4="ADM_TENANT_ID = u'";
        match5="DB_USER = u'";
        match6="DB_PASSWD = u'";
        match7="user =";
        match8="password =";
        file1='cloto/configuration.py';
        file2='cloto/db.cfg';
        if [[ `bash --version | grep 'apple-darwin'` ]]
        then
            sed -i "" "s|$match1|$match1$openstackurl|" $file1;
            sed -i "" "s/$match2/$match2$admuser/" $file1;
            sed -i "" "s/$match3/$match3$admpass/" $file1;
            sed -i "" "s/$match4/$match4$admtenant/" $file1;
            sed -i "" "s/$match5/$match5$dbuser/" $file1;
            sed -i "" "s/$match6/$match6$dbpass/" $file1;
            sed -i "" "s/$match7/$match7\ $dbuser/" $file2;
            sed -i "" "s/$match8/$match8\ $dbpass/" $file2;
        else
            sed -i "s|$match1|$match1$openstackurl|" $file1;
            sed -i "s/$match2/$match2$admuser/" $file1;
            sed -i "s/$match3/$match3$admpass/" $file1;
            sed -i "s/$match4/$match4$admtenant/" $file1;
            sed -i "s/$match5/$match5$dbuser/" $file1;
            sed -i "s/$match6/$match6$dbpass/" $file1;
            sed -i "s/$match7/$match7\ $dbuser/" $file2;
            sed -i "s/$match8/$match8\ $dbpass/" $file2;
        fi;
        if [[ `mysql -u$dbuser -p$dbpass -e 'show databases' | grep "cloto"` ]]
        then
                echo "Cloto database exist, everything is OK"
        else
                mysql -u$dbuser -p$dbpass -e 'CREATE DATABASE cloto'
                echo "Cloto  database was created, Now its ok"
        fi
        break;;
        No )
        echo "Probably you will get some errors during installation, do not worry, it is normal if you chose 'NO'";
        echo "Please remember to complete all configuration data after installation and syncdb after all";
        break;;
    esac
done

echo "Installing fiware-cloto on system..."

installation_path="/opt/policyManager/fiware-cloto"
config_file="fiware-cloto.cfg"
config_path="/etc/sysconfig/$config_file"

log_path="/var/log/fiware-cloto"

if [ ! -d "$log_path" ]; then
  mkdir -m 777 $log_path
  echo 0 > $log_path/RuleEngine.log
fi

echo "..."

#cp settings/fiware-cloto.cfg $config_path

if [ ! -d "$installation_path" ]; then
  mkdir -p $installation_path
fi

echo "..."

cp -r * /opt/policyManager/fiware-cloto/
chmod 777 /opt/policyManager/fiware-cloto/
cd /opt/policyManager/fiware-cloto/
ln fiware-cloto /etc/init.d/fiware-cloto
chmod a+x /etc/init.d/fiware-cloto

echo "..."
pip install -r requirements.txt
python manage.py syncdb
echo "..."
echo "...Done"
echo "Please check file located in $installation_path to configure all parameters "
echo "and check all configuration described in README.md before start fiware-cloto"
echo "### To execute fiware-cloto you must execute 'service fiware-cloto start' ###"
