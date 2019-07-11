FROM centos:7


#RUN yum -y install epel-release
RUN yum -y install wget
RUN wget -O /etc/yum.repos.d/epel.repo http://mirrors.aliyun.com/repo/epel-7.repo

RUN yum -y update
RUN yum -y install python36 python36-pip python36-devel python36-rpm
RUN pip3 install pylint pytest pyYAML requests
RUN pip3 install jinja2

RUN yum -y install genisoimage isomd5sum createrepo