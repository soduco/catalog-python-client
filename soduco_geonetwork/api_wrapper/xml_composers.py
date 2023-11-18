"""System module."""
import collections
import json
import os
import sys
import uuid
import warnings
import re
from typing import Any, ClassVar, Union
from collections import defaultdict
from lxml import etree as ET

RECORD_DOCUMENT_TEMPLATE_PATH = (
    os.path.dirname(__file__) + "/xmltemplates/dataset_iso19115.xml"
)

"""
register_namespaces() method isn't sufficient alone.
We have to use namespace url when creating an Element.

For example we want to create the element <gml:beginPosition> :
ET.Element("{http://www.opengis.net/gml/3.2}beginPosition")

Lineage relations to non-yet uploaded resources are postponed
If the value isn't an UUID, then it's a local file.
In this case, we save the file name in a dictionnary "self.postponed".
We will have to resolve the relations IDs before exporting the dictionnary
"""

NAMESPACES = {
    "mdb": "http://standards.iso.org/iso/19115/-3/mdb/2.0",
    "cat": "http://standards.iso.org/iso/19115/-3/cat/1.0",
    "gfc": "http://standards.iso.org/iso/19110/gfc/1.1",
    "cit": "http://standards.iso.org/iso/19115/-3/cit/2.0",
    "gcx": "http://standards.iso.org/iso/19115/-3/gcx/1.0",
    "gex": "http://standards.iso.org/iso/19115/-3/gex/1.0",
    "lan": "http://standards.iso.org/iso/19115/-3/lan/1.0",
    "srv": "http://standards.iso.org/iso/19115/-3/srv/2.1",
    "mas": "http://standards.iso.org/iso/19115/-3/mas/1.0",
    "mcc": "http://standards.iso.org/iso/19115/-3/mcc/1.0",
    "mco": "http://standards.iso.org/iso/19115/-3/mco/1.0",
    "mda": "http://standards.iso.org/iso/19115/-3/mda/1.0",
    "mds": "http://standards.iso.org/iso/19115/-3/mds/2.0",
    "mdt": "http://standards.iso.org/iso/19115/-3/mdt/2.0",
    "mex": "http://standards.iso.org/iso/19115/-3/mex/1.0",
    "mmi": "http://standards.iso.org/iso/19115/-3/mmi/1.0",
    "mpc": "http://standards.iso.org/iso/19115/-3/mpc/1.0",
    "mrc": "http://standards.iso.org/iso/19115/-3/mrc/2.0",
    "mrd": "http://standards.iso.org/iso/19115/-3/mrd/1.0",
    "mri": "http://standards.iso.org/iso/19115/-3/mri/1.0",
    "mrl": "http://standards.iso.org/iso/19115/-3/mrl/2.0",
    "mrs": "http://standards.iso.org/iso/19115/-3/mrs/1.0",
    "msr": "http://standards.iso.org/iso/19115/-3/msr/2.0",
    "mdq": "http://standards.iso.org/iso/19157/-2/mdq/1.0",
    "mac": "http://standards.iso.org/iso/19115/-3/mac/2.0",
    "gco": "http://standards.iso.org/iso/19115/-3/gco/1.0",
    "gml": "http://www.opengis.net/gml/3.2",
    "xlink": "http://www.w3.org/1999/xlink",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}

# Register every XML namespace used in a GeoNetwork record document.
for namespace, uri in NAMESPACES.items():
    ET.register_namespace(namespace, uri)


