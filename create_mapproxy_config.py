#!/usr/bin/env python3

import json
import logging
import pandas
import yaml


def main():
    logging.basicConfig(level="INFO")
    logging.info("START")
    with open('../geonetwork-resources/verniquet/extents.yaml', 'r') as extent_file:
        data = yaml.safe_load(extent_file)
    dataverse = json.loads(open('../geonetwork-resources/verniquet/dataverse.harvard.edu.json').read())
    dataverse_data_file_url = "https://dataverse.harvard.edu/api/access/datafile/"
    dataverse_links = {}
    def create_dictionary():
        for e in dataverse["data"]["latestVersion"]["files"]:
            dataverse_label:str = e["label"]
            if dataverse_label.endswith(".json"):
                dataverse_directory_label:str = e["directoryLabel"]
                if dataverse_directory_label.__contains__("/"):
                    sheet = int(dataverse_directory_label.split("/")[1])
                    if dataverse_directory_label.startswith("davidrumsey"):
                        key = f"verniquet_stanford_{sheet}"
                    else:
                        key = f"verniquet_bnf_{sheet}"
                else:
                    if dataverse_directory_label.startswith("davidrumsey"):
                        key = f"verniquet_stanford"
                    else:
                        key = f"verniquet_bnf"
                dataverse_file_id = e["dataFile"]["id"]
                logging.debug(f"json found: {dataverse_file_id}")
                link = dataverse_data_file_url + str(dataverse_file_id)
                dataverse_links[key] = link
    create_dictionary()
    layers = []
    caches = {}
    sources = {}
    #parisExtent = [2.2789487344052968,48.8244731921314568,2.4080435114903960,48.8904078536729116]
    parisExtent = [2.2182,48.8074,2.4757,48.9103]
    def create_entries(version, version_start):
        list = pandas.read_csv(f"../geonetwork-resources/verniquet_{version}/yaml_list.csv")
        for index, row in list.iterrows():
            uuid = row["geonetwork_uuid"]
            if (index > version_start):
                sheet = index -version_start
                wms = f"verniquet_{version}_{sheet}"
                wms_cache = f"{wms}_cache"
                wms_source = f"{wms}_tms"
                file=dataverse_links[wms]
                extent = data[sheet]['geoExtent']
                xmin,ymin,xmax,ymax=float(extent["westBoundLongitude"]),float(extent["southBoundLatitude"]),float(extent["eastBoundLongitude"]),float(extent["northBoundLatitude"])
                logging.info(f"Row {index} = Sheet{sheet} => {uuid} => {wms}")
                layers.append({
                    "name": wms,
                    "title": f"Atlas du plan general de la ville de Paris, feuille {sheet} [Exemplaire {version}]",
                    "sources": [wms_cache]
                })
                caches.update({
                    wms_cache: {
                        "grids": ["webmercator"],
                        "sources": [wms_source]
                    }
                })
                sources.update({
                    wms_source: {
                        "type": "tile",
                        "grid": "webmercator",
                        "url": f"https://allmaps.xyz/%(z)s/%(x)s/%(y)s.png?url={file}",
                        "coverage":{
                            "bbox": [xmin,ymin,xmax,ymax],
                            "srs": "EPSG:4326"
                        },
                        "transparent": True
                    }
                })
        wms = f"verniquet_{version}"
        wms_cache = f"{wms}_cache"
        wms_source = f"{wms}_tms"
        file=dataverse_links[wms]
        layers.append({
            "name": wms,
            "title": f"Atlas du plan general de la ville de Paris [Exemplaire {version}]",
            "sources": [wms_cache]
        })
        caches.update({
            wms_cache: {
                "grids": ["webmercator"],
                "sources": [wms_source]
            }
        })
        sources.update({
            wms_source: {
                "type": "tile",
                "grid": "webmercator",
                "url": f"https://allmaps.xyz/%(z)s/%(x)s/%(y)s.png?url={file}",
                "coverage":{
                    "bbox": parisExtent.copy(),
                    "srs": "EPSG:4326"
                },
                "transparent": True
            }
        })
    def create_entries_nofile(wms, title, date, url, sheets, sheet_url, diff, extents):
        wms_cache = f"{wms}_cache"
        wms_source = f"{wms}_tms"
        layers.append({
            "name": wms,
            "title": f"{title}. {date}",
            "sources": [wms_cache]
        })
        caches.update({
            wms_cache: {
                "grids": ["webmercator"],
                "sources": [wms_source]
            }
        })
        sources.update({
            wms_source: {
                "type": "tile",
                "grid": "webmercator",
                "url": f"https://allmaps.xyz/%(z)s/%(x)s/%(y)s.png?url={url}",
                "coverage":{
                    "bbox": parisExtent.copy(),
                    "srs": "EPSG:4326"
                },
                "transparent": True
            }
        })
        if sheets:
            for sheet in sheets:
                wms_sheet_cache = f"{wms}_{sheet:02d}_cache"
                wms_sheet_source = f"{wms}_{sheet:02d}_tms"
                layers.append({
                    "name": f"{wms}_{sheet:02d}",
                    "title": f"{title}. {date}. Feuille {sheet}",
                    "sources": [wms_sheet_cache]
                })
                caches.update({
                    wms_sheet_cache: {
                        "grids": ["webmercator"],
                        "sources": [wms_sheet_source]
                    }
                })
                extent = extents[str(sheet)]
                xmin,ymin,xmax,ymax=float(extent["westBoundLongitude"]),float(extent["southBoundLatitude"]),float(extent["eastBoundLongitude"]),float(extent["northBoundLatitude"])
                sources.update({
                    wms_sheet_source: {
                        "type": "tile",
                        "grid": "webmercator",
                        "url": f"https://allmaps.xyz/%(z)s/%(x)s/%(y)s.png?url={sheet_url}{(sheet+diff):02d}.json&transformation.type=thinPlateSpline",
                        "coverage":{
                            "bbox": [xmin,ymin,xmax,ymax],
                            "srs": "EPSG:4326"
                        },
                        "transparent": True
                    }
                })
    create_entries("bnf",1)
    create_entries("stanford",1)
    # Adding the Atlas Municipal atlases
    with open("../geonetwork-resources/atlas_municipal/atlas_municipal_entents.json", "r") as extent_file:
        atlas_municipal_extents = json.load(extent_file)
    with open("../geonetwork-resources/jacoubet/jacoubet_extents.json", "r") as extent_file:
        jacoubet_extents = json.load(extent_file)
    create_entries_nofile("atlas_municipal_1878","Atlas municipal des vingt arrondissements de la ville de Paris [Exemplaire Ville de Paris/BHdV]","1878",
                          "https://github.com/soduco/allmaps_annotations/raw/main/output/bhdv_atlas_municipal_1878/annotation_bhdv_atlas_municipal_1878.&transformation.type=thinPlateSpline",list(range(1,17)),
                          "https://github.com/soduco/allmaps_annotations/raw/main/output/bhdv_atlas_municipal_1878/BhdV_PL_ATL20Ardt_1878_00",1,atlas_municipal_extents)
    create_entries_nofile("atlas_municipal_1886","Atlas municipal des vingt arrondissements de la ville de Paris [Exemplaire Ville de Paris/BHdV]","1886",
                          "https://github.com/soduco/allmaps_annotations/raw/main/output/bhdv_atlas_municipal_1886/annotation_bhdv_atlas_municipal_1886.json&transformation.type=thinPlateSpline",list(range(1,17)),
                          "https://github.com/soduco/allmaps_annotations/raw/main/output/bhdv_atlas_municipal_1886/BhdV_PL_ATL20Ardt_1886_00",1,atlas_municipal_extents)
    create_entries_nofile("atlas_municipal_1887","Atlas municipal des vingt arrondissements de la ville de Paris [Exemplaire Ville de Paris/BHdV]","1887",
                          "https://github.com/soduco/allmaps_annotations/raw/main/output/bhdv_atlas_municipal_1887/annotation_bhdv_atlas_municipal_1887.json&transformation.type=thinPlateSpline",list(range(1,17)),
                          "https://github.com/soduco/allmaps_annotations/raw/main/output/bhdv_atlas_municipal_1887/BhdV_PL_ATL20Ardt_1887_00",1,atlas_municipal_extents)
    create_entries_nofile("atlas_municipal_1888","Atlas municipal des vingt arrondissements de la ville de Paris [Exemplaire Ville de Paris/BHdV]","1888",
                          "https://github.com/soduco/allmaps_annotations/raw/main/output/bhdv_atlas_municipal_1888/annotation_bhdv_atlas_municipal_1888.json&transformation.type=thinPlateSpline",list(range(1,17)),
                          "https://github.com/soduco/allmaps_annotations/raw/main/output/bhdv_atlas_municipal_1888/BHdV_PL_ATL20Ardt_1888_00",1,atlas_municipal_extents)
    create_entries_nofile("atlas_municipal_1900","Atlas municipal des vingt arrondissements de la ville de Paris [Exemplaire Ville de Paris/BHdV]","1900",
                          "https://github.com/soduco/allmaps_annotations/raw/main/output/bhdv_atlas_municipal_1900/annotation_bhdv_atlas_municipal_1900.json&transformation.type=thinPlateSpline",list(range(1,17)),
                          "https://github.com/soduco/allmaps_annotations/raw/main/output/bhdv_atlas_municipal_1900/BHdV_PL_ATL20Ardt_1900_00",1,atlas_municipal_extents)
    create_entries_nofile("atlas_municipal_1925","Atlas municipal des vingt arrondissements de la ville de Paris [Exemplaire Ville de Paris/BHdV]","1925-1926",
                          "https://github.com/soduco/allmaps_annotations/raw/main/output/bhdv_atlas_municipal_1925/annotation_bhdv_atlas_municipal_1925.json&transformation.type=thinPlateSpline",list(range(1,17)),
                          "https://github.com/soduco/allmaps_annotations/raw/main/output/bhdv_atlas_municipal_1925/BHdV_PL_ATL20Ardt_1926_00",3,atlas_municipal_extents)
    create_entries_nofile("atlas_municipal_1937","Atlas municipal des vingt arrondissements de la ville de Paris [Exemplaire Ville de Paris/BHdV]","1929-1936",
                          "https://github.com/soduco/allmaps_annotations/raw/main/output/bhdv_atlas_municipal_1937/annotation_bhdv_atlas_municipal_1937.json&transformation.type=thinPlateSpline",list(range(1,17)),
                          "https://github.com/soduco/allmaps_annotations/raw/main/output/bhdv_atlas_municipal_1937/BHdV_PL_ATL20Ardt_1937_00",0,atlas_municipal_extents)
    create_entries_nofile("bhvp_jacoubet","Atlas général de la ville, des faubourgs et des monuments parisiens de Jacoubet [Exemplaire Ville de Paris/BHVP]","1825-1836",
                          "https://github.com/soduco/allmaps_annotations/raw/main/output/bhvp_jacoubet/annotation_bhvp_jacoubet.json&transformation.type=thinPlateSpline",list(range(3,8))+list(range(10,53)),
                          "https://github.com/soduco/allmaps_annotations/raw/main/output/bhvp_jacoubet/bhvp_jacoubet_",0,jacoubet_extents)
    create_entries_nofile("SHDGR__GR_6_M_J10_C_1188","Parcellaire de Paris des ingénieurs géographes, environ 1820-1833 [Exemplaire SHD]","1820-1833",
                          "https://github.com/soduco/allmaps_annotations/raw/main/output/SHDGR__GR_6_M_J10_C_1188/SHDGR__GR_6_M_J10_C_1188.json&transformation.type=thinPlateSpline", None, None, 0, parisExtent)
    create_entries_nofile("atlas_general_paris","Atlas général de Paris (CP/F/31/1 et 2), environ 1807-1821 [Exemplaire AN FRAN_IR_057290]","1807-1821",
                          "https://github.com/soduco/allmaps_annotations/raw/main/output/Atlas_general_de_Paris/Atlas_general_de_Paris.json&transformation.type=thinPlateSpline", None, None, 0, parisExtent)
    config = {
        "services":{
            "tms":{
                "use_grid_names": True,
                # origin for /tiles service
                "origin": 'nw'
            },
            "kml":{
                "use_grid_names": True
            },
            "wmts":{},
            "wms":{
                "md":{
                "title": "MapProxy WMS Proxy",
                "abstract": "This is a minimal MapProxy example."
                }
            }
        },
        "layers": layers,
        "caches": caches,
        "sources": sources,
        "grids":{
            "webmercator":{
                "base": "GLOBAL_WEBMERCATOR"
            }
        },
        "globals":{}
    }
    with open('mapproxy.yaml', 'w') as file:
        yaml.dump(config, file, sort_keys=False)#, default_flow_style=False)
    logging.info("END")

if __name__ == "__main__":
    main()
