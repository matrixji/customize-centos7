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
    fi
fi

if [ "$os" == "unknown" ] ; then
    print "Not support os for building"
    exit 1
fi

if [ "$os" == "centos7" ] ; then
    sudo yum -y install epel-release
    sudo yum -y install python36 python36-pip python36-devel python36-virtualenv

    virtualenv=virtualenv-3.6
    python=${python_dir}/bin/python3
fi

rm -fr ${python_dir}
mkdir -pv ${build_dir}
${virtualenv} ${python_dir}
${python} -m pip install pyYAML rpm


