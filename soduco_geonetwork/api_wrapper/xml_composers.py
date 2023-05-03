"""System module."""
import os
import uuid
import yaml
import xml.etree.ElementTree as ET
from typing import List, Optional
from pydantic import BaseModel
from collections import defaultdict

XML_TEMPLATE = os.path.dirname(__file__) + "/xmltemplates/dataset_iso19115.xml"

"""
register_namespaces() method isn't sufficient alone.
We have to use namespace url when creating an Element.

For example we want to create the element <gml:beginPosition> :
ET.Element("{http://www.opengis.net/gml/3.2}beginPosition")

Lineage relations to non-yet uploaded resources are postponed
Si la valeur n'est pas un UUID, c'est une resource locale.
Dans ce cas on enregistre la resource dans un attribut dictionnaire self.postponed:
Il faudra résoudre les identifiants des relations "resourceLineage" avant d'exporter
le dictionnaire.
"""

# we save here the namespaces url to reuse them later
MDB = "http://standards.iso.org/iso/19115/-3/mdb/2.0"
CAT = "http://standards.iso.org/iso/19115/-3/cat/1.0"
GFC = "http://standards.iso.org/iso/19110/gfc/1.1"
CIT = "http://standards.iso.org/iso/19115/-3/cit/2.0"
GCX = "http://standards.iso.org/iso/19115/-3/gcx/1.0"
GEX = "http://standards.iso.org/iso/19115/-3/gex/1.0"
LAN = "http://standards.iso.org/iso/19115/-3/lan/1.0"
SRV = "http://standards.iso.org/iso/19115/-3/srv/2.1"
MAS = "http://standards.iso.org/iso/19115/-3/mas/1.0"
MCC = "http://standards.iso.org/iso/19115/-3/mcc/1.0"
MCO = "http://standards.iso.org/iso/19115/-3/mco/1.0"
MDA = "http://standards.iso.org/iso/19115/-3/mda/1.0"
MDS = "http://standards.iso.org/iso/19115/-3/mds/2.0"
MDT = "http://standards.iso.org/iso/19115/-3/mdt/2.0"
MEX = "http://standards.iso.org/iso/19115/-3/mex/1.0"
MMI = "http://standards.iso.org/iso/19115/-3/mmi/1.0"
MPC = "http://standards.iso.org/iso/19115/-3/mpc/1.0"
MRC = "http://standards.iso.org/iso/19115/-3/mrc/2.0"
MRD = "http://standards.iso.org/iso/19115/-3/mrd/1.0"
MRI = "http://standards.iso.org/iso/19115/-3/mri/1.0"
MRL = "http://standards.iso.org/iso/19115/-3/mrl/2.0"
MRS = "http://standards.iso.org/iso/19115/-3/mrs/1.0"
MSR = "http://standards.iso.org/iso/19115/-3/msr/2.0"
MDQ = "http://standards.iso.org/iso/19157/-2/mdq/1.0"
MAC = "http://standards.iso.org/iso/19115/-3/mac/2.0"
GCO = "http://standards.iso.org/iso/19115/-3/gco/1.0"
GML = "http://www.opengis.net/gml/3.2"
XLINK = "http://www.w3.org/1999/xlink"
XSI = "http://www.w3.org/2001/XMLSchema-instance"

PREFIX_MAP = {
    "mdb": MDB,
    "cat": CAT,
    "gfc": GFC,
    "cit": CIT,
    "gcx": GCX,
    "gex": GEX,
    "lan": LAN,
    "srv": SRV,
    "mas": MAS,
    "mcc": MCC,
    "mco": MCO,
    "mda": MDA,
    "mds": MDS,
    "mdt": MDT,
    "mex": MEX,
    "mmi": MMI,
    "mpc": MPC,
    "mrc": MRC,
    "mrd": MRD,
    "mri": MRI,
    "mrl": MRL,
    "mrs": MRS,
    "msr": MSR,
    "mdq": MDQ,
    "mac": MAC,
    "gco": GCO,
    "gml": GML,
    "xlink": XLINK,
    "xsi": XSI,
}


