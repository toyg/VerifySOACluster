# -*- coding: utf-8 -*-

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright @ 2103 Giacomo Lacava - g.lacava@gmail.com

from targetvalidator import TargetValidator

# map names from properties file to Oracle example names
localServers = {
    'OSB_Cluster': osb_target_name,
    'SOA_Cluster': soa_target_name,
    'BAM_Cluster': bam_target_name,
    'WSM-PM_Cluster': wsm_target_name,
    'WLS_OSB1': osb1_server_name,
    'AdminServer': admin_server_name
}

# connect
connect(admin_username,admin_password,admin_url)
domainConfig()

tv = TargetValidator(cmo, localServers)

# validate all mappings
for itemType in tv.PARSEMAP:
    tv.prettyValidateDeployments(itemType)
