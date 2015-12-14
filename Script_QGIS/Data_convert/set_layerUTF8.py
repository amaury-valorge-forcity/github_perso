#!/usr/bin/env Python
# -*- coding: utf-8 -*-

for layer in QgsMapLayerRegistry.instance().mapLayers().values():
    layer.setProviderEncoding(u'UTF-8')
    layer.dataProvider().setEncoding(u'UTF-8')