class Title(BaseModel):
    """
    Creates a new ISO-19115 title element.

    Xml serialisation:
    <cit:title>
        <gco:CharacterString></gco:CharacterString>
    </cit:title>

    TO DO:
    XML serialisation for multilingue:
    <cit:title xsi:type="lan:PT_FreeText_PropertyType">
        <gco:CharacterString>Atlas du plan général de la Ville de Paris</gco:CharacterString>
        <lan:PT_FreeText>
            <lan:textGroup>
            <lan:LocalisedCharacterString locale="#EN">Atlas du plan général de la Ville de Paris</lan:LocalisedCharacterString>
            </lan:textGroup>
            <lan:textGroup>
            <lan:LocalisedCharacterString locale="#FR">Atlas du plan général de la Ville de Paris</lan:LocalisedCharacterString>
            </lan:textGroup>
        </lan:PT_FreeText>
    </cit:title>
    Args:
        BaseModel (_type_): _description_

    Returns:
        _type_: _description_
    """

    title: str
    parent_element_xpath = ".//mri:MD_DataIdentification/mri:citation/cit:CI_Citation"

    def compose_xml(self):
        """Compose XML elements"""
        xml = ET.Element(f"{{{CIT}}}title")
        e_title = ET.SubElement(xml, f"{{{GCO}}}CharacterString")
        e_title.text = self.title
        return xml


class Date(BaseModel):
    """

    XML serialisation:
    <cit:date>
        <cit:CI_Date>
            <cit:date>
            <gco:Date>{value}</gco:Date>
            </cit:date>
            <cit:dateType>
            <cit:CI_DateTypeCode
                codeList="http://standards.iso.org/iso/19115/resources/Codelists/cat/codelists.xml#CI_DateTypeCode"
                codeListValue="{event}"
            />
            </cit:dateType>
        </cit:CI_Date>
    </cit:date>
    """

    value: str
    event: str
    parent_element_xpath = ".//mri:MD_DataIdentification/mri:citation/cit:CI_Citation"

    def compose_xml(self):
        """Compose XML elements"""
        xml = ET.Element(f"{{{CIT}}}date")
        cit_ci_date = ET.SubElement(xml, f"{{{CIT}}}CI_Date")
        cit_date = ET.SubElement(cit_ci_date, f"{{{CIT}}}date")
        gco_date = ET.SubElement(cit_date, f"{{{GCO}}}Date")
        gco_date.text = self.value

        cit_datetype = ET.SubElement(cit_ci_date, f"{{{CIT}}}dateType")
        ET.SubElement(
            cit_datetype,
            f"{{{CIT}}}CI_DateTypeCode",
            attrib={
                "codeList": "http://standards.iso.org/iso/19115/resources/Codelists/cat/codelists.xml#CI_DateTypeCode",
                "codeListValue": self.event,
            },
        )
        return xml


class PresentationForm(BaseModel):
    """
    XML serialisation:
    <cit:presentationForm>
        <cit:CI_PresentationFormCode
            codeList="http://standards.iso.org/iso/19115/resources/Codelists/cat/codelists.xml#CI_PresentationFormCode"
            codeListValue="{presentationFormat}"/>
    </cit:presentationForm>

    Args:
        BaseModel (_type_): _description_

    Returns:
        _type_: _description_
    """

    presentationForm: str
    parent_element_xpath = ".//mri:MD_DataIdentification/mri:citation/cit:CI_Citation"

    def compose_xml(self):
        """Compose XML elements"""
        xml = ET.Element(f"{{{CIT}}}presentationForm")
        ET.SubElement(
            xml,
            f"{{{CIT}}}CI_PresentationFormCode",
            attrib={
                "codeList": "http://standards.iso.org/iso/19115/resources/Codelists/cat/codelists.xml#CI_PresentationFormCode",
                "codeListValue": self.presentationForm,
            },
        )

        return xml