class RecordDocumentBuilder:
    """Build a Geonetwork record document in XML format.

    Building a document starts from a base document template
    and applies `XMLComposer` objects to enrich it step by step.
    `XMLComposers` are in charge of generating a block of XML that can be inserted
    at a specific location in an XML document.

    This class also provide the method `process_data_tree()` to automatically create the list of composers
    for a Geonetork record represented as a dictionary, typically parsed from a YAML document.

    Calling the method `build()` will trigger the actual composition of the XML record.
    """

    __document_template__: str = RECORD_DOCUMENT_TEMPLATE_PATH

    def __init__(self) -> None:
        """Create a new builder.

        At init stage, a builder holds an XML tree loaded from the template document `__document_template__`.
        """
        self.deferred_processing = defaultdict(list)
        self.record_doc = ET.parse(self.__document_template__)
        self._composers = []
        self._constructed = False

    def build(self) -> ET._ElementTree:
        """Trigger building and return the XML record document.

        Building is done by applying the sequence of registered composers to the base XML template.

        Builders are not reusable, meaning that calling `build()` on the same builder object will raise
        an exception.

        Important notes
        -------
        In some cases (e.g. associated resources), information for specific fields may not be available
        at this stage but instead requires the record to be pushed to a GeoNetwork instance first.
        Affected composers are then applied and added to the `self.deferred_processing` dictionary,
        making them available for further processing.
        """
        if self._constructed:
            raise ValueError("The builder has already been used")

        for composer in self._composers:
            new_element = composer.compose()

            # New XML elements can be duplicated and inserted at multiple points
            #  in the xml_document depending on the parent_xpath expression.
            insertion_points = self.record_doc.xpath(
                composer.parent_xpath, namespaces=NAMESPACES
            )
            for point in insertion_points:
                if composer.before:
                    subElement = point.find(composer.before, namespaces=NAMESPACES)
                    index = point.index(subElement)
                    point.insert(index, new_element)
                elif composer.after:
                    subElement = point.find(composer.after, namespaces=NAMESPACES)
                    index = point.index(subElement)
                    point.insert(index + 1, new_element)
                else:
                    point.append(new_element)
                
        self._constructed = True
        return self.get()

    def process_data_tree(self, data_tree: dict[str, Any]) -> "RecordDocumentBuilder":
        """Register the composers required to build the XML representation of a record document
        stored as a Python dictionary.

        The data tree is processed so its nodes are mapped to specific XML composers that are in charge
        of enriching the initial XML template with new elements.
        The result should be a valid GeoNetwork record document, however no validation is done here.

        Important notes
        -------
        1. This method expects `data_tree` to be a dictionary that defines a tree structure where:
            - keys are strings and correspond to a node;
            - values contain the children of that node.
                List-like and dictionary values are sub-trees, any other types are treated as leafs.
        2. Finding the relevant composer for a node in the data tree heavily relies on naming.
        If a composer should apply to a node then the dictionary key **must** have the same name as the composer.
        However, the first letter can be lowercase or uppercase to accommodate YAML naming conventions.
        """

        # FIXME: move this in build() or add_composer() ? Problem : we don't know the `node` anymore in build().
        self.deferred_processing["uuid"] = data_tree["identifier"]

        # Compositing the record document is made by traversing `data_tree` depth-first
        #  and applying a composer to each node.
        # Each composer produces an XML partial which is inserted in the record template
        #  at a location specified by the composer.
        # Every node will be visited unless one of this node's parent has is mapped to a *leaf* composer.
        # See @Iso19115Element.is_leaf_composer() for more information.
        stack = [(k, v) for k, v in data_tree.items()]
        while stack:
            node, subtree = stack.pop(0)

            # Compositing applies to each element of list-like nodes.
            if is_list_like(subtree):
                stack = [(node, e) for e in subtree] + stack
                continue

            # The name of the composer class to instantiate is formed by the current key
            #  with the first letter capitalized.
            # We assumes that keys are strings either in PascalCase or CamelCase,
            #  as classes names usually are in PascalCase.
            try:
                composer_cls = str_to_composer_cls(node)
            except AttributeError:
                warnings.warn(
                    f"No XML composer found for the key `{node}` in the module {__name__}. "
                    f"A class named `{node}` was expected."
                    f"This is a non-blocking error, compositing can continue but output XML \
                        might be invalid."
                )
                composer = None
            else:
                composer = composer_cls(subtree)
                self.add_composer(composer)

                # Composers that need deferred processing are retained and made accessible to external code.
                # This is required for batch-uploads when documents to push to GeoNetwork reference each others.
                # Because relationships between resources use the resource's uuid assigned by GeoNetwork,
                #  all documents have to be pushed before their uuids can be retrieved to update the relationships
                # FIXME: move this in build() or add_composer() ? Problem : we don't know the `node` anymore in build().
                if composer.is_deferred_processing():
                    self.deferred_processing[node].append(composer.parameters)
            finally:
                # If the traversed entry is a sub-tree, we want to visit it
                #  unless the composer takes care of creating XML content for the entire sub-tree.
                if isinstance(subtree, dict):
                    if not composer or not composer.is_leaf_composer():
                        children = [(k, v) for k, v in subtree.items()]
                        stack = children + stack
        return self

    def get(self) -> ET._ElementTree:
        """Return the record document in its current state."""
        return self.record_doc

    def add_composer(self, composer: "XMLComposer") -> "RecordDocumentBuilder":
        """Append a new composer to the build chain."""
        self._composers.append(composer)
        return self


