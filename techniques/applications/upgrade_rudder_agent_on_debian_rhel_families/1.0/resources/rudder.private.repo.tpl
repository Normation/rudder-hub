[Rudder_{{{vars.upgrade_rudder_agent_on_debian_rhel_families.rudder_version}}}]
name=Rudder {{{vars.upgrade_rudder_agent_on_debian_rhel_families.rudder_version}}}
username={{{vars.upgrade_rudder_agent_on_debian_rhel_families.rudder_licence}}}
password={{{vars.upgrade_rudder_agent_on_debian_rhel_families.licence_password}}}
baseurl=http://{{{vars.upgrade_rudder_agent_on_debian_rhel_families.rudder_repository}}}/rpm/{{{vars.upgrade_rudder_agent_on_debian_rhel_families.rudder_version}}}/RHEL_{{{vars.sys.os_version_major}}}/
gpgcheck=1
gpgkey=https://{{{vars.upgrade_rudder_agent_on_debian_rhel_families.rudder_repository}}}/rpm/rudder_rpm_key.pub
