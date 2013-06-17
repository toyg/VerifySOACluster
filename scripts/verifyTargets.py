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