def insert_namespace(xml_string: str) -> str:
    xmlns = " ".join(f'xmlns:{ns}="{url}"' for ns, url in NAMESPACES.items())
    namespaced = re.sub(
        r"<(.+?)>", r"<\1 {xmlns}>".format(xmlns=xmlns), xml_string, count=1
    )
    return namespaced


def load_element_template(cls: str) -> str:
    here = os.path.dirname(__file__)
    path = f"{here}/../xml/partials/{cls.__name__.lower()}.xml"
    with open(path, "r") as t:
        return t.read()


def is_valid_uuid(uuid_: uuid.uuid4):
    try:
        uuid_obj = uuid.UUID(uuid_, version=4)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_


class XMLComposer:
    template: ClassVar[ET.ElementTree] = ""
    insertion_points: ClassVar[dict[str, Union[str, tuple[str, str]]]] = {}
    parent_xpath: ClassVar[str] = "./"
    before:ClassVar[str] = None
    after:ClassVar[str] = None

    """
    The default behavior of a RecordDocumentBuilder is to traverse a record tree depth-first
    and apply a composer to every node.
    However, composers are often responsible for entire part of a GeoNetwork XML record and
    visiting the children of a node mapped to such composer is not desired.

    Setting a composer as *leaf* will prevent a RecordDocumentBuilder to visit the descendants
    of the node mapped to this composer in a record tree.
    In short, if you create a new composer class that creates XML for a entire sub-tree of a record tree into XML,
    make it a leaf.
    """
    is_leaf: bool = True

    def __new__(cls, *args) -> "XMLComposer":
        try:
            template = load_element_template(cls)
            xml_element = insert_namespace(template)
            obj = super(XMLComposer, cls).__new__(cls)
            # print(f"template={template}")
            # print(f"xml_element={xml_element}")
            obj.xml_element = ET.fromstring(xml_element)
            obj.deferred_id = None
            obj.parameters = {}
            return obj
        except FileNotFoundError as e:
            raise ValueError(f"Empty XML template for {cls}") from e

    def __init__(self, *args) -> None:
        """Create a new GeoNetwork record composer in charge of the generation of a part of a XML record document."""
        pass

    def compose(self) -> ET._Element:
        for k, v in self.parameters.items():
            point = self.insertion_points[k]
            # If point is a tuple it means that the insertion point is an attribute.
            if isinstance(point, tuple):
                xpath_expr, attr = point
            else:
                xpath_expr, attr = point, None

            matches = self.xml_element.xpath(xpath_expr, namespaces=NAMESPACES)

            if not matches:
                raise ValueError(f"Could not locate {k} at {v} in {self}")

            for m in matches:
                if attr:
                    m.set(attr, v)
                else:
                    m.text = v
        return self.xml_element

    def is_deferred_processing(self) -> bool:
        """Does this composer require post-processing ?"""
        return bool(self.deferred_id)

    def is_leaf_composer(self) -> bool:
        """Does this composer apply to a whole sub-tree instead of on a single node ?"""
        return self.is_leaf

    def toJSON(self) -> str:
        return json.dumps(self.parameters)

    def __str__(self) -> str:
        """Return the composed XML element in string format."""
        return ET.tostring(self.xml_element, pretty_print=True).decode()

    def __repr__(self) -> str:
        """Return the rendered XML document in string format."""
        return self.xml_element


