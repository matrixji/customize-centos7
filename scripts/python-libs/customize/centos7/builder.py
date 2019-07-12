# encoding: utf-8

from datetime import datetime
from jinja2 import Template
from os import (killpg, getpgid, path)
from signal import SIGKILL
from xml.dom.minidom import parseString

import glob
import logging
import re
import requests
import shutil
import time

from customize.centos7.config import Config
from customize.centos7.action import ShellCommand as sh


class Builder():
    def __init__(self, project_dir, args):
        self.cfg = Config(project_dir, args)
        self.log = logging.getLogger('mycent')
        self.pdir = project_dir
        self.bdir = path.join(project_dir, 'build')

    # TODO: Fixme, move to more sub modules.
    def build(self):
        shell = Builder._shell_actions
        data = dict(
            os_name=self.cfg.get('name'),
            os_version=self.cfg.get('version'),
            project_dir=self.pdir,
            cache_dir=path.join(self.bdir, 'cache'),
            fs_dir=path.join(self.bdir, 'isofs'),
            osurl=self.cfg.get('yum.os-online'),
            rpm_download_dir=path.join(self.bdir, 'rpm_download'),
            groups_xml=path.join(self.bdir, 'cache', 'groups.xml'),
        )

        # download basic files for iso
        self.sequence(*shell("""
            mkdir -pv %(cache_dir)s/{isolinux,images,LiveOS}
        """ % data))

        download_files = (
            'isolinux/boot.msg',
            'isolinux/grub.conf',
            'isolinux/initrd.img',
            'isolinux/isolinux.bin',
            'isolinux/isolinux.cfg',
            'isolinux/splash.png',
            'isolinux/vesamenu.c32',
            'isolinux/vmlinuz',
            'LiveOS/squashfs.img',
        )
        cmds = []
        for dlname in download_files:
            data['dlname'] = dlname
            cmds.append(sh('wget -c -q -O %(cache_dir)s/%(dlname)s %(osurl)s/%(dlname)s' % data))
        self.parallel(*cmds)

        self.sequence(*shell("""
            rm -fr %(fs_dir)s
            mkdir -pv %(fs_dir)s
            cp -fr %(cache_dir)s/{isolinux,images,LiveOS} %(fs_dir)s
            mkdir -pv %(fs_dir)s/Packages
        """ % data))


        # patch yum config
        self.sequence(*shell("""
            mkdir -pv %(cache_dir)s/etc/yum.repos.d
            rm -fr %(cache_dir)s/etc/yum.repos.d/*
            rm -fr %(cache_dir)s/var
            yum clean all
        """ % data))

        repos = self.cfg.get('yum.repos')
        for repo in repos:
            with open(path.join('%(cache_dir)s/etc/yum.repos.d' % data, repo), 'w') as fp:
                fp.write(repos[repo])

        # download rpms for core/minimal
        req = requests.get(path.join(data['osurl'], 'repodata/repomd.xml'))
        repomd_xml = parseString(req.content)
        group_section = None
        for section in repomd_xml.getElementsByTagName('data'):
            if section.getAttribute('type') == 'group':
                group_section = section
                break

        ref = group_section.getElementsByTagName('location')[0].getAttribute('href')
        req = requests.get(path.join(data['osurl'], ref))
        repomd_xml = parseString(req.content)
        core_group = None
        for group in repomd_xml.getElementsByTagName('group'):
            group_id = group.getElementsByTagName('id')[0].firstChild.nodeValue
            if group_id == 'core':
                core_group = group
                break

        core_package_list = []
        all_packages = dict()
        package_list_node = core_group.getElementsByTagName('packagelist')[0]
        for pkg_req in package_list_node.getElementsByTagName('packagereq'):
            pkg_name = pkg_req.firstChild.nodeValue
            core_package_list.append(pkg_name)
            all_packages[pkg_name] = pkg_name

        other_package_list = []
        groups = self.cfg.get('install-packages')
        for _, pkgs in groups.items():
            for pkg in pkgs:
                pkg_name = pkg
                if pkg_name.find('.') > 0:
                    pkg_words = pkg_name.split('-')
                    if len(pkg_words) > 2:
                        pkg_name = '-'.join(pkg_words[:-2])
                other_package_list.append(pkg_name)
                all_packages[pkg_name] = pkg

        self.sequence(*shell('mkdir -pv %(rpm_download_dir)s' % data))
        self.sequence(*shell('rm -fr %(rpm_download_dir)s/*.tmp' % data))
        all_packages = ' '.join(all_packages.values())
        cmd = 'yum -y install --releasever=7 --noplugins'
        cmd += ' --downloadonly --downloaddir={} --installroot={} {}'
        action = sh(cmd.format(data['rpm_download_dir'], data['cache_dir'], all_packages))
        action.run()
        if action.error:
            self.log.error('Run %s return error: %s', action, action.error)
            exit(1)
        self.log.info('Download rpm: %s success', all_packages)

        # generate groups.xml
        # now rpms should download
        install_rpms = set()
        rpms = glob.glob(path.join(data['rpm_download_dir'], '*.rpm'))
        for rpm in rpms:
            line = path.basename(rpm)
            line = re.sub(r'-[^-]+-[^-]+$', '', line)
            install_rpms.add(line)
        install_rpms = list(install_rpms)
        install_rpms.sort()
        context = dict(
            os_name=self.cfg.get('name'),
            install_rpms=install_rpms,
        )

        template_file = path.join(self.pdir, 'scripts', 'groups.xml.j2')
        output_file = data['groups_xml']
        with open(template_file) as fp_template:
            template = Template(fp_template.read())
            content = template.render(context)
            with open(output_file, 'w') as fp_out:
                fp_out.write(content)
        
        # isolinux.cfg
        context = dict(
            os_name=self.cfg.get('name'),
            os_version=self.cfg.get('version'),
        )
        template_file = path.join(self.pdir, 'scripts', 'isolinux.cfg.j2')
        output_file = path.join(data['fs_dir'], 'isolinux/isolinux.cfg')
        with open(template_file) as fp_template:
            template = Template(fp_template.read())
            content = template.render(context)
            with open(output_file, 'w') as fp_out:
                fp_out.write(content)

        # TODO: patch squashfs.img is needed (replace splash)

        # patch initrd.img
        data['time'] = datetime.now().strftime('%Y%m%d%H%M')
        self.sequence(*shell("""
            rm -frv %(cache_dir)s/_initrd_imgfs
            mkdir -pv %(cache_dir)s/_initrd_imgfs
            cp -fr %(fs_dir)s/isolinux/initrd.img %(cache_dir)s/initrd.img.xz
            rm -fr %(cache_dir)s/initrd.img
            cd %(cache_dir)s && xz -d initrd.img.xz
            cd %(cache_dir)s/_initrd_imgfs && cpio -imd < %(cache_dir)s/initrd.img
            rm -fr %(cache_dir)s/initrd.img
            sed s/Product=.*/Product=%(os_name)s/ -i %(cache_dir)s/_initrd_imgfs/.buildstamp
            sed s/Version=.*/Version=%(os_version)s/ -i %(cache_dir)s/_initrd_imgfs/.buildstamp
            sed s/UUID=.*/Version=$(date +%(time)s.x86_64)/ %(cache_dir)s/_initrd_imgfs/.buildstamp
            cat %(cache_dir)s/_initrd_imgfs/.buildstamp
            test -f %(project_dir)s/ks.cfg && cp -fr %(project_dir)s/ks.cfg %(cache_dir)s/_initrd_imgfs || echo
            cd %(cache_dir)s/_initrd_imgfs && find . | cpio -c -o >%(cache_dir)s/initrd.img
            xz -C crc32 %(cache_dir)s/initrd.img
            cp -fr %(cache_dir)s/initrd.img.xz %(fs_dir)s/isolinux/initrd.img
        """ % data))

        # discinfo
        self.sequence(*shell("""
            date '+%%s.%%N' > %(fs_dir)s/.discinfo
            echo %(os_version)s >> %(fs_dir)s/.discinfo
            echo x86_64 >> %(fs_dir)s/.discinfo
            echo ALL >> %(fs_dir)s/.discinfo
        """ % data))

        # copy packages
        self.sequence(sh('cp -fr %(rpm_download_dir)s/*.rpm %(fs_dir)s/Packages' % data))

        # generate repomd
        self.sequence(*shell("""
            cd %(fs_dir)s && createrepo -g %(groups_xml)s .
        """ % data))

        # iso
        isoname = '%(os_name)s-%(os_version)s.iso' % data
        isopath = path.join(data['project_dir'], isoname)
        cmd = 'mkisofs -joliet-long -T -o ' + isopath
        cmd += ' -V ' + data['os_name'].upper() + '_' + str(data['os_version'])
        cmd += ' -b isolinux/isolinux.bin -c isolinux/boot.cat'
        cmd += ' -no-emul-boot -boot-load-size 4'
        cmd += ' -boot-info-table -R .'
        self.sequence(sh('cd %(fs_dir)s && ' % data + cmd))
        self.sequence(sh('implantisomd5 ' + isopath))

    @staticmethod
    def _shell_actions(lines):
        actions = lines.split('\n')
        return [sh(act.strip()) for act in actions if act.strip()]

    def sequence(self, *actions):
        for action in actions:
            action.run()
            if action.error:
                self.log.error('Run %s return error: %s', action, action.error)
            else:
                self.log.info('Run %s return success', action)
            if action.error:
                exit(1)

    def parallel(self, *actions):
        for action in actions:
            action.start()
        acts = set(actions)
        while acts:
            time.sleep(0.1)
            has_error = False
            unfinished = set()
            for action in acts:
                if not action.is_alive():
                    if action.error:
                        has_error = True
                        self.log.error('Run %s return error: %s', action, action.error)
                    else:
                        self.log.info('Run %s return success', action)
                    if has_error:
                        break
                else:
                    unfinished.add(action)
                acts = unfinished

            if has_error:
                for action in actions:
                    action.stop()
                exit(1)