class TemporalExtent(BaseModel):
    """
    XML serialisation:
    <mri:extent>
        <gex:EX_Extent>
            <gex:temporalElement>
                <gex:EX_TemporalExtent>
                    <gex:extent>
                    <gml:TimePeriod gml:id="A1234">
                        <gml:beginPosition>
                            {beginPosition_value}
                        </gml:beginPosition>
                        <gml:endPosition>
                            {endPosition_value}
                        </gml:endPosition>
                    </gml:TimePeriod>
                    </gex:extent>
                </gex:EX_TemporalExtent>
            </gex:temporalElement>
        </gex:EX_Extent>
    </mri:extent>

    Args:
        BaseModel (_type_): _description_

    Returns:
        _type_: _description_
    """

    beginPosition: str
    endPosition: str
    parent_element_xpath = ".//mri:MD_DataIdentification"

    def compose_xml(self):
        """Compose XML elements"""
        xml = ET.Element(f"{{{MRI}}}extent")
        ex_extent = ET.SubElement(xml, f"{{{GEX}}}EX_Extent")
        gex_temporal_element = ET.SubElement(ex_extent, f"{{{GEX}}}temporalElement")
        gex_temporal_extent = ET.SubElement(
            gex_temporal_element, f"{{{GEX}}}EX_TemporalExtent"
        )
        gex_extent = ET.SubElement(gex_temporal_extent, f"{{{GEX}}}extent")
        gml_time_period = ET.SubElement(
            gex_extent, f"{{{GML}}}TimePeriod", attrib={f"{{{GML}}}id": "A1234"}
        )
        gml_begin_position = ET.SubElement(gml_time_period, f"{{{GML}}}beginPosition")
        gml_end_position = ET.SubElement(gml_time_period, f"{{{GML}}}endPosition")
        gml_begin_position.text = self.beginPosition
        gml_end_position.text = self.endPosition

        return xml


class GeoExtent(BaseModel):
    """
    XML serialisation:
    <mri:extent>
        <gex:EX_Extent>
            <gex:geographicElement>
                <gex:EX_GeographicBoundingBox>
                    <gex:westBoundLongitude>
                        <gco:Decimal>{value}</gco:Decimal>
                    </gex:westBoundLongitude>
                    <gex:eastBoundLongitude>
                        <gco:Decimal>{value}</gco:Decimal>
                    </gex:eastBoundLongitude>
                    <gex:southBoundLatitude>
                        <gco:Decimal>{value}</gco:Decimal>
                    </gex:southBoundLatitude>
                    <gex:northBoundLatitude>
                        <gco:Decimal>{value}</gco:Decimal>
                    </gex:northBoundLatitude>
                </gex:EX_GeographicBoundingBox>
            </gex:geographicElement>
        </gex:EX_Extent>
    </mri:extent>

    Args:
        BaseModel (_type_): _description_

    Returns:
        _type_: _description_
    """

    westBoundLongitude: str
    eastBoundLongitude: str
    southBoundLatitude: str
    northBoundLatitude: str
    parent_element_xpath = ".//mri:MD_DataIdentification"

    def compose_xml(self):
        """Compose XML elements"""
        xml = ET.Element(f"{{{MRI}}}extent")
        ex_extent = ET.SubElement(xml, f"{{{GEX}}}EX_Extent")
        gex_geographic_element = ET.SubElement(ex_extent, f"{{{GEX}}}geographicElement")
        gex_geographic_bounding_box = ET.SubElement(
            gex_geographic_element, f"{{{GEX}}}EX_GeographicBoundingBox"
        )
        gex_west_bound_longitude = ET.SubElement(
            gex_geographic_bounding_box, f"{{{GEX}}}westBoundLongitude"
        )
        gco_west_value = ET.SubElement(gex_west_bound_longitude, f"{{{GCO}}}Decimal")
        gco_west_value.text = self.westBoundLongitude
        gex_east_bound_longitude = ET.SubElement(
            gex_geographic_bounding_box, f"{{{GEX}}}eastBoundLongitude"
        )
        gco_east_value = ET.SubElement(gex_east_bound_longitude, f"{{{GCO}}}Decimal")
        gco_east_value.text = self.eastBoundLongitude
        gex_south_bound_latitude = ET.SubElement(
            gex_geographic_bounding_box, f"{{{GEX}}}southBoundLatitude"
        )
        gco_south_value = ET.SubElement(gex_south_bound_latitude, f"{{{GCO}}}Decimal")
        gco_south_value.text = self.southBoundLatitude
        gex_north_bound_latitude = ET.SubElement(
            gex_geographic_bounding_box, f"{{{GEX}}}northBoundLatitude"
        )
        gco_north_value = ET.SubElement(gex_north_bound_latitude, f"{{{GCO}}}Decimal")
        gco_north_value.text = self.northBoundLatitude

        return xml