class Identifier(XMLComposer):
    """Generate a uuid5 from the yaml identifier
    """
    insertion_points = {
        "uuid" : "//mcc:code/gco:CharacterString"
    }

    parent_xpath = "./mdb:metadataIdentifier"

    def __init__(self, record_tree) -> None:
        self.parameters = {
            "uuid": str(uuid.uuid5(uuid.NAMESPACE_X500, record_tree))
        }


class Identification(XMLComposer):
    insertion_points = {
        "title": "//cit:title/gco:CharacterString"
    }
    parent_xpath = "./mdb:identificationInfo/mri:MD_DataIdentification"

    def __init__(self, record_tree: str) -> None:
        self.parameters = {
            "title": record_tree["title"]
        }


class Abstract(XMLComposer):
    insertion_points = {
        "abstract": "//mri:abstract/gco:CharacterString"
    }
    parent_xpath = "./mdb:identificationInfo/mri:MD_DataIdentification"

    def __init__(self, record_tree: str) -> None:
        self.parameters = {
            "abstract": record_tree
        }


class SpatialResolution(XMLComposer):
    insertion_points = {
        "spatial_resolution": "//mri:denominator/gco:Integer"
    }
    parent_xpath = "./mdb:identificationInfo/mri:MD_DataIdentification/mri:spatialResolution"

    def __init__(self, record_tree: str) -> None:
        self.parameters = {
            "spatial_resolution": record_tree
        }


class Scope(XMLComposer):
    insertion_points = {
        "scope": (
            "//mdb:metadataScope/mdb:MD_MetadataScope/mdb:resourceScope/mcc:MD_ScopeCode",
            "codeListValue",
        )
    }
    parent_xpath = "."

    def __init__(self, record_tree: str) -> None:
        self.parameters = {
            "scope": record_tree
        }


class Events(XMLComposer):
    insertion_points = {
        "date": "//cit:date/gco:Date",
        "event_type": (
            "//cit:dateType/cit:CI_DateTypeCode",
            "codeListValue",
        ),
    }
    parent_xpath = "./mdb:identificationInfo/mri:MD_DataIdentification/mri:citation/cit:CI_Citation"

    def __init__(self, record_tree: dict) -> None:
        self.parameters = {
            "date": record_tree["value"],
            "event_type": record_tree["event"],
        }


class PresentationForm(XMLComposer):
    insertion_points = {
        "presentation_format": (
            "//cit:CI_PresentationFormCode",
            "codeListValue",
        ),
    }
    parent_xpath = "./mdb:identificationInfo/mri:MD_DataIdentification/mri:citation/cit:CI_Citation"

    def __init__(self, record_tree: str) -> None:
        self.parameters = {"presentation_format": record_tree}


class Extent(XMLComposer):
    insertion_points = {}
    parent_xpath = "./mdb:identificationInfo/mri:MD_DataIdentification"

    # We want the document builder to visit children of "Extent" nodes in a record tree.
    is_leaf = False


class TemporalExtent(XMLComposer):
    insertion_points = {
        "begin_position": "//gml:beginPosition",
        "end_position": "//gml:endPosition",
    }
    parent_xpath = (
        "./mdb:identificationInfo/mri:MD_DataIdentification/mri:extent/gex:EX_Extent"
    )

    def __init__(self, record_tree: dict) -> None:
        self.parameters = {
            "begin_position": record_tree["beginPosition"],
            "end_position": record_tree["endPosition"],
        }


