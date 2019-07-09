#!/bin/sh

set -e

workdir=$1
build_dir=${workdir}/build
python_dir=${build_dir}/.python

virtualenv=echo

# detect os
os="unknown"
if [ -f /etc/redhat-release ] ; then
    if grep -q 'CentOS Linux release 7' /etc/redhat-release ; then
        os="centos7"
    elif grep -q 'Fedora release 30' /etc/redhat-release ; then
        os="fedora30"
    fi
fi

if [ "$os" == "unknown" ] ; then
    echo "Not support os for building"
    exit 1
fi

if [ "$os" == "centos7" ] ; then
    sudo yum -y install epel-release
    sudo yum -y install python36 python36-pip python36-devel python36-virtualenv

    virtualenv=virtualenv-3.6
    python=${python_dir}/bin/python3
elif [ "$os" == "fedora30" ] ; then
    sudo yum -y install python3 python3-pip python3-devel python3-virtualenv
    virtualenv=virtualenv
    python=${python_dir}/bin/python3
fi

rm -fr ${python_dir}
mkdir -pv ${build_dir}
${virtualenv} ${python_dir}
${python} -m pip install pyYAML rpm


