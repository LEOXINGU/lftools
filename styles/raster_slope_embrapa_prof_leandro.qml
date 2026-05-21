<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="Symbology" version="3.44.8-Solothurn">
  <pipe-data-defined-properties>
    <Option type="Map">
      <Option name="Embrapa-Brazil" type="QString" value="Prof_Leandro_Franca"/>
      <Option name="properties"/>
      <Option name="type" type="QString" value="collection"/>
    </Option>
  </pipe-data-defined-properties>
  <pipe>
    <provider>
      <resampling zoomedOutResamplingMethod="nearestNeighbour" maxOversampling="2" enabled="false" zoomedInResamplingMethod="nearestNeighbour"/>
    </provider>
    <rasterrenderer nodataColor="" alphaBand="-1" band="1" opacity="1" type="singlebandpseudocolor" classificationMax="900" classificationMin="3">
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
        <colorrampshader minimumValue="3" labelPrecision="4" clip="0" maximumValue="500" colorRampType="DISCRETE" classificationMode="2">
          <colorramp name="[source]" type="gradient">
            <Option type="Map">
              <Option name="color1" type="QString" value="40,111,164,255,hsv:0.57125000000000004,0.75823605706874186,0.64432745860990315,1"/>
              <Option name="color2" type="QString" value="177,16,17,255,hsv:0.99808333333333332,0.912489509422446,0.69587243457694359,1"/>
              <Option name="direction" type="QString" value="ccw"/>
              <Option name="discrete" type="QString" value="0"/>
              <Option name="rampType" type="QString" value="gradient"/>
              <Option name="spec" type="QString" value="rgb"/>
              <Option name="stops" type="QString" value="0.0100604;162,249,208,255,hsv:0.4216388888888889,0.35051499198901348,0.975570305943389,1;rgb;ccw:0.0342052;76,198,77,255,hsv:0.33477777777777779,0.61855497062638287,0.77834744792858779,1;rgb;ccw:0.084507;241,235,122,255,hsv:0.15836111111111112,0.49485008010986498,0.94633401998931865,1;rgb;ccw:0.144869;255,174,93,255,hsv:0.08330555555555555,0.63402761882963299,1,1;rgb;ccw"/>
            </Option>
          </colorramp>
          <item label="0% – 3% (Plano)" color="#286fa4" alpha="255" value="3"/>
          <item label="3% - 8% (Suave ondulado)" color="#a2f9d0" alpha="255" value="8"/>
          <item label="8% - 20% (Ondulado)" color="#4cc64d" alpha="255" value="20"/>
          <item label="20% - 45% (Forte ondulado)" color="#f1eb7a" alpha="255" value="45"/>
          <item label="45% - 75% (Montanhoso)" color="#ffae5d" alpha="255" value="75"/>
          <item label="> 75% (Escarpado)" color="#b11011" alpha="255" value="inf"/>
          <rampLegendSettings minimumLabel="" prefix="" suffix="" direction="0" maximumLabel="" orientation="2" useContinuousLegend="1">
            <numericFormat id="basic">
              <Option type="Map">
                <Option name="decimal_separator" type="invalid"/>
                <Option name="decimals" type="int" value="6"/>
                <Option name="rounding_type" type="int" value="0"/>
                <Option name="show_plus" type="bool" value="false"/>
                <Option name="show_thousand_separator" type="bool" value="true"/>
                <Option name="show_trailing_zeros" type="bool" value="false"/>
                <Option name="thousand_separator" type="invalid"/>
              </Option>
            </numericFormat>
          </rampLegendSettings>
        </colorrampshader>
      </rastershader>
    </rasterrenderer>
    <brightnesscontrast brightness="0" gamma="1" contrast="0"/>
    <huesaturation colorizeStrength="100" invertColors="0" colorizeBlue="128" colorizeRed="255" colorizeGreen="128" colorizeOn="0" grayscaleMode="0" saturation="0"/>
    <rasterresampler maxOversampling="2"/>
    <resamplingStage>resamplingFilter</resamplingStage>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