class GeoExtent(XMLComposer):
    insertion_points = {
        "westbound_longitude": ".//gex:westBoundLongitude/gco:Decimal",
        "eastbound_longitude": ".//gex:eastBoundLongitude/gco:Decimal",
        "southbound_latitude": ".//gex:southBoundLatitude/gco:Decimal",
        "northbound_latitude": ".//gex:northBoundLatitude/gco:Decimal",
    }
    parent_xpath = (
        "./mdb:identificationInfo/mri:MD_DataIdentification/mri:extent/gex:EX_Extent"
    )

    def __init__(self, record_tree: dict) -> None:
        self.parameters = {
            "westbound_longitude": record_tree["westBoundLongitude"],
            "eastbound_longitude": record_tree["eastBoundLongitude"],
            "southbound_latitude": record_tree["southBoundLatitude"],
            "northbound_latitude": record_tree["northBoundLatitude"],
        }


class Keywords(XMLComposer):
    insertion_points = {
        "keyword": "//mri:keyword/gco:CharacterString",
        "keyword_type": ("//mri:type/mri:MD_KeywordTypeCode", "codeListValue"),
    }
    parent_xpath = "./mdb:identificationInfo/mri:MD_DataIdentification"

    def __init__(self, record_tree: dict) -> None:
        self.parameters = {
            "keyword": record_tree["value"],
            "keyword_type": record_tree["typeOfKeyword"] # "place",  # FIXME hardcoded placeholder value
        }


class AssociatedResource(XMLComposer):
    insertion_points = {
        "value": ("//mri:metadataReference", "uuidref"),
        "typeOfAssociation": (
            "//mri:associationType/mri:DS_AssociationTypeCode",
            "codeListValue",
        ),
    }
    parent_xpath = "./mdb:identificationInfo/mri:MD_DataIdentification"

    def __init__(self, record_tree: dict) -> None:
        self.parameters = {
            "value": record_tree["value"],
            "typeOfAssociation": record_tree["typeOfAssociation"],
        }

        should_defer_id = not is_valid_uuid(self.parameters["value"])
        if should_defer_id:
            self.deferred_id = self.parameters["value"]

# TODO Merge with Organisations and Individuals builders
# Distributor is an Individual or ogranisation with fixed "role" value
class DistributionInfo(XMLComposer):
    insertion_points = {
        "distributor": "//cit:CI_Organisation/cit:name/gco:CharacterString",
        "mail": "//cit:electronicMailAddress/gco:CharacterString",
        "distributor_logo": "//cit:logo//mcc:fileName/gco:CharacterString",
    }
    parent_xpath = "."

    # DistributionInfo is typically composed of one or several OnlineResources
    is_leaf = False

    def __init__(self, record_tree: dict) -> None:
        self.parameters = {
            "distributor": record_tree["distributor"],
            "mail": record_tree["distributor_mail"],
        }
        if "distributor_logo" in record_tree and record_tree["distributor_logo"] is not None:
            self.parameters.update({"distributor_logo": record_tree["distributor_logo"]})

class DistributionFormat(XMLComposer):
    insertion_points = {
        "distribution_format": "//mrd:formatSpecificationCitation/cit:CI_Citation/cit:title/gco:CharacterString",
    }
    # parent_xpath = "./mdb:identificationInfo/mri:MD_DataIdentification/mdb:distributionInfo/mrd:MD_Distribution"
    parent_xpath = "./mdb:distributionInfo/mrd:MD_Distribution/mrd:distributionFormat"

    def __init__(self, record_tree: dict) -> None:
        self.parameters = {"distribution_format": record_tree}