class Keyword(BaseModel):
    """
    XML serialisation:
    <mri:descriptiveKeywords>
        <mri:MD_Keywords>
            <mri:keyword>
                <gco:CharacterString>{keyword_value}</gco:CharacterString>
            </mri:keyword>
            <mri:type>
                <mri:MD_KeywordTypeCode
                    codeListValue={type_of_keyword_value}
                    codeList="http://standards.iso.org/iso/19115/resources/Codelists/cat/codelists.xml#MD_KeywordTypeCode"
                />
            </mri:type>
        </mri:MD_Keywords>
    </mri:descriptiveKeywords>

    Args:
        BaseModel (_type_): _description_

    Returns:
        _type_: _description_
    """

    value: str
    typeOfKeyword: str
    parent_element_xpath = ".//mri:MD_DataIdentification"

    def compose_xml(self):
        """Compose XML elements"""
        xml = ET.Element(f"{{{MRI}}}descriptiveKeywords")
        mri_md_keywords = ET.SubElement(xml, f"{{{MRI}}}MD_Keywords")
        mri_keyword = ET.SubElement(mri_md_keywords, f"{{{MRI}}}keyword")
        gco_character_string = ET.SubElement(mri_keyword, f"{{{GCO}}}CharacterString")
        gco_character_string.text = self.value
        mri_type = ET.SubElement(mri_md_keywords, f"{{{MRI}}}type")
        ET.SubElement(
            mri_type,
            f"{{{MRI}}}MD_KeywordTypeCode",
            attrib={
                "codeList": "http://standards.iso.org/iso/19115/resources/Codelists/cat/codelists.xml#MD_KeywordTypeCode",
                "codeListValue": self.typeOfKeyword,
            },
        )

        return xml


class AssociatedRessource(BaseModel):
    """
    XML serialisation:
    <mri:MD_DataIdentification>
        <mri:associatedResource>
            <mri:MD_AssociatedResource>
                <mri:associationType>
                    <mri:DS_AssociationTypeCode
                        codeList="http://standards.iso.org/iso/19115/resources/Codelists/cat/codelists.xml#DS_AssociationTypeCode"
                        codeListValue="{typeOfAssociation}"
                    />
                </mri:associationType>
                <mri:metadataReference uuidref="{value}" />
            </mri:MD_AssociatedResource>
        </mri:associatedResource>
    </mri:MD_DataIdentification>


    Args:
        BaseModel (_type_): _description_

    Returns:
        _type_: _description_
    """

    value: str
    typeOfAssociation: str
    parent_element_xpath = ".//mdb:identificationInfo"

    def compose_xml(self):
        """Compose XML elements"""
        xml = ET.Element(f"{{{MRI}}}MD_DataIdentification")
        mri_md_data_identification = ET.SubElement(xml, f"{{{MRI}}}associatedResource")
        mri_associated_resource = ET.SubElement(
            mri_md_data_identification, f"{{{MRI}}}MD_AssociatedResource"
        )
        mri_md_associated_resource = ET.SubElement(
            mri_associated_resource, f"{{{MRI}}}associationType"
        )
        ET.SubElement(
            mri_md_associated_resource,
            f"{{{MRI}}}DS_AssociationTypeCode",
            attrib={
                "codeList": "http://standards.iso.org/iso/19115/resources/Codelists/cat/codelists.xml#DS_AssociationTypeCode",
                "codeListValue": self.typeOfAssociation,
            },
        )
        ET.SubElement(
            mri_associated_resource,
            f"{{{MRI}}}metadataReference",
            attrib={"uuidref": self.value},
        )

        return xml


