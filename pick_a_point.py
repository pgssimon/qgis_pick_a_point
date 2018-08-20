# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from PyQt5.QtCore import QVariant, QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsFields,
                       QgsField,
                       QgsWkbTypes,
                       QgsCoordinateReferenceSystem,
                       QgsGeometry,
                       QgsFeature,
                       QgsPoint,
                       QgsPointXY,
                       QgsProject,
                       QgsProcessingParameterPoint,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)
import processing


class ExampleProcessingAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    START_POINT = 'START_POINT'
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ExampleProcessingAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'pickpoint'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Pick point on map')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('Custom scripts')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'customscripts'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Pick a point on the map canvas and return as a layer")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        self.addParameter(
            QgsProcessingParameterPoint(
                self.START_POINT,
                self.tr('Pick a point on the map')
            )
        )

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output layer')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        startPoint = self.parameterAsPoint(
            parameters,
            self.START_POINT,
            context,
            #crs = QgsCoordinateReferenceSystem("EPSG:2193")
            crs = QgsCoordinateReferenceSystem(QgsProject().crs())
        )

        # If source was not found, throw an exception to indicate that the algorithm
        # encountered a fatal error. The exception text can be any string, but in this
        # case we use the pre-built invalidSourceError method to return a standard
        # helper text for when a source cannot be evaluated
        if startPoint is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.START_POINT))

        fields = QgsFields()
        fields.append(QgsField('type', QVariant.String, '', 254, 0))
        fields.append(QgsField('coordinates', QVariant.String, '', 254, 0))

        feat = QgsFeature()
        feat.setFields(fields)

        (point_sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields,
            QgsWkbTypes.MultiPoint,
            #source.wkbType(),
            #QgsCoordinateReferenceSystem("EPSG:2193")
            crs = QgsCoordinateReferenceSystem(QgsProject().crs())
        )

        results = {}

        # If sink was not created, throw an exception to indicate that the algorithm
        # encountered a fatal error. The exception text can be any string, but in this
        # case we use the pre-built invalidSinkError method to return a standard
        # helper text for when a sink cannot be evaluated
        if point_sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        if point_sink is not None:
            results[self.OUTPUT] = dest_id
            #geomPoints = QgsGeometry.fromMultiPointXY(points)
            geomPoints = QgsGeometry.fromMultiPointXY([startPoint])
            feat.setGeometry(geomPoints)
            feat['type'] = 'point'
            feat['coordinates'] = startPoint.toString()
            point_sink.addFeature(feat, QgsFeatureSink.FastInsert)



        # Return the results of the algorithm. In this case our only result is
        # the feature sink which contains the processed features, but some
        # algorithms may return multiple feature sinks, calculated numeric
        # statistics, etc. These should all be included in the returned
        # dictionary, with keys matching the feature corresponding parameter
        # or output names.

        #return {self.OUTPUT: dest_id}
        return results
