<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.44.8-Solothurn" styleCategories="Symbology">
  <pipe-data-defined-properties>
    <Option type="Map">
      <Option value="" name="name" type="QString"/>
      <Option name="properties"/>
      <Option value="collection" name="type" type="QString"/>
    </Option>
  </pipe-data-defined-properties>
  <pipe>
    <provider>
      <resampling zoomedInResamplingMethod="nearestNeighbour" zoomedOutResamplingMethod="nearestNeighbour" maxOversampling="2" enabled="false"/>
    </provider>
    <rasterrenderer band="1" classificationMin="0" nodataColor="" alphaBand="-1" classificationMax="60" opacity="1" type="singlebandpseudocolor">
      <rasterTransparency/>
      <minMaxOrigin>
        <limits>None</limits>
        <extent>WholeRaster</extent>
        <statAccuracy>Estimated</statAccuracy>
        <cumulativeCutLower>0.02</cumulativeCutLower>
        <cumulativeCutUpper>0.98</cumulativeCutUpper>
        <stdDevFactor>2</stdDevFactor>
      </minMaxOrigin>
      <rastershader>
        <colorrampshader labelPrecision="4" clip="0" classificationMode="2" minimumValue="0" maximumValue="60" colorRampType="DISCRETE">
          <colorramp name="[source]" type="gradient">
            <Option type="Map">
              <Option value="125,195,197,255,hsv:0.50411111111111107,0.36597238117036696,0.77318989852750442,1" name="color1" type="QString"/>
              <Option value="127,0,0,255,rgb:0.4980392,0,0,1" name="color2" type="QString"/>
              <Option value="ccw" name="direction" type="QString"/>
              <Option value="0" name="discrete" type="QString"/>
              <Option value="gradient" name="rampType" type="QString"/>
              <Option value="rgb" name="spec" type="QString"/>
              <Option value="0.05;125,195,197,255,hsv:0.50411111111111107,0.36597238117036696,0.77318989852750442,1;rgb;ccw:0.133333;166,217,106,255,rgb:0.6509804,0.8509804,0.4156863,1;rgb;ccw:0.266667;255,255,191,255,rgb:1,1,0.7490196,1;rgb;ccw:0.5;253,174,97,255,rgb:0.9921569,0.6823529,0.3803922,1;rgb;ccw:1;244,109,67,255,rgb:0.9568627,0.427451,0.2627451,1;rgb;ccw" name="stops" type="QString"/>
            </Option>
          </colorramp>
          <item color="#7dc3c5" label="0% – 3% (Nearly level)" value="3" alpha="255"/>
          <item color="#a6d96a" label="3% – 8% (Gently sloping / Undulating)" value="8" alpha="255"/>
          <item color="#ffffbf" label="8% – 16% (Strongly sloping / Rolling)" value="16" alpha="255"/>
          <item color="#fdae61" label="16% – 30% (Moderately steep / Hilly)" value="30" alpha="255"/>
          <item color="#f46d43" label="30% – 60% (Steep)" value="60" alpha="255"/>
          <item color="#7f0000" label="> 45% (Very steep)" value="inf" alpha="255"/>
          <rampLegendSettings minimumLabel="" maximumLabel="" suffix="" prefix="" useContinuousLegend="1" direction="0" orientation="2">
            <numericFormat id="basic">
              <Option type="Map">
                <Option name="decimal_separator" type="invalid"/>
                <Option value="6" name="decimals" type="int"/>
                <Option value="0" name="rounding_type" type="int"/>
                <Option value="false" name="show_plus" type="bool"/>
                <Option value="true" name="show_thousand_separator" type="bool"/>
                <Option value="false" name="show_trailing_zeros" type="bool"/>
                <Option name="thousand_separator" type="invalid"/>
              </Option>
            </numericFormat>
          </rampLegendSettings>
        </colorrampshader>
      </rastershader>
    </rasterrenderer>
    <brightnesscontrast gamma="1" brightness="0" contrast="0"/>
    <huesaturation saturation="0" grayscaleMode="0" colorizeBlue="128" colorizeStrength="100" colorizeOn="0" colorizeGreen="128" invertColors="0" colorizeRed="255"/>
    <rasterresampler maxOversampling="2"/>
    <resamplingStage>resamplingFilter</resamplingStage>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