class DistributionInfo(BaseModel):
    """
    XML serialisation:
    <mdb:distributionInfo xmlns:geonet="http://www.fao.org/geonetwork">
        <mrd:MD_Distribution>
            <mrd:distributionFormat>
                <mrd:MD_Format>
                    <mrd:formatSpecificationCitation>
                        <cit:CI_Citation>
                            <cit:title>
                                <gco:CharacterString>{distributionFormat}</gco:CharacterString>
                            </cit:title>
                        </cit:CI_Citation>
                    </mrd:formatSpecificationCitation>
                </mrd:MD_Format>
            </mrd:distributionFormat>
            <mrd:transferOptions>
                <mrd:MD_DigitalTransferOptions>
                    <mrd:onLine>
                        <cit:CI_OnlineResource>
                            <cit:linkage>
                                <gco:CharacterString>{onlineResources_linkage}</gco:CharacterString>
                            </cit:linkage>
                            <cit:protocol>
                                <gco:CharacterString>{onlineResources_protocol}</gco:CharacterString>
                            </cit:protocol>
                            <cit:name>
                                <gco:CharacterString>{onlineResources_name}</gco:CharacterString>
                            </cit:name>
                            <cit:function>
                                <cit:CI_OnLineFunctionCode
                                    codeList="http://standards.iso.org/iso/19115/resources/Codelists/cat/codelists.xml#CI_OnLineFunctionCode"
                                    codeListValue="{onlineResources_typeOfTransferOption}"
                                />
                            </cit:function>
                        </cit:CI_OnlineResource>
                    </mrd:onLine>
                </mrd:MD_DigitalTransferOptions>
            </mrd:transferOptions>
        </mrd:MD_Distribution>
    </mdb:distributionInfo>


    Args:
        BaseModel (_type_): _description_

    Returns:
        _type_: _description_
    """

    distributionFormat: Optional[str]
    onlineResources: list = []
    # transferOptions: list  # FIXME Replaced by onlineResources ?
    parent_element_xpath = ".//mri:MD_DataIdentification"
    # In transferOptions:
    # - linkage
    # - protocol
    # - name
    # - typeOfTransferOption

    def compose_xml(self):
        """Compose XML elements"""
        xml = ET.Element(f"{{{MRD}}}MD_Distribution")
        mrd_distribution_format = ET.SubElement(xml, f"{{{MRD}}}distributionFormat")
        mrd_md_format = ET.SubElement(mrd_distribution_format, f"{{{MRD}}}MD_Format")
        mrd_format_specification_citation = ET.SubElement(
            mrd_md_format, f"{{{MRD}}}formatSpecificationCitation"
        )

        cit_ci_citation = ET.SubElement(
            mrd_format_specification_citation, f"{{{CIT}}}CI_Citation"
        )
        cit_title = ET.SubElement(cit_ci_citation, f"{{{CIT}}}title")
        gco_character_string = ET.SubElement(cit_title, f"{{{GCO}}}CharacterString")
        gco_character_string.text = self.distributionFormat

        mrd_transfer_options = ET.SubElement(xml, f"{{{MRD}}}transferOptions")
        mrd_md_digital_transfer_options = ET.SubElement(
            mrd_transfer_options, f"{{{MRD}}}MD_DigitalTransferOptions"
        )

        # Insert links to related online resources (WMS layers, images, websites and so on)
        for online_resource in self.onlineResources:
            mrd_online = ET.SubElement(
                mrd_md_digital_transfer_options, f"{{{MRD}}}onLine"
            )
            cit_ci_online_resource = ET.SubElement(
                mrd_online, f"{{{CIT}}}CI_OnlineResource"
            )

            cit_linkage = ET.SubElement(cit_ci_online_resource, f"{{{CIT}}}linkage")
            linkage_gco_character_string = ET.SubElement(
                cit_linkage, f"{{{GCO}}}CharacterString"
            )
            linkage_gco_character_string.text = online_resource["linkage"]

            cit_protocol = ET.SubElement(cit_ci_online_resource, f"{{{CIT}}}protocol")
            protocol_gco_character_string = ET.SubElement(
                cit_protocol, f"{{{GCO}}}CharacterString"
            )
            protocol_gco_character_string.text = online_resource["protocol"]

            cit_name = ET.SubElement(cit_ci_online_resource, f"{{{CIT}}}name")
            name_gco_character_string = ET.SubElement(
                cit_name, f"{{{GCO}}}CharacterString"
            )
            name_gco_character_string.text = online_resource["name"]

            online_function_code = online_resource["onlineFunctionCode"]
            if online_function_code:
                cit_function = ET.SubElement(
                    cit_ci_online_resource, f"{{{CIT}}}function"
                )
                cit_ci_online_function_code = ET.SubElement(
                    cit_function, f"{{{CIT}}}CI_OnLineFunctionCode"
                )
                cit_ci_online_function_code.text = online_function_code

        return xml


