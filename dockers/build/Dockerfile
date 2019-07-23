FROM centos:7


RUN yum -y install wget && \
    wget -O /etc/yum.repos.d/epel.repo http://mirrors.aliyun.com/repo/epel-7.repo && \
    yum -y install python36 python36-pip python36-devel python36-rpm \
                   genisoimage isomd5sum createrepo squashfs-tools && \
    pip3 install pylint pytest pyYAML requests jinja2 && \
    yum clean all
