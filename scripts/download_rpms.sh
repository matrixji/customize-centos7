#!/bin/sh

destdir=$1

blacklist="gpg-pubkey"

mkdir -pv $destdir
for rpm in $(rpm -qai | egrep "^(Name|Architecture) *:" | sed 's/.*: //' | awk '{
    printf "%s.", $0;
    getline;
    print
}') ; do
    rpm=$(echo $rpm|sed 's/\.(none)//')
    if echo $blacklist | grep -wq $rpm ; then
        echo skip $rpm
    else
        echo download rpm for $rpm
        if ! yum -y reinstall --downloadonly --downloaddir=$destdir $rpm 2>&1 >$destdir/last.log ; then
            if ! grep -w 'Error: Nothing to do' $destdir/last.log ; then
                echo yum error
                exit 1
            fi
        fi
    fi
done