class ResourceLineage(BaseModel):
    """
    XML serialisation:
    <mrl:LI_Lineage>
        <mrl:source uuidref="{value}"
                    xlink:title="{title to fetch}"
        />
    </mrl:LI_Lineage>


    Args:
        BaseModel (_type_): _description_

    Returns:
        _type_: _description_
    """

    uuidref: str
    parent_element_xpath = ".//mdb:resourceLineage"

    # TO TEST
    # xlink:title disable for now
    # If geonetwork don't add it automatically
    # we need to fetch the record's title before we can add it
    def compose_xml(self):
        """Compose XML elements"""
        xml = ET.Element(f"{{{MRL}}}LI_Lineage")
        ET.SubElement(xml, f"{{{MRL}}}source", attrib={"uuidref": self.uuidref})

        return xml


class Stakeholders(BaseModel):
    """
    XML serialisation:
        <mri:pointOfContact>
            <cit:CI_Responsibility>
               <cit:role>
                  <cit:CI_RoleCode
                        codeList="http://standards.iso.org/iso/19115/resources/Codelists/cat/codelists.xml#CI_RoleCode"
                        codeListValue="{role}"
                    />
               </cit:role>
               <cit:party>
                  <cit:CI_Individual>
                     <cit:name>
                        <gco:CharacterString>{name}</gco:CharacterString>
                     </cit:name>
                  </cit:CI_Individual>
               </cit:party>
            </cit:CI_Responsibility>
         </mri:pointOfContact>


    Args:
        BaseModel (_type_): _description_

    Returns:
        _type_: _description_
    """

    role: str
    name: str
    parent_element_xpath = ".//mdb:identificationInfo/mri:MD_DataIdentification"

    def compose_xml(self):
        """Compose XML elements"""
        xml = ET.Element(f"{{{MRI}}}pointOfContact")
        cit_ci__responsibility = ET.SubElement(xml, f"{{{CIT}}}CI_Responsibility")
        cit_role = ET.SubElement(cit_ci__responsibility, f"{{{CIT}}}role")
        ET.SubElement(
            cit_role,
            f"{{{CIT}}}CI_RoleCode",
            attrib={
                "codeList": "http://standards.iso.org/iso/19115/resources/Codelists/cat/codelists.xml#CI_RoleCode",
                "codeListValue": self.role,
            },
        )
        cit_party = ET.SubElement(cit_ci__responsibility, f"{{{CIT}}}party")
        cit_ci_individual = ET.SubElement(cit_party, f"{{{CIT}}}CI_Individual")
        cit_name = ET.SubElement(cit_ci_individual, f"{{{CIT}}}name")
        gco_character_string = ET.SubElement(cit_name, f"{{{GCO}}}CharacterString")
        gco_character_string.text = self.name

        return xml


