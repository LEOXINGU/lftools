<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="Symbology" version="3.44.11-Solothurn">
  <pipe-data-defined-properties>
    <Option type="Map">
      <Option value="" type="QString" name="name"/>
      <Option name="properties"/>
      <Option value="collection" type="QString" name="type"/>
    </Option>
  </pipe-data-defined-properties>
  <pipe>
    <provider>
      <resampling enabled="false" maxOversampling="2" zoomedInResamplingMethod="nearestNeighbour" zoomedOutResamplingMethod="nearestNeighbour"/>
    </provider>
    <rasterrenderer classificationMax="10000" type="singlebandpseudocolor" opacity="1" alphaBand="-1" classificationMin="1" band="1" nodataColor="">
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
        <colorrampshader clip="0" labelPrecision="4" minimumValue="1" maximumValue="10000" colorRampType="DISCRETE" classificationMode="2">
          <colorramp type="gradient" name="[source]">
            <Option type="Map">
              <Option value="215,25,28,255,rgb:0.8431373,0.0980392,0.1098039,1" type="QString" name="color1"/>
              <Option value="26,150,65,255,rgb:0.1019608,0.5882353,0.254902,1" type="QString" name="color2"/>
              <Option value="ccw" type="QString" name="direction"/>
              <Option value="0" type="QString" name="discrete"/>
              <Option value="gradient" type="QString" name="rampType"/>
              <Option value="rgb" type="QString" name="spec"/>
              <Option value="0.00040004;255,165,95,255,hsv:0.07269444444444445,0.6293736171511406,1,1;rgb;ccw:0.00090009;255,250,131,255,hsv:0.16016666666666668,0.48717479209582665,1,1;rgb;ccw:0.00240024;184,255,169,255,rgb:0.7219501,1,0.6625467,1;rgb;ccw" type="QString" name="stops"/>
            </Option>
          </colorramp>
          <item label="Very High" value="1" alpha="255" color="#d7191c"/>
          <item label="High" value="5" alpha="255" color="#ffa55f"/>
          <item label="Moderate" value="10" alpha="255" color="#fffa83"/>
          <item label="Low" value="25" alpha="255" color="#b8ffa9"/>
          <item label="Very Low" value="inf" alpha="255" color="#1a9641"/>
          <rampLegendSettings prefix="" orientation="2" maximumLabel="" useContinuousLegend="1" direction="0" suffix="" minimumLabel="">
            <numericFormat id="basic">
              <Option type="Map">
                <Option type="invalid" name="decimal_separator"/>
                <Option value="6" type="int" name="decimals"/>
                <Option value="0" type="int" name="rounding_type"/>
                <Option value="false" type="bool" name="show_plus"/>
                <Option value="true" type="bool" name="show_thousand_separator"/>
                <Option value="false" type="bool" name="show_trailing_zeros"/>
                <Option type="invalid" name="thousand_separator"/>
              </Option>
            </numericFormat>
          </rampLegendSettings>
        </colorrampshader>
      </rastershader>
    </rasterrenderer>
    <brightnesscontrast brightness="0" contrast="0" gamma="1"/>
    <huesaturation colorizeOn="0" colorizeBlue="128" colorizeRed="255" saturation="0" colorizeGreen="128" colorizeStrength="100" invertColors="0" grayscaleMode="0"/>
    <rasterresampler maxOversampling="2"/>
    <resamplingStage>resamplingFilter</resamplingStage>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