class OnlineResources(XMLComposer):
    insertion_points = {
        "linkage": "//cit:CI_OnlineResource/cit:linkage/gco:CharacterString",
        "protocol": "//cit:CI_OnlineResource/cit:protocol/gco:CharacterString",
        "name": "//cit:CI_OnlineResource/cit:name/gco:CharacterString",
        "type": (
            "//cit:CI_OnlineResource/cit:function/cit:CI_OnLineFunctionCode",
            "codeListValue",
        ),
        "description": "//cit:CI_OnlineResource/cit:description/gco:CharacterString",
    }

    #parent_xpath = "./mdb:identificationInfo/mri:MD_DataIdentification/mdb:distributionInfo/mrd:MD_Distribution/mrd:transferOptions/mrd:MD_DigitalTransferOptions"
    parent_xpath = "./mdb:distributionInfo/mrd:MD_Distribution/mrd:transferOptions/mrd:MD_DigitalTransferOptions"

    def __init__(self, record_tree: dict) -> None:
        self.parameters = {
            "linkage": record_tree["linkage"],
            "protocol": record_tree["protocol"],
            "name": record_tree["name"],
            "type": record_tree["onlineFunctionCode"],
        }

        if "description" in record_tree and record_tree["description"] is not None:
            self.parameters.update({"description": record_tree["description"]})


class Individuals(XMLComposer):
    insertion_points = {
        "name": "//cit:CI_Individual/cit:name/gco:CharacterString",
        "role": ("//cit:role/cit:CI_RoleCode", "codeListValue"),
    }

    parent_xpath = "./mdb:identificationInfo/mri:MD_DataIdentification/mri:associatedResource"

    # Individuals may have a PartyIdentifier
    is_leaf = False

    def __init__(self, record_tree: dict) -> None:
        self.parameters = {
            "name": record_tree["name"],
            "role": record_tree["role"],
        }


class Organisations(XMLComposer):
    insertion_points = {
        "name": "//cit:CI_Organisation/cit:name/gco:CharacterString",
        "role": ("//cit:role/cit:CI_RoleCode", "codeListValue"),
        "mail": "//cit:electronicMailAddress/gco:CharacterString",
        "logo": "//cit:logo//mcc:fileName/gco:CharacterString",
    }

    parent_xpath = "./mdb:identificationInfo/mri:MD_DataIdentification"

    # Organisations may have a PartyIdentifier
    is_leaf = False

    def __init__(self, record_tree: dict) -> None:
        self.parameters = {
            "name": record_tree["name"],
            "role": record_tree["role"],
            "mail": record_tree["mail"],
        }
        if "logo" in record_tree and record_tree["logo"] is not None:
            self.parameters.update({"logo": record_tree["logo"]})

class PartyIdentifier(XMLComposer):
    insertion_points = {
        "authority_name": "//mcc:authority//cit:title/gco:CharacterString",
        "code": "//mcc:code/gco:CharacterString",
        "codespace": "//mcc:codeSpace/gco:CharacterString",
    }

    parent_xpath = ".//mri:pointOfContact/cit:CI_Responsibility/cit:party/*"

    def __init__(self, record_tree: dict) -> None:
        self.parameters = {
            "authority_name": record_tree["authority_name"],
            "code": record_tree["code"],
            "codespace": record_tree["codespace"],
        }

class Overview(XMLComposer):
    insertion_points = {
        "overview": "//mcc:fileName/gco:CharacterString",
    }
    parent_xpath = "./mdb:identificationInfo/mri:MD_DataIdentification"

    def __init__(self, record_tree: str) -> None:
        self.parameters = {"overview": record_tree}


class ResourceLineage(XMLComposer):
    # In mrl:source, attribute xlink:title should (#TODO verify ?) be inserted automatically by GeoNetwork.
    insertion_points = {
        "value": ("//mrl:source", "uuidref"),
    }

    parent_xpath = ".//mrl:LI_Lineage"#./mdb:resourceLineage/mrl:LI_Lineage

    def __init__(self, record_tree: str) -> None:
        self.parameters = {"value": record_tree}
        should_defer_id = not is_valid_uuid(self.parameters["value"])
        if should_defer_id:
            self.deferred_id = self.parameters["value"]