class Overview(BaseModel):
    """
    XML serialisation:
        <mri:graphicOverview>
            <mcc:MD_BrowseGraphic>
               <mcc:fileName>
                  <gco:CharacterString>{url}</gco:CharacterString>
               </mcc:fileName>
               <mcc:fileDescription>
                  <gco:CharacterString>Overview</gco:CharacterString>
               </mcc:fileDescription>
            </mcc:MD_BrowseGraphic>
        </mri:graphicOverview>

    Args:
        BaseModel (_type_): _description_

    Returns:
        _type_: _description_
    """

    url: str
    parent_element_xpath = ".//mri:MD_DataIdentification"

    def compose_xml(self):
        """Compose XML elements"""
        xml = ET.Element(f"{{{MRI}}}graphicOverview")
        mcc_md_browse_graphic = ET.SubElement(xml, f"{{{MCC}}}MD_BrowseGraphic")
        mcc_file_name = ET.SubElement(mcc_md_browse_graphic, f"{{{MCC}}}fileName")
        name_gco_character_string = ET.SubElement(
            mcc_file_name, f"{{{GCO}}}CharacterString"
        )
        name_gco_character_string.text = self.url

        mcc_file_description = ET.SubElement(
            mcc_md_browse_graphic, f"{{{MCC}}}fileDescription"
        )
        description_gco_character_string = ET.SubElement(
            mcc_file_description, f"{{{GCO}}}CharacterString"
        )
        description_gco_character_string.text = "Overview"

        return xml


