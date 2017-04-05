#!/usr/bin/python
#Parse metadata in dicom files (directories with series) into json OHIF Standalone Viewer format
import dicom
import os
import json

def parse_dicom_directory(directory):
    imagefiles = os.listdir(directory)
    firstimage = dicom.read_file(os.path.join(directory, imagefiles[0]))
    #urlprefix = "dicomweb://localhost:3000/" + directory + "/"
    urlprefix = "dicomweb://104.198.43.42/" + directory + "/"

    imageseries = firstimage.SeriesInstanceUID
    rows = firstimage.Rows
    columns = firstimage.Columns

    instances = []

    for imagefile in imagefiles:
        image = dicom.read_file(os.path.join(directory, imagefile))
        #check images are part of same series and same dimensions
        assert imageseries == image.SeriesInstanceUID
        assert rows == image.Rows
        assert columns == image.Columns
        instances.append({
            "sopInstanceUid": image.SOPInstanceUID,
            "columns": image.Rows,
            "rows": image.Columns,
            "url": urlprefix + imagefile,
            "instanceNumber": image.InstanceNumber
        })

    instances.sort(key=lambda instance: instance["instanceNumber"])

    series = {
        "seriesInstanceUid": firstimage.SeriesInstanceUID,
        "seriesDescription": firstimage.SeriesDescription,
        "instances": instances
    }

    study = {
        "studyInstanceUid": firstimage.StudyInstanceUID,
        "patientName": firstimage.PatientName,
        "seriesList": [series]
    }

    rootobject = {
        "transactionId": "kaggleData",
        "studies": [study]
    }

    with open(directory + ".json", "w") as output:
        output.write(json.dumps(rootobject, sort_keys=True, indent=2, separators=(',', ': ')))


for d in os.listdir("."):
    if os.path.isdir(d):
        parse_dicom_directory(d)
