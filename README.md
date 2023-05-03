# Geonetwork Python client

This package helps you create XML files for the Geonetwork metadata catalog and handle its API.
It's currently in alpha release.

## Commands

Here are the available commands:


```bash
    soduco_geonetwork_cli parse
```
Parse a yaml file and create xml files accordingly

```bash
    soduco_geonetwork_cli upload
```
Upload xml files listed in a csv file

```bash
    soduco_geonetwork_cli delete
```
Delete records on geonetwork from a uuid list in a csv file
```bash
    soduco_geonetwork_cli update
```
Update records on Geonetwork
```bash
    soduco_geonetwork_cli update-postponed-values
```
Update records on Geonetwork based on a csv file containing postponed values at record creation (like links beetween records)