class IsoDocumentBuilder:
    """The main XML sheet"""

    __template_path__ = XML_TEMPLATE

    def __init__(self, data_dict: dict) -> None:
        self.data_dict = data_dict
        self.postponed = defaultdict(list)
        self.postponed["uuid"] = self.data_dict["identifier"]

    @staticmethod
    def load_all(yaml_multidoc) -> List["IsoDocumentBuilder"]:
        """Load all yaml documents present in file"""
        doc_dicts = yaml.load_all(yaml_multidoc)
        for data in doc_dicts:
            yield IsoDocumentBuilder(data)

    def _is_valid_uuid(self, uuid_to_test: uuid.uuid4):
        try:
            uuid_obj = uuid.UUID(uuid_to_test, version=4)
        except ValueError:
            return False
        return str(uuid_obj) == uuid_to_test

    def return_xml(self):
        """Indent XML for better indentation and print the result"""
        ET.indent(self)
        ET.dump(self)

    def _make_xml_element(self, factory: type, **kwargs) -> ET.Element:
        return factory(**kwargs).compose_xml()

    def _insert_xml(
        self, insert_point: str, doc: ET.ElementTree, element: ET.Element
    ) -> None:
        parent_element = doc.find(insert_point, PREFIX_MAP)
        parent_element.append(element)

    def compose_xml(self):
        """Build XML file from a yaml document"""
        xml = ET.parse(self.__class__.__template_path__)

        # Register every XML namespace used in ISO19115
        for namespace, uri in PREFIX_MAP.items():
            ET.register_namespace(namespace, uri)

        # -- BLock MD_DataIdentification --

        # Create and insert the TITLE element
        if "title" in self.data_dict:
            title_data = self.data_dict.get("title")
            title_element = Title(title=title_data)
            self._insert_xml(
                title_element.parent_element_xpath, xml, title_element.compose_xml()
            )

        # Create and insert the DATE element
        if "date" in self.data_dict:
            date_data = self.data_dict.get("date")
            for event in date_data:
                date_element = Date(**event)
                self._insert_xml(
                    date_element.parent_element_xpath, xml, date_element.compose_xml()
                )

        # Create and insert the PRESENTATIONFORM element
        if "presentationForm" in self.data_dict:
            presentation_data = self.data_dict.get("presentationForm")
            pform_element = PresentationForm(presentationForm=presentation_data)
            self._insert_xml(
                pform_element.parent_element_xpath, xml, pform_element.compose_xml()
            )

        # Create and insert the TEMPORALEXTENT element
        if "extent" in self.data_dict and "temporalExtent" in self.data_dict["extent"]:
            data = self.data_dict.get("extent")
            tempextent_element = TemporalExtent(**data["temporalExtent"])
            self._insert_xml(
                tempextent_element.parent_element_xpath,
                xml,
                tempextent_element.compose_xml(),
            )

        # Create and insert the GEOEXTENT element
        if "extent" in self.data_dict and "geoExtent" in self.data_dict["extent"]:
            data = self.data_dict.get("extent")
            geoextent_element = GeoExtent(**data["geoExtent"])
            self._insert_xml(
                geoextent_element.parent_element_xpath,
                xml,
                geoextent_element.compose_xml(),
            )

        # Create and insert the KEYWORD elements
        if "keywords" in self.data_dict:
            data = self.data_dict.get("keywords")
            for keyword in data:
                keyword_element = Keyword(**keyword)
                self._insert_xml(
                    keyword_element.parent_element_xpath,
                    xml,
                    keyword_element.compose_xml(),
                )

        # Create and insert the ASSOCIATEDRESSOURCE elements
        if "associatedResource" in self.data_dict:
            data = self.data_dict.get("associatedResource")
            for resource in data:
                if self._is_valid_uuid(resource["value"]):
                    associated_resource_element = AssociatedRessource(**resource)
                    self._insert_xml(
                        associated_resource_element.parent_element_xpath,
                        xml,
                        associated_resource_element.compose_xml(),
                    )
                else:
                    self.postponed["associatedResource"].append(resource)

        # Create and insert the STAKEHOLDERS elements
        if "stakeholders" in self.data_dict:
            data = self.data_dict.get("stakeholders")
            for stakeholder in data:
                stakeholder_element = Stakeholders(**stakeholder)
                self._insert_xml(
                    stakeholder_element.parent_element_xpath,
                    xml,
                    stakeholder_element.compose_xml(),
                )

        # Create and insert the OVERVIEW element
        if "overview" in self.data_dict:
            url_data = self.data_dict.get("overview")
            overview_element = Overview(url=url_data)
            self._insert_xml(
                overview_element.parent_element_xpath,
                xml,
                overview_element.compose_xml(),
            )

        # -- BLock MD_Distribution --

        # Create and insert the DISTRIBUTIONINFO elements
        if "distributionInfo" in self.data_dict:
            data = self.data_dict.get("distributionInfo")
            for distribution in data:
                distribution_info_element = DistributionInfo(**distribution)
                self._insert_xml(
                    distribution_info_element.parent_element_xpath,
                    xml,
                    distribution_info_element.compose_xml(),
                )

        # -- BLock resourceLineage --

        # Create and insert the RESOURCELINEAGE elements
        if "resourceLineage" in self.data_dict:
            relations = self.data_dict.get("resourceLineage")
            for relation in relations:
                if self._is_valid_uuid(relation):
                    resource_info_element = ResourceLineage(uuidref=relation)
                    self._insert_xml(
                        resource_info_element.parent_element_xpath,
                        xml,
                        resource_info_element.compose_xml(),
                    )
                else:
                    self.postponed["resourceLineage"].append(relation)

        return xml
