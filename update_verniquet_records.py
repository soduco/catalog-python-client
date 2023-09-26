#!/usr/bin/env python3

import logging
from soduco_geonetwork.api_wrapper import (
    config,
    dataset,
    geonetwork,
)

import pandas

def main():
    logging.basicConfig(level="INFO")
    logging.info("START")
    #version = "bnf"
    version = "stanford"
    version_start = 1
    list = pandas.read_csv(f"../geonetwork-resources/verniquet_{version}/yaml_list.csv")
    session = geonetwork.log_in(
        config.config["GEONETWORK_USER"], config.config["GEONETWORK_PASSWORD"]
    )
    for index, row in list.iterrows():
        uuid = row["geonetwork_uuid"]
        if (index > version_start):
            sheet = index -version_start
            wms = f"verniquet_{version}_{sheet}"
            logging.info(f"Row {index} = Sheet{sheet} => {uuid} => {wms}")
            #xpath = "./mdb:MD_Metadata/mdb:identificationInfo/mri:MD_DataIdentification/mri:citation/cit:CI_Citation"
            #value = f"<gn_add><cit:identifier xmlns:cit=\"http://standards.iso.org/iso/19115/-3/cit/2.0\"><mcc:MD_Identifier xmlns:mcc=\"http://standards.iso.org/iso/19115/-3/mcc/1.0\"><mcc:code><gco:CharacterString xmlns:gco=\"http://standards.iso.org/iso/19115/-3/gco/1.0\">{wms}</gco:CharacterString></mcc:code><mcc:codeSpace><gco:CharacterString xmlns:gco=\"http://standards.iso.org/iso/19115/-3/gco/1.0\">wms_id</gco:CharacterString></mcc:codeSpace></mcc:MD_Identifier></cit:identifier></gn_add>"
            #xpath = "./mdb:MD_Metadata/mdb:identificationInfo/mri:MD_DataIdentification/mri:citation/cit:CI_Citation/cit:identifier"
            #value = "<gn_delete></gn_delete>"
            #xpath = "./mdb:MD_Metadata/mdb:distributionInfo/mrd:MD_Distribution/mrd:transferOptions/mrd:MD_DigitalTransferOptions"
# value = f"<gn_add>\
# <mrd:onLine xmlns:mrd=\"http://standards.iso.org/iso/19115/-3/mrd/1.0\">\
# <cit:CI_OnlineResource xmlns:cit=\"http://standards.iso.org/iso/19115/-3/cit/2.0\">\
# <cit:linkage>\
# <gco:CharacterString xmlns:gco=\"http://standards.iso.org/iso/19115/-3/gco/1.0\">\
# https://map.geohistoricaldata.org/mapproxy/service=WMS?REQUEST=GetCapabilities\
# </gco:CharacterString>\
# </cit:linkage>\
# <cit:protocol xmlns:cit=\"http://standards.iso.org/iso/19115/-3/cit/2.0\">\
# <gco:CharacterString xmlns:gco=\"http://standards.iso.org/iso/19115/-3/gco/1.0\">OGC:WMS</gco:CharacterString>\
# </cit:protocol>\
# <cit:name xmlns:cit=\"http://standards.iso.org/iso/19115/-3/cit/2.0\">\
# <gco:CharacterString xmlns:gco=\"http://standards.iso.org/iso/19115/-3/gco/1.0\">{wms}</gco:CharacterString>\
# </cit:name>\
# <cit:description xmlns:cit=\"http://standards.iso.org/iso/19115/-3/cit/2.0\">\
# <gco:CharacterString xmlns:gco=\"http://standards.iso.org/iso/19115/-3/gco/1.0\">Visualisation</gco:CharacterString>\
# </cit:description>\
# <cit:function xmlns:cit=\"http://standards.iso.org/iso/19115/-3/cit/2.0\">\
# <cit:CI_OnLineFunctionCode codeList=\"http://standards.iso.org/iso/19115/resources/Codelists/cat/codelists.xml#CI_OnLineFunctionCode\" codeListValue=\"browsing\"/>\
# </cit:function>\
# </cit:CI_OnlineResource>\
# </mrd:onLine>\
# </gn_add>"
            #xpath = "./mdb:MD_Metadata/mdb:distributionInfo/mrd:MD_Distribution/mrd:transferOptions/mrd:MD_DigitalTransferOptions/mrd:onLine/cit:CI_OnlineResource[starts-with(cit:linkage/gco:CharacterString,'https://www.davidrumsey') or starts-with(cit:linkage/gco:CharacterString,'https://dataverse') or starts-with(cit:linkage/gco:CharacterString,'https://gallica.bnf.fr')]/cit:protocol/gco:CharacterString"
            #value = "<gn_replace>WWW:DOWNLOAD-1.0-http--download</gn_replace>"
            xpath = ".//cit:CI_Organisation[cit:name/gco:CharacterString='The SoDUCo project' or cit:name/gco:CharacterString='The SoDUCo Project']"
            value = "<gn_add>\
<cit:logo xmlns:cit=\"http://standards.iso.org/iso/19115/-3/cit/2.0\">\
<mcc:MD_BrowseGraphic xmlns:mcc=\"http://standards.iso.org/iso/19115/-3/mcc/1.0\">\
<mcc:fileName xmlns:mcc=\"http://standards.iso.org/iso/19115/-3/mcc/1.0\">\
<gco:CharacterString xmlns:gco=\"http://standards.iso.org/iso/19115/-3/gco/1.0\">https://catalog.geohistoricaldata.org/geonetwork/images/harvesting/soduco.png</gco:CharacterString>\
</mcc:fileName>\
</mcc:MD_BrowseGraphic>\
</cit:logo>\
<gn_add>"
            logging.info(value)
            response = dataset.update([uuid], xpath, value, session)
            logging.info(response)
    logging.info("END")

if __name__ == "__main__":
    main()
