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
    parisExtent = [2.2789487344052968,48.8244731921314568,2.4080435114903960,48.8904078536729116]
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
    def create_entry(wms, date, url):
        wms_cache = f"{wms}_cache"
        wms_source = f"{wms}_tms"
        layers.append({
            "name": wms,
            "title": f"Atlas municipal des vingt arrondissements de la ville de Paris. {date}]",
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
    create_entries("bnf",1)
    create_entries("stanford",1)
    # Adding the Atlas Municipal atlases
    create_entry("atlas_municipal_1878","1878","https://github.com/soduco/allmaps_annotations/raw/main/output/bhdv_atlas_municipal_1878/annotation_bhdv_atlas_municipal_1878.json")
    create_entry("atlas_municipal_1886","1886","https://github.com/soduco/allmaps_annotations/raw/main/output/bhdv_atlas_municipal_1886/annotation_bhdv_atlas_municipal_1886.json")
    create_entry("atlas_municipal_1887","1887","https://github.com/soduco/allmaps_annotations/raw/main/output/bhdv_atlas_municipal_1887/annotation_bhdv_atlas_municipal_1887.json")
    create_entry("atlas_municipal_1888","1888","https://github.com/soduco/allmaps_annotations/raw/main/output/bhdv_atlas_municipal_1888/annotation_bhdv_atlas_municipal_1888.json")
    create_entry("atlas_municipal_1900","1900","https://github.com/soduco/allmaps_annotations/raw/main/output/bhdv_atlas_municipal_1900/annotation_bhdv_atlas_municipal_1900.json")
    create_entry("atlas_municipal_1925","1925","https://github.com/soduco/allmaps_annotations/raw/main/output/bhdv_atlas_municipal_1925/annotation_bhdv_atlas_municipal_1925.json")
    create_entry("atlas_municipal_1937","1929-1936","https://github.com/soduco/allmaps_annotations/raw/main/output/bhdv_atlas_municipal_1937/annotation_bhdv_atlas_municipal_1937.json")
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