class ProcessStep(XMLComposer):
    insertion_points = {
        "description": "//mrl:LE_ProcessStep/mrl:description/gco:CharacterString",
        "title": "//mrl:LE_ProcessStep/mrl:reference//cit:title/gco:CharacterString",
        "processingIdentifier": "//mrl:LE_ProcessStep/mrl:reference//cit:identifier//mcc:code/gco:CharacterString",
        "typeOfActivity": "//mrl:LE_Processing/mrl:identifier/mcc:MD_Identifier/mcc:code/gco:CharacterString",
        "softwareTitle": "//mrl:softwareReference//cit:title/gco:CharacterString",
        "softwareIdentifier": "//mrl:softwareReference//mcc:MD_Identifier/mcc:code/gco:CharacterString"
    }

    parent_xpath = "./mdb:resourceLineage/mrl:LI_Lineage"

    # ProcessStep is typically composed of one or several ProcessStepSource and ProcessStepOutput
    is_leaf = False

    # Pour l'instant, template renseigne le processor comme étant soduco. Permettre le choix ?
    def __init__(self, record_tree: str) -> None:
        self.parameters = {
            "description": record_tree["description"],
            "title": record_tree["title"],
            "processingIdentifier": record_tree["processingIdentifier"],
            "typeOfActivity": record_tree["typeOfActivity"],
            "softwareTitle": record_tree["softwareTitle"],
            "softwareIdentifier": record_tree["softwareIdentifier"],
        }


class ProcessStepSource(XMLComposer):
    insertion_points = {
        "description": "//mrl:LI_Source/mrl:description/gco:CharacterString",
        "title": "//mrl:sourceCitation//cit:title/gco:CharacterString",
        "identifier": "//mrl:sourceCitation//mcc:MD_Identifier/mcc:code/gco:CharacterString",
        "url": "//cit:onlineResource//cit:linkage/gco:CharacterString"
    }

    parent_xpath = "./mdb:resourceLineage/mrl:LI_Lineage/mrl:processStep/mrl:LE_ProcessStep"
    before = "./mrl:processingInformation"

    def __init__(self, record_tree: str) -> None:
        self.parameters = {
            "description": record_tree["description"],
            "title": record_tree["title"],
            "identifier": record_tree["identifier"],
            "url": record_tree["url"]
        }


class ProcessStepOutput(XMLComposer):
    insertion_points = {
        "description": "//mrl:LE_Source/mrl:description/gco:CharacterString",        
        "title": "//mrl:sourceCitation//cit:title/gco:CharacterString",
        "identifier": "//mrl:sourceCitation//mcc:MD_Identifier/mcc:code/gco:CharacterString",
        "url": "//cit:onlineResource//cit:linkage/gco:CharacterString"
    }

    parent_xpath = "./mdb:resourceLineage/mrl:LI_Lineage/mrl:processStep/mrl:LE_ProcessStep"
    after = "./mrl:processingInformation"

    def __init__(self, record_tree: str) -> None:
        self.parameters = {
            "description": record_tree["description"],
            "title": record_tree["title"],
            "identifier": record_tree["identifier"],
            "url": record_tree["url"]
        }


###
# Helper functions
###
# TODO: the warning is currently raised for elements inside a builder if it has a sub-builder. It shouldn't.
def str_to_composer_cls(tree_node: str) -> type:
    """Return a composer class for a record tree node.

    This function tries to instanciates a sublclass of Iso19115Element from this module
    whose name is the same as the YAML key, with the first letter capitalized.
    An AttributeError is raised if the class does not exist.
    """
    class_name = tree_node[0].upper() + tree_node[1:]
    class_ = getattr(sys.modules[__name__], class_name)

    if class_ == "Iso19115Element":
        warnings.warn(
            f"You tried to create a {class_} object"
            " but this class is not meant to be instanciated directly.",
            UserWarning,
        )
    assert issubclass(class_, XMLComposer)
    return class_


def is_list_like(obj: Any) -> bool:
    """Return True if `obj` is list-like (i.e. a `collections.abc.Iterable`)
    but neither a string, bytes nor a dictionary."""
    return isinstance(obj, collections.abc.Iterable) and not isinstance(
        obj, (str, bytes, dict)
    )
